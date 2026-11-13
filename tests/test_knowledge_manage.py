"""Documents uploaded from the admin panel: extraction, MongoDB records, access and the API.

MongoDB is mongomock (in memory); the search index is the temporary one of the
``kb`` fixture, so nothing touches a real database or the developer's index.
"""

from __future__ import annotations

import io
import time

import jwt
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.knowledge import documents, guide_loader, manage
from app.knowledge import service as knowledge_store
from app.knowledge.extract import extract
from app.knowledge.parser import GuideError
from app.main import app
from app.services.auth import CallerScope
from tests.test_app_chat_isolation import JWT_SECRET, kb  # noqa: F401  (kb is a fixture)


ADMIN = CallerScope(tenant="staging", user_id="9", role="Super Admin")
ETTU = CallerScope(tenant="ettu", user_id="u2")
DENMARK = CallerScope(tenant="denmark", user_id="u1")
SECRET = "Golden wombat refund rule: refunds are paid within nine working days"


def _pdf(*pages: str) -> bytes:
    """A small valid PDF with one line of text per page."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", None,
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for text in pages:
        stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        objects.append(f"<< /Length {len(stream)} >>\nstream\n{stream.decode()}\nendstream")
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                       f"/Resources << /Font << /F1 3 0 R >> >> /Contents {len(objects)} 0 R >>")
        kids.append(f"{len(objects)} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    out, offsets = io.BytesIO(), []
    out.write(b"%PDF-1.4\n")
    for n, body in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(f"{n} 0 obj\n{body}\nendobj\n".encode())
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    out.write("".join(f"{o:010d} 00000 n \n" for o in offsets).encode())
    out.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out.getvalue()


def _docx() -> bytes:
    import docx

    document = docx.Document()
    document.add_paragraph("Refund policy", style="Title")
    document.add_heading("When refunds are paid", level=1)
    document.add_paragraph(SECRET)
    document.add_heading("Steps", level=2)
    document.add_paragraph("Open the order", style="List Bullet")
    table = document.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text, table.rows[0].cells[1].text = "Plan", "Days"
    table.rows[1].cells[0].text, table.rows[1].cells[1].text = "Gold", "9"
    out = io.BytesIO()
    document.save(out)
    return out.getvalue()


@pytest.fixture()
def store(kb, monkeypatch):  # noqa: F811
    db = mongomock.MongoClient(tz_aware=True)["knowledge_test"]
    s = documents.KnowledgeDocuments(db)
    s.ensure_indexes()
    documents.use(s)
    monkeypatch.setattr(knowledge_store, "refresh_caches", lambda: None)
    monkeypatch.setattr(get_settings().knowledge_manage, "allowed_tenants", [])
    yield s
    documents.use(None)


def _visible(scope: CallerScope, doc_id: str) -> bool:
    return doc_id in knowledge_store.visible_guides(scope)


def _finds_secret(scope: CallerScope) -> bool:
    return any("wombat" in h.content for h in knowledge_store.search(scope, "golden wombat refund rule", limit=5))


# ---------- extraction ----------


def test_pdf_gives_one_section_per_page():
    got = extract("policy.pdf", _pdf("First page words", "Second page words"))
    assert got.kind == "pdf"
    assert "## Page 1\n\nFirst page words" in got.body and "## Page 2\n\nSecond page words" in got.body


def test_docx_keeps_headings_lists_and_tables():
    got = extract("policy.docx", _docx())
    assert got.title == "Refund policy"
    assert "## When refunds are paid" in got.body and "### Steps" in got.body
    assert "- Open the order" in got.body
    assert "| Plan | Days |" in got.body and "| Gold | 9 |" in got.body


def test_markdown_front_matter_is_separated():
    got = extract("a.md", b"---\ndoc_id: x.y\ntenants: [ettu]\n---\n# Title here\n\n## Part\n\nText")
    assert got.front_matter == {"doc_id": "x.y", "tenants": ["ettu"]}
    assert got.title == "Title here" and got.body.startswith("# Title here")


@pytest.mark.parametrize("name, message", [
    ("old.doc", "save the file as .docx"),
    ("sheet.xlsx", "Only .md, .pdf and .docx"),
])
def test_unsupported_types_are_refused(name, message):
    with pytest.raises(GuideError, match=message):
        extract(name, b"data")


def test_pdf_without_text_is_refused():
    with pytest.raises(GuideError, match="scanned PDF"):
        extract("scan.pdf", _pdf())


# ---------- upload and access ----------


def test_upload_is_visible_only_to_the_chosen_tenants(store):
    result = manage.upload(ADMIN, "refund-policy.pdf", _pdf(SECRET), tenants="ettu")
    assert result["result"] == "created" and result["doc_id"] == "upload.refund-policy"
    record = store.get("upload.refund-policy")
    assert record["status"] == "ready" and record["tenants"] == ["ettu"] and not record["all_tenants"]
    assert record["chunk_count"] == store.chunk_count("upload.refund-policy") > 0
    assert _visible(ETTU, "upload.refund-policy") and _finds_secret(ETTU)
    assert not _visible(DENMARK, "upload.refund-policy") and not _finds_secret(DENMARK)


def test_chunks_are_kept_with_embeddings(store):
    manage.upload(ADMIN, "refund.docx", _docx(), tenants="all")
    chunk = store.db[documents.CHUNKS].find_one({"doc_id": "upload.refund"})
    assert len(chunk["embedding"]) > 0 and chunk["embedding_model"] == get_settings().app_chat.embedding_model
    assert store.get_file(store.get("upload.refund")["file_id"]) == _docx()


def test_all_tenants_with_exclusion(store):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="all", exclude_tenants="denmark")
    assert _visible(ETTU, "upload.refund") and not _visible(DENMARK, "upload.refund")


def test_same_file_again_changes_nothing(store):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    again = manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    assert again["result"] == "unchanged"
    assert [a["action"] for a in store.audit_log("upload.refund")] == ["upload"]


def test_access_change_applies_at_once_without_re_embedding(store):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    before = {c["chunk_id"] for c in store.db[documents.CHUNKS].find({"doc_id": "upload.refund"})}
    manage.set_access(ADMIN, "upload.refund", tenants=["denmark"])
    assert _visible(DENMARK, "upload.refund") and not _visible(ETTU, "upload.refund")
    after = {c["chunk_id"] for c in store.db[documents.CHUNKS].find({"doc_id": "upload.refund"})}
    assert before == after
    change = store.audit_log("upload.refund")[0]
    assert change["action"] == "access" and change["details"]["after"]["tenants"] == ["denmark"]


def test_replace_keeps_previous_and_drops_old_chunks(store):
    manage.upload(ADMIN, "refund.pdf", _pdf("Old refund text about ducks"), tenants="ettu")
    old_file = store.get("upload.refund")["file_id"]
    result = manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    record = store.get("upload.refund")
    assert result["result"] == "replaced"
    assert record["previous"]["file_id"] == old_file and record["file_id"] != old_file
    hashes = {c["content_hash"] for c in store.db[documents.CHUNKS].find({"doc_id": "upload.refund"})}
    assert hashes == {record["content_hash"]}
    assert _finds_secret(ETTU)


def test_failed_processing_keeps_the_live_version(store, monkeypatch):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    real = knowledge_store.ingest_guide

    def broken(text, source="folder"):
        if "ducks" in text:
            raise RuntimeError("embedding server down")
        return real(text, source)

    monkeypatch.setattr(knowledge_store, "ingest_guide", broken)
    with pytest.raises(manage.ManageError) as e:
        manage.upload(ADMIN, "refund.pdf", _pdf("New text about ducks"), tenants="denmark")
    assert e.value.status == 500
    record = store.get("upload.refund")
    assert record["status"] == "failed" and "pending" not in record
    assert _finds_secret(ETTU) and not _visible(DENMARK, "upload.refund")


def test_failed_new_document_is_not_readable(store, monkeypatch):
    monkeypatch.setattr(knowledge_store, "export_document", lambda doc_id: 1 / 0)
    with pytest.raises(manage.ManageError):
        manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    assert store.get("upload.refund")["status"] == "failed"
    assert not _visible(ETTU, "upload.refund")


@pytest.mark.parametrize("kwargs, status, message", [
    ({"tenants": ""}, 400, "Choose which tenants"),
    ({"tenants": "ettu", "exclude_tenants": "denmark"}, 400, "only be given with all tenants"),
    ({"tenants": "bad tenant!"}, 400, "not a valid tenant"),
    ({"tenants": "ettu", "doc_id": "ettu.private-policy"}, 409, "built-in guide"),
])
def test_bad_uploads_are_refused(store, kwargs, status, message):
    with pytest.raises(manage.ManageError, match=message) as e:
        manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), **kwargs)
    assert e.value.status == status


def test_unknown_tenant_is_refused_when_a_list_is_set(store, monkeypatch):
    monkeypatch.setattr(get_settings().knowledge_manage, "allowed_tenants", ["ettu", "denmark"])
    with pytest.raises(manage.ManageError, match="Unknown tenant 'mars'"):
        manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu,mars")


def test_same_name_or_same_file_under_another_doc_id_is_refused(store):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    with pytest.raises(manage.ManageError, match="already uploaded as 'upload.refund'"):
        manage.upload(ADMIN, "Refund.pdf", _pdf("Different words"), tenants="ettu", doc_id="other.doc")
    with pytest.raises(manage.ManageError, match="already uploaded as 'upload.refund'"):
        manage.upload(ADMIN, "copy.pdf", _pdf(SECRET), tenants="ettu")


def test_markdown_front_matter_fills_in_tenants_and_routes(store):
    text = (b"---\ndoc_id: up.guide\ntitle: Refunds\ntenants: [ettu]\nroutes: [tms/refunds]\n"
            b"suggested_questions: ['When are refunds paid?']\n---\n## Refunds\n\n" + SECRET.encode())
    manage.upload(ADMIN, "refunds.md", text)
    entry = knowledge_store.list_guides_admin()["up.guide"]
    assert entry["access"]["tenants"] == ["ettu"] and entry["routes"] == ["tms/refunds"]
    assert entry["source"] == "upload"
    # The form wins over the file's own tenants.
    manage.upload(ADMIN, "refunds.md", text, tenants="denmark")
    assert knowledge_store.list_guides_admin()["up.guide"]["access"]["tenants"] == ["denmark"]


def test_delete_removes_everything(store):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    file_id = store.get("upload.refund")["file_id"]
    manage.delete(ADMIN, "upload.refund")
    assert store.get("upload.refund") is None and store.chunk_count("upload.refund") == 0
    assert not _visible(ETTU, "upload.refund") and not _finds_secret(ETTU)
    with pytest.raises(Exception):
        store.get_file(file_id)


# ---------- startup ----------


def test_restore_brings_back_uploads_and_removes_orphans(store):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    knowledge_store.delete_guide("upload.refund")  # the index lost it
    knowledge_store.ingest_guide("---\ndoc_id: up.orphan\ntitle: Orphan\ntenants: all\n---\n## A\n\nText", "upload")
    report = manage.restore()
    assert report["loaded"] == 1 and report["removed"] == 1
    assert _finds_secret(ETTU)
    assert "up.orphan" not in knowledge_store.list_guides_admin()


def test_restore_finishes_an_interrupted_upload(store):
    manage.upload(ADMIN, "refund.pdf", _pdf("Old refund text about ducks"), tenants="ettu")
    record = store.get("upload.refund")
    pending = manage._validated({**{k: record[k] for k in manage._VERSION_FIELDS}, "body": "## New\n\n" + SECRET,
                                 "file_hash": "new"}, "upload.refund")
    store.update("upload.refund", {"pending": pending, "status": "processing"})  # the process died here
    assert manage.restore()["resumed"] == 1
    assert store.get("upload.refund")["status"] == "ready" and _finds_secret(ETTU)


def test_guide_loader_keeps_uploaded_documents(store, tmp_path):
    manage.upload(ADMIN, "refund.pdf", _pdf(SECRET), tenants="ettu")
    folder = tmp_path / "guides"
    folder.mkdir()
    (folder / "one.md").write_text("---\ndoc_id: tms.one\ntitle: One\ntenants: all\n---\n## One\n\nText", encoding="utf-8")
    (folder / "clash.md").write_text("---\ndoc_id: upload.refund\ntitle: Clash\ntenants: all\n---\n## C\n\nText",
                                     encoding="utf-8")
    report = guide_loader.load_guides(folder)
    assert any("belongs to a document uploaded" in e for e in report.errors)
    assert "upload.refund" in knowledge_store.list_guides_admin() and _finds_secret(ETTU)


# ---------- API ----------


def _headers(role: str | None, tenant: str = "staging") -> dict:
    claims = {"user_id": "9", "tenant": tenant, "exp": int(time.time()) + 600}
    if role:
        claims["role_name"] = role
    return {"auth": f"Bearer {jwt.encode(claims, JWT_SECRET, algorithm='HS256')}", "tenant": tenant}


@pytest.fixture()
def client(store, monkeypatch):
    monkeypatch.setattr(get_settings().auth, "role_claims", ["role_name"])
    with TestClient(app) as c:
        documents.use(store)  # app startup does not connect in tests
        yield c


def test_api_refuses_non_admins(client):
    for role in (None, "Organizer", "Referee"):
        r = client.get("/api/knowledge/manage/documents", headers=_headers(role))
        assert r.status_code == 403


def test_api_allows_admin_and_super_admin(client):
    for role in ("Admin", "Super Admin", " super  ADMIN "):
        r = client.get("/api/knowledge/manage/documents", headers=_headers(role))
        assert r.status_code == 200, role


def test_api_upload_list_access_download_delete(client):
    h = _headers("Super Admin")
    r = client.post("/api/knowledge/manage/documents", headers=h,
                    files={"file": ("refund.docx", _docx())}, data={"tenants": "ettu"})
    assert r.status_code == 200, r.text
    assert r.json()["document"]["tenants"] == ["ettu"]
    listed = client.get("/api/knowledge/manage/documents", headers=h).json()["documents"]
    assert [d["doc_id"] for d in listed] == ["upload.refund"] and "body" not in listed[0]
    r = client.patch("/api/knowledge/manage/documents/upload.refund", headers=h, json={"tenants": ["all"]})
    assert r.status_code == 200 and r.json()["document"]["all_tenants"] is True
    r = client.get("/api/knowledge/manage/documents/upload.refund/file", headers=h)
    assert r.status_code == 200 and r.content == _docx() and "refund.docx" in r.headers["content-disposition"]
    assert client.delete("/api/knowledge/manage/documents/upload.refund", headers=h).status_code == 200
    assert client.get("/api/knowledge/manage/documents", headers=h).json()["documents"] == []


def test_api_reports_bad_files(client):
    r = client.post("/api/knowledge/manage/documents", headers=_headers("super admin"),
                    files={"file": ("old.doc", b"x")}, data={"tenants": "ettu"})
    assert r.status_code == 400 and ".docx" in r.json()["detail"]


def test_api_refuses_oversize_files(client, monkeypatch):
    monkeypatch.setattr(get_settings().knowledge_manage, "max_file_mb", 0.001)
    r = client.post("/api/knowledge/manage/documents", headers=_headers("Super Admin"),
                    files={"file": ("big.pdf", _pdf("x" * 2000))}, data={"tenants": "ettu"})
    assert r.status_code == 413


def test_api_without_mongodb_is_unavailable(client):
    documents.use(None)
    r = client.get("/api/knowledge/manage/documents", headers=_headers("Super Admin"))
    assert r.status_code == 503
