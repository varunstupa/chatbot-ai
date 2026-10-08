"""Tenant isolation, screen routing and auth for the admin-app chat."""

from __future__ import annotations

import hashlib
import math
import pathlib
import re
import time

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencies import get_rag_pipeline
from app.config.settings import get_settings
from app.main import app
from app.knowledge import registry as knowledge_registry
from app.knowledge import service as knowledge_store
from app.knowledge.parser import GuideError, parse_guide
from app.services import app_chat
from app.services.auth import CallerScope

JWT_SECRET = "unit-test-secret-that-is-long-enough-0123456789"
SERVICE_KEY = "unit-test-service-key"

DETAILS = """---
doc_id: tms.event-settings.create-event
title: Event Details page
routes: ["tms/event-settings/create-event/:event_id"]
aliases: ["event details", "details step"]
tenants: all
suggested_questions: ["How do I create an event?"]
---
# Event Details page

Overview of the event details page where organisers create an event.

## Event Details page: dates

The End Date is locked until a Start Date is chosen. Changing the start date clears the end date.

## Event Details page: thumbnail

The thumbnail must be exactly 379 x 200 pixels and smaller than 1 MB.
"""

REGISTRATION = """---
doc_id: tms.event-settings.registration
title: Registration settings page
routes: ["tms/event-settings/registration/:event_id"]
aliases: ["registration settings"]
tenants: all
exclude_tenants: [switz]
---
## Registration settings page: deadline

Set the registration deadline and the entry fee for each category on the registration settings page.
"""

ETTU_PRIVATE = """---
doc_id: ettu.private-policy
title: ETTU internal policy
tenants: [ettu]
---
## ETTU internal policy: secret

The ETTU confidential wildcard quota is forty two zebra players per federation.
"""

ETTU_OVERLAY = """---
doc_id: tms.event-settings.create-event.ettu
title: Event Details page
routes: ["tms/event-settings/create-event/:event_id"]
tenants: [ettu]
overrides: tms.event-settings.create-event
---
## Event Details page: dates for ETTU

For ETTU the End Date is locked until a Start Date is chosen and must fall inside the ETTU season window.
"""


class FakeEmbeddings:
    """Deterministic bag-of-words vectors so tests need no model download."""

    dim = 256

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def __init__(self) -> None:
        self.documents_embedded = 0

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.documents_embedded += len(texts)
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


class FakePipeline:
    """Stands in for the LLM: returns the retrieved context as the answer."""

    def __init__(self) -> None:
        self.session_ids: list[str] = []

    async def answer(self, question, session_id, corpus="merged", *, prompt_template=None,
                     retriever=None, no_answer_text=None):
        self.session_ids.append(session_id)
        context, sources = retriever(question)
        return (context if sources else no_answer_text), sources

    async def stream(self, question, session_id, corpus="merged", *, prompt_template=None,
                     retriever=None, no_answer_text=None):
        self.session_ids.append(session_id)
        yield {"type": "session", "session_id": session_id}
        context, sources = retriever(question)
        yield {"type": "sources", "chunks": sources}
        yield {"type": "token", "text": context if sources else no_answer_text}
        yield {"type": "done"}


@pytest.fixture()
def kb(tmp_path, monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s.app_chat, "persist_directory", str(tmp_path / "kb"))
    monkeypatch.setattr(s.app_chat, "max_distance", 1.5)
    monkeypatch.setattr(s.app_chat, "screen_max_distance", 1.5)
    monkeypatch.setattr(s, "app_chat_jwt_secret", SecretStr(JWT_SECRET))
    # Test tokens are HS256 with these claims, whatever the deployed config says.
    monkeypatch.setattr(s.auth, "jwt_algorithms", ["HS256"])
    monkeypatch.setattr(s.auth, "mode", "jwt")
    monkeypatch.setattr(s.auth, "user_claims", ["user_id"])
    monkeypatch.setattr(s.auth, "allowed_tenants", [])
    monkeypatch.setattr(s, "app_chat_jwt_public_key", None)
    monkeypatch.setattr(s, "app_chat_allow_unverified_dev_tokens", False)
    monkeypatch.setattr(s, "knowledge_service_key", SecretStr(SERVICE_KEY))
    embeddings = FakeEmbeddings()
    monkeypatch.setattr(knowledge_store, "get_embeddings", lambda: embeddings)
    knowledge_store.reset_for_tests()
    for guide in (DETAILS, REGISTRATION, ETTU_PRIVATE, ETTU_OVERLAY):
        knowledge_store.ingest_guide(guide)
    yield embeddings
    knowledge_store.reset_for_tests()


@pytest.fixture()
def client(kb):
    pipeline = FakePipeline()
    app.dependency_overrides[get_rag_pipeline] = lambda: pipeline
    with TestClient(app) as c:
        c.pipeline = pipeline  # type: ignore[attr-defined]
        yield c
    app.dependency_overrides.clear()


def token(tenant: str | None = "denmark", *, secret: str = JWT_SECRET, exp_in: int = 600,
          user: str = "u1") -> str:
    claims: dict = {"user_id": user, "exp": int(time.time()) + exp_in}
    if tenant is not None:
        claims["tenant"] = tenant
    return jwt.encode(claims, secret, algorithm="HS256")


def auth(tenant: str = "denmark", **kw) -> dict:
    return {"auth": f"Bearer {token(tenant, **kw)}", "tenant": tenant}


DENMARK = CallerScope(tenant="denmark", user_id="u1")
ETTU = CallerScope(tenant="ettu", user_id="u2")
SWITZ = CallerScope(tenant="switz", user_id="u3")
SECRET_QUESTION = "ETTU confidential wildcard quota zebra players per federation"
DETAILS_ROUTE = "tms/event-settings/create-event/:event_id"


# ---------- front matter ----------


def test_guide_without_tenants_is_rejected():
    with pytest.raises(GuideError, match="tenants"):
        knowledge_store.parse_guide("---\ndoc_id: a.b\ntitle: T\n---\nbody")


def test_guide_without_front_matter_is_rejected():
    with pytest.raises(GuideError):
        knowledge_store.parse_guide("# just markdown")


def test_exclude_requires_all():
    with pytest.raises(GuideError):
        knowledge_store.parse_guide(
            "---\ndoc_id: a.b\ntitle: T\ntenants: [ettu]\nexclude_tenants: [switz]\n---\nbody"
        )


# ---------- storage isolation ----------


def test_other_tenant_never_gets_private_chunks(kb):
    hits = knowledge_store.search(DENMARK, SECRET_QUESTION)
    assert all(h.doc_id != "ettu.private-policy" for h in hits)
    assert all("zebra" not in h.content for h in hits)
    assert all(not h.tenant_specific for h in hits)


def test_owner_tenant_gets_private_chunks(kb):
    hits = knowledge_store.search(ETTU, SECRET_QUESTION)
    assert hits and hits[0].doc_id == "ettu.private-policy"


def test_private_doc_id_cannot_be_requested_by_other_tenant(kb):
    assert knowledge_store.search(DENMARK, SECRET_QUESTION, doc_ids=["ettu.private-policy"]) == []
    assert knowledge_store.overview(DENMARK, ["ettu.private-policy"]) == []


def test_private_guide_not_listed_for_other_tenant(kb):
    assert "ettu.private-policy" not in knowledge_store.visible_guides(DENMARK)
    assert "ettu.private-policy" in knowledge_store.visible_guides(ETTU)
    assert knowledge_store.guides_named_in(DENMARK, "tell me the ettu internal policy") == []


def test_exclude_tenants_hides_common_guide(kb):
    assert "tms.event-settings.registration" in knowledge_store.visible_guides(DENMARK)
    assert "tms.event-settings.registration" not in knowledge_store.visible_guides(SWITZ)
    hits = knowledge_store.search(SWITZ, "registration deadline entry fee")
    assert all(h.doc_id != "tms.event-settings.registration" for h in hits)


def test_reingest_replaces_chunks(kb):
    before = knowledge_store.overview(DENMARK, ["tms.event-settings.create-event"], limit=50)
    knowledge_store.ingest_guide(DETAILS)
    after = knowledge_store.overview(DENMARK, ["tms.event-settings.create-event"], limit=50)
    assert len(before) == len(after)


def test_delete_guide(kb):
    assert knowledge_store.delete_guide("ettu.private-policy")
    assert knowledge_store.search(ETTU, SECRET_QUESTION, doc_ids=["ettu.private-policy"]) == []
    assert not knowledge_store.delete_guide("ettu.private-policy")


# ---------- screen routing ----------


def test_route_pattern_and_url_fallback(kb):
    assert knowledge_store.guides_for_screen(DENMARK, DETAILS_ROUTE) == [
        "tms.event-settings.create-event"
    ]
    assert knowledge_store.guides_for_screen(
        DENMARK, None, "/tms/event-settings/create-event/1358?x=1"
    ) == ["tms.event-settings.create-event"]
    assert knowledge_store.guides_for_screen(DENMARK, "tms/unknown/:id") == []


def test_overlay_listed_first_for_its_tenant(kb):
    assert knowledge_store.guides_for_screen(ETTU, DETAILS_ROUTE) == [
        "tms.event-settings.create-event.ettu",
        "tms.event-settings.create-event",
    ]


def test_current_screen_is_searched_first(kb):
    result = app_chat.retrieve(DENMARK, "why is the end date locked", DETAILS_ROUTE, None)
    assert result.mode == "screen"
    assert result.screen_title == "Event Details page"
    assert "Start Date" in result.hits[0].content


def test_overlay_chunk_outranks_base_for_its_tenant(kb):
    result = app_chat.retrieve(ETTU, "why is the end date locked", DETAILS_ROUTE, None)
    assert result.hits[0].doc_id == "tms.event-settings.create-event.ettu"
    denmark = app_chat.retrieve(DENMARK, "why is the end date locked", DETAILS_ROUTE, None)
    assert all("season window" not in h.content for h in denmark.hits)


def test_named_screen_wins_over_current(kb):
    result = app_chat.retrieve(
        DENMARK, "how do I set the deadline in registration settings", DETAILS_ROUTE, None
    )
    assert result.mode == "named"
    assert result.hits[0].doc_id == "tms.event-settings.registration"


def test_fallback_to_other_screen(kb):
    result = app_chat.retrieve(
        DENMARK,
        "thumbnail must be exactly 379 x 200 pixels",
        "tms/event-settings/registration/:event_id",
        None,
    )
    assert result.mode == "fallback"
    assert result.hits[0].title == "Event Details page"


def test_vague_question_gets_overview(kb, monkeypatch):
    monkeypatch.setattr(get_settings().app_chat, "max_distance", 0.01)
    monkeypatch.setattr(get_settings().app_chat, "screen_max_distance", 0.01)
    result = app_chat.retrieve(DENMARK, "what can I do on this page?", DETAILS_ROUTE, None)
    assert result.mode == "overview"
    assert result.hits[0].section == "Overview"


def test_unrelated_question_has_no_hits(kb, monkeypatch):
    monkeypatch.setattr(get_settings().app_chat, "max_distance", 0.01)
    monkeypatch.setattr(get_settings().app_chat, "screen_max_distance", 0.01)
    result = app_chat.retrieve(DENMARK, "quantum chromodynamics lagrangian", DETAILS_ROUTE, None)
    assert result.mode == "none" and result.hits == []


def test_sources_expose_no_paths_or_tenants(kb):
    result = app_chat.retrieve(ETTU, SECRET_QUESTION, None, None)
    for src in result.sources:
        assert set(src) == {"filename", "source", "chunk_index", "content"}
        assert "\\" not in src["filename"] and "/" not in src["filename"]


# ---------- HTTP: authentication ----------


def _ask(client, headers, question="why is the end date locked", **extra):
    body = {"question": question, "screen": {"route": DETAILS_ROUTE}, **extra}
    return client.post("/api/app-chat", json=body, headers={"accept": "application/json", **headers})


def test_no_token_is_401(client):
    assert _ask(client, {}).status_code == 401


def test_bad_signature_is_401(client):
    headers = {"auth": f"Bearer {token('denmark', secret='x' * 40)}"}
    assert _ask(client, headers).status_code == 401


def test_expired_token_is_401(client):
    headers = {"auth": f"Bearer {token('denmark', exp_in=-60)}"}
    assert _ask(client, headers).status_code == 401


def test_unsigned_token_is_401(client):
    unsigned = jwt.encode({"tenant": "ettu", "user_id": "u"}, key="", algorithm="none")
    assert _ask(client, {"auth": f"Bearer {unsigned}"}).status_code == 401


def test_token_without_tenant_is_403(client):
    headers = {"auth": f"Bearer {token(None)}", "tenant": "ettu"}
    assert _ask(client, headers).status_code == 403


def test_tenant_header_must_match_token(client):
    headers = {"auth": f"Bearer {token('denmark')}", "tenant": "ettu"}
    assert _ask(client, headers).status_code == 403


def test_tenant_in_body_is_ignored(client):
    r = _ask(client, auth("denmark"), question=SECRET_QUESTION, tenant="ettu")
    assert r.status_code == 200
    assert "zebra" not in r.text


def test_missing_jwt_key_fails_closed(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "app_chat_jwt_secret", None)
    assert _ask(client, auth("denmark")).status_code == 503


# ---------- HTTP: chat ----------


def test_chat_answers_from_current_screen(client):
    r = _ask(client, auth("denmark"))
    assert r.status_code == 200
    body = r.json()
    assert "Start Date" in body["answer"]
    assert body["chunks"][0]["filename"] == "Event Details page"


def test_chat_never_leaks_other_tenant(client):
    r = _ask(client, auth("denmark"), question=SECRET_QUESTION)
    assert "zebra" not in r.text
    owner = _ask(client, auth("ettu"), question=SECRET_QUESTION)
    assert "zebra" in owner.json()["answer"]


def test_history_key_is_scoped_by_tenant_and_user(client):
    sid = "shared-session-0001"
    a = _ask(client, auth("denmark"), session_id=sid)
    b = _ask(client, auth("ettu", user="u9"), session_id=sid)
    assert a.json()["session_id"] == sid and b.json()["session_id"] == sid
    keys = client.pipeline.session_ids
    assert keys[0] != keys[1]
    assert keys[0].startswith("denmark--") and keys[1].startswith("ettu--")


def test_stream_does_not_expose_scoped_session_key(client):
    r = client.post(
        "/api/app-chat/stream",
        json={"question": "why is the end date locked", "screen": {"route": DETAILS_ROUTE}},
        headers=auth("denmark"),
    )
    assert r.status_code == 200
    assert "denmark--" not in r.text
    assert '"type": "token"' in r.text and "Start Date" in r.text


def test_screen_endpoint(client):
    r = client.get("/api/knowledge/screen", params={"route": DETAILS_ROUTE}, headers=auth("denmark"))
    assert r.json() == {
        "documented": True,
        "title": "Event Details page",
        "suggested_questions": ["How do I create an event?"],
    }
    unknown = client.get("/api/knowledge/screen", params={"route": "x/y"}, headers=auth("denmark"))
    assert unknown.json()["documented"] is False
    assert client.get("/api/knowledge/screen").status_code == 401


# ---------- HTTP: ingest ----------


def test_guide_listing_requires_service_key(client):
    listed = client.get("/api/knowledge/documents", headers={"X-Service-Key": SERVICE_KEY})
    assert "ettu.private-policy" in listed.json()["documents"]
    assert client.get("/api/knowledge/documents").status_code == 401
    assert client.get("/api/knowledge/documents", headers=auth("ettu")).status_code == 401


def test_guides_cannot_be_written_over_http(client):
    files = {"file": ("guide.md", DETAILS.encode("utf-8"), "text/markdown")}
    headers = {"X-Service-Key": SERVICE_KEY}
    assert client.post("/api/knowledge/documents", files=files, headers=headers).status_code == 405
    gone = client.delete("/api/knowledge/documents/ettu.private-policy", headers=headers)
    assert gone.status_code in (404, 405)


def test_upload_requires_service_key(client):
    r = client.post("/upload", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 401


def test_service_key_unset_fails_closed(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "knowledge_service_key", None)
    listed = client.get("/api/knowledge/documents", headers={"X-Service-Key": SERVICE_KEY})
    assert listed.status_code == 503


# ---------- HTTP: decode-only mode (tenant and expiry checked, no signature) ----------


@pytest.fixture()
def decode_only(client, monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "app_chat_jwt_secret", None)
    monkeypatch.setattr(s, "app_chat_allow_unverified_dev_tokens", True)
    monkeypatch.setattr(s.auth, "allowed_tenants", ["staging"])
    return client


def _foreign_token(claims: dict) -> str:
    """A token signed with a key this service does not know, like a real login token."""
    return jwt.encode(claims, "some-other-services-key-0123456789abcdef", algorithm="HS256")


def test_decode_only_accepts_valid_staging_token(decode_only):
    t = _foreign_token({"tenant": "staging", "user_role_id": 9, "exp": int(time.time()) + 600})
    r = _ask(decode_only, {"auth": f"Bearer {t}", "tenant": "staging"})
    assert r.status_code == 200


def test_decode_only_rejects_expired_token(decode_only):
    t = _foreign_token({"tenant": "staging", "exp": int(time.time()) - 60})
    assert _ask(decode_only, {"auth": f"Bearer {t}"}).status_code == 401


def test_decode_only_rejects_token_without_expiry(decode_only):
    t = _foreign_token({"tenant": "staging"})
    assert _ask(decode_only, {"auth": f"Bearer {t}"}).status_code == 401


def test_decode_only_rejects_token_without_tenant(decode_only):
    t = _foreign_token({"user_role_id": 9, "exp": int(time.time()) + 600})
    assert _ask(decode_only, {"auth": f"Bearer {t}", "tenant": "staging"}).status_code == 403


def test_decode_only_rejects_other_tenant(decode_only):
    t = _foreign_token({"tenant": "ettu", "exp": int(time.time()) + 600})
    assert _ask(decode_only, {"auth": f"Bearer {t}", "tenant": "ettu"}).status_code == 403


def test_decode_only_rejects_header_tenant_mismatch(decode_only):
    t = _foreign_token({"tenant": "staging", "exp": int(time.time()) + 600})
    assert _ask(decode_only, {"auth": f"Bearer {t}", "tenant": "ettu"}).status_code == 403


def test_decode_only_rejects_garbage_token(decode_only):
    assert _ask(decode_only, {"auth": "Bearer not-a-jwt"}).status_code == 401


# ---------- single collection, document-level access ----------


ROLE_GUIDE = """---
doc_id: tms.admin-only
title: Admin tools page
routes: ["tms/admin-tools"]
tenants: all
roles: [admin]
---
## Admin tools page: purge

The purge button deletes archived seasons permanently from the admin tools page.
"""


def _ettu_private(tenants: str, body_word: str = "zebra") -> str:
    return ETTU_PRIVATE.replace("tenants: [ettu]", f"tenants: {tenants}").replace("zebra", body_word)


def test_single_collection_and_content_only_metadata(kb):
    index = knowledge_store._index()
    assert index.collection_names() == ["knowledge_chunks"]
    got = index._collection.get(include=["metadatas"])
    allowed_keys = {"chunk_id", "doc_id", "title", "section", "chunk_index", "route"}
    assert got["metadatas"]
    for metadata in got["metadatas"]:
        assert set(metadata) <= allowed_keys
        assert "tenant" not in metadata


def test_access_change_updates_registry_without_reembedding(kb):
    embeddings = kb
    embeddings.documents_embedded = 0
    result = knowledge_store.ingest_guide(_ettu_private("[ettu, denmark]"))
    assert result["re_embedded"] is False
    assert embeddings.documents_embedded == 0
    assert knowledge_store.search(DENMARK, SECRET_QUESTION)[0].doc_id == "ettu.private-policy"

    knowledge_store.ingest_guide(_ettu_private("[ettu]"))
    assert embeddings.documents_embedded == 0
    assert all(h.doc_id != "ettu.private-policy" for h in knowledge_store.search(DENMARK, SECRET_QUESTION))


def test_unchanged_guide_is_not_reembedded(kb):
    embeddings = kb
    embeddings.documents_embedded = 0
    assert knowledge_store.ingest_guide(DETAILS)["re_embedded"] is False
    assert embeddings.documents_embedded == 0


def test_content_change_reembeds_and_replaces_old_chunks(kb):
    embeddings = kb
    embeddings.documents_embedded = 0
    result = knowledge_store.ingest_guide(_ettu_private("[ettu]", body_word="giraffe"))
    assert result["re_embedded"] is True
    assert embeddings.documents_embedded == result["chunks_indexed"]
    texts = [h.content for h in knowledge_store.overview(ETTU, ["ettu.private-policy"], limit=50)]
    assert any("giraffe" in t for t in texts)
    assert all("zebra" not in t for t in texts)


def test_route_change_without_reembedding(kb):
    embeddings = kb
    embeddings.documents_embedded = 0
    moved = DETAILS.replace("tms/event-settings/create-event/:event_id", "tms/event-settings/details/:event_id")
    assert knowledge_store.ingest_guide(moved)["re_embedded"] is False
    assert embeddings.documents_embedded == 0
    assert knowledge_store.guides_for_screen(DENMARK, "tms/event-settings/details/:event_id") == [
        "tms.event-settings.create-event"
    ]
    got = knowledge_store._index()._collection.get(
        where={"doc_id": "tms.event-settings.create-event"}, include=["metadatas"]
    )
    assert {m["route"] for m in got["metadatas"]} == {"tms/event-settings/details/:event_id"}


def test_role_restricted_guide(kb):
    knowledge_store.ingest_guide(ROLE_GUIDE)
    admin = CallerScope(tenant="denmark", user_id="u1", role="Admin")
    manager = CallerScope(tenant="denmark", user_id="u2", role="event_manager")
    no_role = CallerScope(tenant="denmark", user_id="u3", role=None)
    assert "tms.admin-only" in knowledge_store.visible_guides(admin)
    assert "tms.admin-only" not in knowledge_store.visible_guides(manager)
    assert "tms.admin-only" not in knowledge_store.visible_guides(no_role)
    question = "purge archived seasons permanently"
    assert knowledge_store.search(admin, question)[0].doc_id == "tms.admin-only"
    assert all(h.doc_id != "tms.admin-only" for h in knowledge_store.search(manager, question))


def test_invalid_role_is_rejected():
    with pytest.raises(GuideError, match="roles"):
        knowledge_store.ingest_guide(ROLE_GUIDE.replace("roles: [admin]", "roles: ['@@']"))


def test_malformed_registry_entry_denies_access():
    assert not knowledge_registry.entry_allows({}, DENMARK)
    assert not knowledge_registry.entry_allows({"access": {"tenants": "denmark"}}, DENMARK)


def test_guard_drops_chunk_of_document_not_allowed(kb):
    allowed = knowledge_store.visible_guides(DENMARK)
    hit = knowledge_store._checked_hit(
        "secret", {"doc_id": "ettu.private-policy"}, 0.1, DENMARK, allowed
    )
    assert hit is None


def test_registry_survives_new_service_instance(kb):
    knowledge_store.reset_for_tests()
    assert "ettu.private-policy" in knowledge_store.visible_guides(ETTU)
    assert "ettu.private-policy" not in knowledge_store.visible_guides(DENMARK)


def test_delete_revokes_and_removes_chunks(kb):
    assert knowledge_store.delete_guide("ettu.private-policy")
    assert knowledge_store._index().count("ettu.private-policy") == 0
    assert "ettu.private-policy" not in knowledge_store.list_guides_admin()


# ---------- loading the guides folder at startup ----------


from app.knowledge import guide_loader  # noqa: E402

BROKEN = "---\ndoc_id: a.b\ntitle: T\n---\nbody"


def _write(folder, name, text):
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_loader_loads_folder_and_skips_unchanged(kb, tmp_path):
    embeddings = kb
    folder = tmp_path / "guides"
    for name, text in (("a/details.md", DETAILS), ("b/registration.md", REGISTRATION),
                       ("c/private.md", ETTU_PRIVATE), ("c/overlay.md", ETTU_OVERLAY)):
        _write(folder, name, text)
    _write(folder, "README.md", "not a guide")
    embeddings.documents_embedded = 0
    report = guide_loader.load_guides(folder)
    assert report.errors == [] and report.removed == []
    assert {i["doc_id"] for i in report.loaded} == {
        "tms.event-settings.create-event", "tms.event-settings.registration",
        "ettu.private-policy", "tms.event-settings.create-event.ettu",
    }
    assert all(i["re_embedded"] is False for i in report.loaded)
    assert embeddings.documents_embedded == 0


def test_loader_removes_guide_whose_file_was_deleted(kb, tmp_path):
    folder = tmp_path / "guides"
    _write(folder, "details.md", DETAILS)
    _write(folder, "registration.md", REGISTRATION)
    report = guide_loader.load_guides(folder)
    assert report.errors == []
    assert set(report.removed) == {"ettu.private-policy", "tms.event-settings.create-event.ettu"}
    assert "ettu.private-policy" not in knowledge_store.list_guides_admin()


def test_loader_does_not_prune_when_a_guide_is_broken(kb, tmp_path):
    folder = tmp_path / "guides"
    _write(folder, "details.md", DETAILS)
    _write(folder, "broken.md", BROKEN)
    report = guide_loader.load_guides(folder)
    assert any("tenants" in e for e in report.errors)
    assert report.removed == []
    assert "ettu.private-policy" in knowledge_store.list_guides_admin()


def test_loader_rejects_duplicate_doc_id(kb, tmp_path):
    folder = tmp_path / "guides"
    _write(folder, "one.md", DETAILS)
    _write(folder, "two.md", DETAILS)
    report = guide_loader.load_guides(folder)
    assert any("also used by" in e for e in report.errors)
    assert report.removed == []


def test_loader_refuses_to_empty_store_from_empty_folder(kb, tmp_path):
    folder = tmp_path / "guides"
    folder.mkdir()
    report = guide_loader.load_guides(folder)
    assert report.errors and report.removed == []
    assert "tms.event-settings.registration" in knowledge_store.list_guides_admin()


def test_repo_guides_are_valid():
    """Every guide shipped in guides/ must pass validation."""
    root = pathlib.Path(__file__).resolve().parent.parent / "guides"
    files = [p for p in root.rglob("*.md") if p.name.lower() != "readme.md"]
    assert files
    ids = set()
    for path in files:
        meta, _ = parse_guide(path.read_text(encoding="utf-8"))
        assert meta.doc_id not in ids, f"duplicate doc_id in {path}"
        ids.add(meta.doc_id)


# ---------- identity signed by the API gateway (auth.mode: gateway) ----------


from app.services.auth import gateway_signature  # noqa: E402

GATEWAY_SECRET = "unit-test-gateway-secret"


@pytest.fixture()
def gateway_mode(client, monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s.auth, "mode", "gateway")
    monkeypatch.setattr(s, "chatbot_internal_secret", SecretStr(GATEWAY_SECRET))
    return client


def signed(tenant="denmark", user="42", role="admin", *, secret=GATEWAY_SECRET, age=0) -> dict:
    ts = str(int(time.time()) - age)
    return {
        "X-Chat-Tenant": tenant,
        "X-Chat-User": user,
        "X-Chat-Role": role,
        "X-Chat-Timestamp": ts,
        "X-Chat-Signature": gateway_signature(secret.encode(), ts, tenant, user, role),
    }


def _screen(client, headers):
    return client.get("/api/knowledge/screen", params={"route": DETAILS_ROUTE}, headers=headers)


def test_signature_matches_gateway_test_vector():
    # The same vector is asserted in the gateway (tests/test_chatbot_proxy.py).
    assert gateway_signature(b"vector-secret", "1700000000", "staging", "42", "admin") == (
        "bd83429af59943a67cd78b18249949a22e15855af0ef4a42bd906186072d3b6e"
    )


def test_gateway_mode_ignores_login_token(gateway_mode):
    assert _screen(gateway_mode, auth("denmark")).status_code == 401


def test_gateway_signature_with_wrong_secret_is_rejected(gateway_mode):
    assert _screen(gateway_mode, signed(secret="not-the-secret")).status_code == 401


def test_gateway_tenant_cannot_be_changed_after_signing(gateway_mode):
    headers = signed("denmark")
    headers["X-Chat-Tenant"] = "ettu"
    assert _screen(gateway_mode, headers).status_code == 401


def test_old_gateway_signature_is_rejected(gateway_mode):
    assert _screen(gateway_mode, signed(age=600)).status_code == 401


def test_gateway_scope_reaches_retrieval(gateway_mode):
    r = gateway_mode.post(
        "/api/app-chat",
        json={"question": SECRET_QUESTION, "screen": {"route": DETAILS_ROUTE}},
        headers=signed("denmark", user="7"),
    )
    assert r.status_code == 200
    assert "zebra" not in r.text
    assert gateway_mode.pipeline.session_ids[-1].startswith("denmark--7--")


def test_gateway_mode_without_secret_fails_closed(gateway_mode, monkeypatch):
    monkeypatch.setattr(get_settings(), "chatbot_internal_secret", None)
    assert _screen(gateway_mode, signed()).status_code == 503


def test_gateway_tenant_outside_allowed_list_is_refused(gateway_mode, monkeypatch):
    monkeypatch.setattr(get_settings().auth, "allowed_tenants", ["staging"])
    assert _screen(gateway_mode, signed("denmark")).status_code == 403
    assert _screen(gateway_mode, signed("staging")).status_code == 200
