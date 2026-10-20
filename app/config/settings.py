"""Centralized configuration: YAML + Pydantic Settings (env / .env), singleton access."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic_settings.exceptions import SettingsError

_CONFIG_LOCK = Lock()
_SETTINGS_CACHE: "Settings | None" = None

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _default_config_path() -> Path:
    env_path = os.environ.get("CONFIG_FILE")
    if env_path:
        return Path(env_path).resolve()
    base = Path(__file__).resolve().parent
    app_env = os.environ.get("APP_ENV", "").strip().lower()
    if app_env == "production":
        candidate = base / "config.production.yaml"
        if candidate.is_file():
            return candidate
    elif app_env == "development":
        candidate = base / "config.development.yaml"
        if candidate.is_file():
            return candidate
    return base / "config.yaml"


class YamlSettingsSource(PydanticBaseSettingsSource):
    """Load structured values from ``config.yaml`` (non-secret fields)."""

    def __init__(self, settings_cls: type[BaseSettings]):
        super().__init__(settings_cls)
        self._yaml_data: dict[str, Any] | None = None

    def _load(self) -> dict[str, Any]:
        if self._yaml_data is not None:
            return self._yaml_data
        path = _default_config_path()
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        raw = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}") from e
        if not isinstance(data, dict):
            raise ValueError("Configuration root must be a mapping")
        self._yaml_data = data
        return self._yaml_data

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        data = self._load()
        if field_name not in data:
            return None, field_name, False
        return data[field_name], field_name, self.field_is_complex(field)

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if value is not None and value_is_complex and isinstance(value, (dict, list)):
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for field_name, field in self.settings_cls.model_fields.items():
            try:
                field_value, field_key, value_is_complex = self.get_field_value(
                    field, field_name
                )
                field_value = self.prepare_field_value(
                    field_name, field, field_value, value_is_complex
                )
            except ValueError as e:
                raise SettingsError(
                    f'error parsing value for field "{field_name}" from YAML'
                ) from e
            if field_value is not None:
                data[field_key] = field_value
        return data


class AppInfo(BaseModel):
    name: str
    version: str


class ServerConfig(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)


class PathsConfig(BaseModel):
    upload_dir: str


class ChunkingConfig(BaseModel):
    chunk_size: int = Field(ge=1)
    chunk_overlap: int = Field(ge=0)


class EmbeddingConfig(BaseModel):
    model_name: str
    model_kwargs: dict[str, Any] = Field(default_factory=dict)
    encode_kwargs: dict[str, Any] = Field(default_factory=dict)
    query_prefix: str = ""
    passage_prefix: str = ""


class VectorStoreConfig(BaseModel):
    collection_name: str
    persist_directory: str
    top_k: int = Field(ge=1, le=100)


class RAGConfig(BaseModel):
    prompt_template: str


StupaRagCorpus = Literal["merged", "website", "uploads"]


class DemoBookingConfig(BaseModel):
    """After user confirms demo wizard, POST to Stupa send-email (or disable)."""

    send_email_url: str = "https://stupasports.ai/api/send-email"
    enabled: bool = True


class JiraConfig(BaseModel):
    """Jira Cloud ticket creation (secrets via ``JIRA_API_TOKEN`` in ``.env``)."""

    base_url: str = ""
    email: str = ""
    project_key: str = ""
    issue_type: str = "Bug"


class StupaChatConfig(BaseModel):
    """Stupa public chat: corpus + strict RAG prompt (demo flow unchanged)."""

    rag_corpus: StupaRagCorpus = "website"
    prompt_template: str = Field(
        min_length=20,
        description="Must contain {context} and {question} placeholders.",
    )

    @field_validator("prompt_template")
    @classmethod
    def prompt_has_placeholders(cls, v: str) -> str:
        t = (v or "").strip()
        if "{context}" not in t or "{question}" not in t:
            raise ValueError(
                "stupa_chat.prompt_template must include {context} and {question}",
            )
        return t


class AuthConfig(BaseModel):
    """Login JWT verification for the admin-app chat (keys come from ``.env``)."""

    # "jwt": the browser calls the chatbot with the login token (local development).
    # "gateway": only requests signed by the API gateway are accepted
    # (CHATBOT_INTERNAL_SECRET); the gateway has already verified the login token.
    mode: Literal["jwt", "gateway"] = "jwt"
    jwt_algorithms: list[str] = Field(default_factory=lambda: ["HS256"])
    # Tenants this deployment answers for. Empty means any tenant in a valid token.
    allowed_tenants: list[str] = Field(default_factory=list)
    # First claim present in the token wins.
    tenant_claims: list[str] = Field(
        default_factory=lambda: ["tenant", "tenant_code", "tenant_name"],
    )
    user_claims: list[str] = Field(
        default_factory=lambda: ["user_id", "sub", "id"],
    )
    role_claims: list[str] = Field(
        default_factory=lambda: ["role_id", "role"],
    )


class CorsConfig(BaseModel):
    allow_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
    )


class AppChatConfig(BaseModel):
    """Admin-app chat: screen guides stored per tenant, screen-aware retrieval."""

    # One folder per embedding model: vectors of two models must never share a store.
    persist_directory: str = "data/chroma_kb_me5"
    # One collection for every tenant; access is decided by the document registry.
    collection_name: str = "knowledge_chunks"
    registry_file: str = "document_registry.json"
    # Guide Markdown files, loaded at every backend start (app.knowledge.guide_loader).
    guides_directory: str = "guides"
    # Multilingual, so questions in any language find the English guides.
    # Changing it needs a new persist_directory (the guides are re-embedded there).
    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_query_prefix: str = "query: "
    embedding_passage_prefix: str = "passage: "
    top_k: int = Field(default=5, ge=1, le=20)
    # Chroma distance (squared L2 on normalized vectors, lower is closer). Hits above
    # the limit count as no match. Measured with multilingual-e5-base on questions in
    # 7 languages: right answers 0.32-0.51, off-topic questions 0.38-0.42. The ranges
    # overlap, so the limits only drop clearly unrelated text; the prompt makes the
    # model say when the passages do not answer the question.
    # Limit for the screen the user is on.
    screen_max_distance: float = Field(default=0.55, gt=0)
    # Limit for guides of other screens, and for guides named in the question.
    max_distance: float = Field(default=0.52, gt=0)
    # Passages are ranked together; these boosts lower the distance of the current
    # screen's guides and of guides named in the question. Lower is closer.
    screen_boost: float = Field(default=0.03, ge=0)
    topic_boost: float = Field(default=0.05, ge=0)
    # How many passages from all guides are ranked before the boosts are applied.
    candidate_pool: int = Field(default=20, ge=5, le=100)
    # Hybrid search: keyword (BM25) results join the semantic candidates, so exact
    # labels and message texts are found. keyword_boost lowers the distance of the best
    # keyword match by that much, the second by half, the third by a third, and so on.
    keyword_search: bool = True
    keyword_pool: int = Field(default=10, ge=0, le=50)
    keyword_boost: float = Field(default=0.03, ge=0)
    # Cross-encoder rerank of the candidates left after the limits. Its score divided by
    # rerank_scale is used as the distance, so the boosts above still decide near ties.
    rerank: bool = False
    rerank_model: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    rerank_pool: int = Field(default=12, ge=1, le=50)
    rerank_scale: float = Field(default=10.0, gt=0)
    # When retrieval is weak (nothing within the limits, or the best passage farther than
    # rewrite_above), the model rewrites the question as an English search query and the
    # search runs again. Costs one extra model call, only for those questions.
    rewrite_weak_questions: bool = False
    rewrite_above: float = Field(default=0.47, gt=0)
    # When a question about the modules gets no answer, the closest suggested questions of
    # the guides are offered ("Did you mean"). Only those within this distance; a question
    # with none that close is not about the modules and gets the plain no-answer message.
    suggest_max_distance: float = Field(default=0.27, gt=0)
    suggest_count: int = Field(default=3, ge=0, le=6)
    # Where each guide's screen is in the app, by doc_id prefix (the longest prefix wins).
    # Added to every passage, so an answer from another screen says where to go.
    screen_locations: dict[str, str] = Field(
        default_factory=lambda: {
            "tms.event-settings": "the Event page (open Event from the sidebar)",
            "tms.event-settings.create-event": "the Event page, Details step (open Event from the sidebar)",
            **{
                f"tms.event-settings.{key}": f"the {step} step of the Event page (open Event from the sidebar, then click {step} in the setup steps at the top)"
                for key, step in {
                    "registration": "Registration", "playing-order": "Playing Order",
                    "draw-settings": "Draw Settings", "payment-invoice": "Payment & Invoice",
                    "umpire-settings": "Umpire Settings", "referee-settings": "Referee Settings",
                    "day-planner": "Day Planner", "game-play": "Game Play",
                    "event-accommodation": "Accommodation", "event-travel": "Travel",
                    "print-settings": "Print Settings", "access-control": "Access-Control",
                    "documents-sponsors": "Documents & Sponsors",
                }.items()
            },
            "tms.players": "the Players page (open Players from the sidebar)",
            "tms.fixture": "the Fixtures/Results page (open Fixtures/Results from the sidebar)",
            "tms.schedular": "the Schedule page (open Schedule from the sidebar)",
            "tms.score-stream": "the Scoring and Streaming page (open Scoring and Streaming from the sidebar)",
            "tms.awards": "the Awards and Standing page (open Awards and Standing from the sidebar)",
            "tms.printing": "the Printing page (open Printing from the sidebar)",
            "tms.ranking": "the Rankings page (open Rankings from the sidebar)",
            "tms.display-setting": "the Display Settings page (open Display Settings from the sidebar)",
            "tms.leaderboard": "the Leaderboard page (open Leaderboard from the sidebar)",
            "tms.export-share-results": "the Export/Share Results page (open Export/Share Results from the sidebar)",
            "tms.navigation": "the sidebar (it lists every module)",
        },
    )
    did_you_mean_message: str ="I couldn't find an exact answer to that. Did you mean:"
    # The same intro per question language (ISO 639-1); others get did_you_mean_message.
    did_you_mean_messages: dict[str, str] = Field(
        default_factory=lambda: {
            "de": "Dazu habe ich keine genaue Antwort gefunden. Meintest du:",
            "fr": "Je n'ai pas trouvé de réponse exacte. Vouliez-vous dire :",
            "es": "No encontré una respuesta exacta. ¿Quisiste decir:",
            "it": "Non ho trovato una risposta esatta. Intendevi:",
            "pt": "Não encontrei uma resposta exata. Você quis dizer:",
            "nl": "Ik heb geen exact antwoord gevonden. Bedoelde je:",
            "sv": "Jag hittade inget exakt svar. Menade du:",
            "da": "Jeg fandt ikke et præcist svar. Mente du:",
            "no": "Jeg fant ikke et nøyaktig svar. Mente du:",
            "cs": "Nenašel jsem přesnou odpověď. Měli jste na mysli:",
            "pl": "Nie znalazłem dokładnej odpowiedzi. Czy chodziło Ci o:",
            "hi": "मुझे इसका सटीक उत्तर नहीं मिला। क्या आपका मतलब था:",
        },
    )
    # multilingual-e5-base reads 512 tokens; 1500-character chunks stay under it.
    chunk_size: int = Field(default=1500, ge=200)
    chunk_overlap: int = Field(default=150, ge=0)
    # Earlier messages resent with each question; fewer keeps follow-ups fast.
    history_messages: int = Field(default=6, ge=0, le=30)
    no_answer_message: str = "I couldn't find that in the guides available to you."
    # The same message per question language (ISO 639-1); others get no_answer_message.
    no_answer_messages: dict[str, str] = Field(
        default_factory=lambda: {
            "de": "Dazu habe ich in den für dich verfügbaren Anleitungen nichts gefunden.",
            "fr": "Je n'ai rien trouvé à ce sujet dans les guides qui vous sont accessibles.",
            "es": "No encontré esa información en las guías disponibles para ti.",
            "it": "Non ho trovato queste informazioni nelle guide a tua disposizione.",
            "pt": "Não encontrei isso nos guias disponíveis para você.",
            "nl": "Ik heb dat niet gevonden in de handleidingen die voor jou beschikbaar zijn.",
            "sv": "Jag hittade inte det i de guider som är tillgängliga för dig.",
            "da": "Jeg kunne ikke finde det i de vejledninger, du har adgang til.",
            "no": "Jeg fant ikke det i veiledningene du har tilgang til.",
            "cs": "V návodech, které máte k dispozici, jsem to nenašel.",
            "pl": "Nie znalazłem tego w przewodnikach dostępnych dla Ciebie.",
            "hi": "आपके लिए उपलब्ध गाइड में मुझे यह जानकारी नहीं मिली।",
        },
    )
    prompt_template: str = Field(
        default=(
            "You are the in-app assistant of an event management system.\n"
            "The user is currently on the screen: {screen}.\n"
            "The organisation's sport is: {sport}. Passages that name sports apply "
            "only to those sports; ignore passages written for another sport.\n"
            "Answer ONLY from the Context below. Each passage says where its screen is in the "
            "app and whether it is the screen the user is on. Never tell the user to go to "
            "the screen they are on, and never say a feature is on the user's screen when its "
            "passage says it is not.\n"
            "Prefer passages from the guide of the user's current screen. Use a passage from another "
            "screen only when no current-screen passage answers the Question, and then begin the answer "
            "with where it is, from that passage's 'Where it is in the app', for example: This is on the "
            "Fixtures/Results page: open Fixtures/Results from the sidebar. Then give its steps. Never copy steps from "
            "a different page as if they were on the current screen.\n"
            "Use the exact button and field names from the Context and keep steps in "
            "the order the Context gives them. Never mention other organisations or "
            "tenants.\n"
            "For a how-to question, give every step and every setting the Context describes for that task, in the order the page shows them. Do not reduce it to one sentence.\n"
            "Number the steps when there are several. Describe where to go as: open the section from the sidebar, then click the tab, for example: Open Score and Streaming from the sidebar, then click the Streaming tab.\n"
            "Call on and off controls toggles. Never write the word switch.\n"
            "When the user reports a problem (something does not work, is missing or is refused), first give the likely cause the Context states, then the numbered steps to fix it. Never give a cause the Context does not state, and never guess general causes such as the internet connection.\n"
            "Never mention the Context, passages or guides in the answer.\n"
            "If the Question could mean two different features of the Context, answer the more likely one and end with one short question asking which the user meant. Otherwise do not ask questions.\n"
            "Write the answer in plain sentences, numbered steps or a short list. Do not "
            "repeat passage titles and do not add headings.\n"
            "Write the entire answer in {language}, even though the Context is in "
            "English. Keep URLs, numbers and exact values unchanged.\n"
            "Do not repeat the Question and do not put the answer in a code block.\n"
            "If the Context does not answer the Question, reply with exactly "
            "NO_ANSWER and nothing else: no explanation, no other words.\n"
            "Never name an API, endpoint, HTTP method, URL path, gateway route, backend service or database table, and never show a route such as tms/... or /v1/... "
            "Describe what the user clicks and fills in on the screen instead. If the Context only describes an API call, answer with the screen steps or reply NO_ANSWER.\n"
            "Never write code, scripts, commands, queries or programming solutions, even when asked for them. Answer only about the event management system; reply NO_ANSWER to general knowledge, programming exercises and any other off-topic request.\n"
            "Never translate NO_ANSWER.\n\n"
            "Context:\n{context}\n\nQuestion:\n{question}\n\n"
            "Answer (concise Markdown):"
        ),
    )

    @field_validator("prompt_template")
    @classmethod
    def prompt_has_placeholders(cls, v: str) -> str:
        for name in ("{context}", "{question}", "{screen}", "{language}"):
            if name not in v:
                raise ValueError(f"app_chat.prompt_template must include {name}")
        return v


class LLMConfig(BaseModel):
    provider: str
    temperature: float = Field(ge=0.0, le=2.0)
    system_message: Optional[str] = None
    local_base_url: str = "http://localhost:11434"
    local_model_name: str = "llama3.2:1b"
    # How long Ollama keeps the model in memory after a request.
    local_keep_alive: str = "30m"
    # Thinking models (qwen3.5) reason before answering unless told not to; on CPU
    # that takes minutes per answer. None leaves it to the model's default.
    local_reasoning: Optional[bool] = False

    @field_validator("provider")
    @classmethod
    def provider_allowed(cls, v: str) -> str:
        allowed = {"local", "ollama"}
        if v not in allowed:
            raise ValueError(f"llm.provider must be one of {sorted(allowed)}")
        return v


class ChatStoreConfig(BaseModel):
    """MongoDB record of admin-chat conversations, one document per tenant and session (app/services/chat_store.py)."""

    enabled: bool = False
    # CHAT_STORE_MONGODB_URI overrides this (it may hold a password).
    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    database: str = "stupa_chatbot"
    # A session is removed by MongoDB this long after its last message (TTL index); 0 keeps everything.
    retention_days: int = Field(default=180, ge=0)
    # Newest messages kept in one session document (MongoDB documents are limited to 16 MB).
    max_messages_per_session: int = Field(default=500, ge=1)
    # A session's messages are kept in memory and written to MongoDB in one go when:
    # it has been idle this long, the widget sends "session closed", it holds
    # flush_at_messages messages, or the chatbot shuts down.
    idle_minutes: float = Field(default=30, gt=0)
    flush_at_messages: int = Field(default=50, ge=1)
    # Safety write for sessions still open, so a crash loses at most this much.
    safety_flush_minutes: float = Field(default=10, gt=0)
    # How often the writer checks for idle and overdue sessions.
    check_seconds: float = Field(default=30, gt=0)
    # Memory guard: above this many unwritten messages everything is written early.
    max_buffered_messages: int = Field(default=10000, ge=1)


class LoggingConfig(BaseModel):
    level: str
    json_format: bool


class MessagesConfig(BaseModel):
    upload_success: str
    missing_filename: str
    upload_empty: str
    query_empty: str
    query_processing_failed: str
    ticket_jira_not_configured: str = (
        "Ticket creation is not configured on the server. "
        "Please contact your administrator."
    )
    ticket_create_failed: str = "Unable to create ticket. Please try again."
    ticket_session_lost: str = (
        "This ticket draft expired or was interrupted. "
        "Say **report an issue** to start again."
    )


class Settings(BaseSettings):
    """Loads ``config.yaml`` first, then ``.env`` / process environment (see model_config)."""

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppInfo
    server: ServerConfig
    paths: PathsConfig
    chunking: ChunkingConfig
    embedding: EmbeddingConfig
    vector_store: VectorStoreConfig
    website_vector_store: VectorStoreConfig
    rag: RAGConfig
    stupa_chat: StupaChatConfig
    demo_booking: DemoBookingConfig = Field(default_factory=DemoBookingConfig)
    jira: JiraConfig = Field(default_factory=JiraConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)
    app_chat: AppChatConfig = Field(default_factory=AppChatConfig)
    chat_store: ChatStoreConfig = Field(default_factory=ChatStoreConfig)
    llm: LLMConfig
    logging: LoggingConfig
    messages: MessagesConfig

    # HS* shared secret or RS*/ES* public key (PEM) used to verify login tokens.
    app_chat_jwt_secret: Optional[SecretStr] = Field(
        default=None,
        validation_alias="APP_CHAT_JWT_SECRET",
    )
    app_chat_jwt_public_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="APP_CHAT_JWT_PUBLIC_KEY",
    )
    # Local development only: accept tokens without checking the signature.
    app_chat_allow_unverified_dev_tokens: bool = Field(
        default=False,
        validation_alias="APP_CHAT_ALLOW_UNVERIFIED_DEV_TOKENS",
    )
    # Shared with the API gateway; verifies the identity it forwards (auth.mode: gateway).
    chatbot_internal_secret: Optional[SecretStr] = Field(
        default=None,
        validation_alias="CHATBOT_INTERNAL_SECRET",
    )
    # Required by the guide listing and /upload (header X-Service-Key).
    knowledge_service_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="KNOWLEDGE_SERVICE_KEY",
    )

    # Overrides chat_store.mongodb_uri.
    chat_store_mongodb_uri: Optional[SecretStr] = Field(
        default=None,
        validation_alias="CHAT_STORE_MONGODB_URI",
    )

    jira_api_token: Optional[SecretStr] = Field(
        default=None,
        validation_alias="JIRA_API_TOKEN",
    )
    jira_base_url: str = Field(default="", validation_alias="JIRA_BASE_URL")
    jira_email: str = Field(default="", validation_alias="JIRA_EMAIL")
    jira_project_key: str = Field(default="", validation_alias="JIRA_PROJECT_KEY")
    jira_issue_type: str = Field(default="Bug", validation_alias="JIRA_ISSUE_TYPE")
    jira_issue_type_id: str = Field(
        default="",
        validation_alias="JIRA_ISSUE_TYPE_ID",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlSettingsSource(settings_cls),
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )


def get_settings(force_reload: bool = False) -> Settings:
    """Return the cached Settings singleton (thread-safe)."""
    global _SETTINGS_CACHE
    with _CONFIG_LOCK:
        if _SETTINGS_CACHE is None or force_reload:
            try:
                _SETTINGS_CACHE = Settings()
            except Exception as e:
                raise ValueError(f"Configuration validation failed: {e}") from e
        return _SETTINGS_CACHE


def reload_settings() -> Settings:
    """Reload configuration from disk / env without process restart."""
    global _SETTINGS_CACHE
    with _CONFIG_LOCK:
        try:
            _SETTINGS_CACHE = Settings()
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}") from e
        return _SETTINGS_CACHE


class _SettingsProxy:
    """Proxy so ``from app.config.settings import settings`` reads the current singleton."""

    def __getattr__(self, name: str):
        inst = get_settings()
        return getattr(inst, name)

    def __repr__(self) -> str:
        return repr(get_settings())


settings = _SettingsProxy()
