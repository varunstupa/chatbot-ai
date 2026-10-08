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

    persist_directory: str = "data/chroma_kb"
    # One collection for every tenant; access is decided by the document registry.
    collection_name: str = "knowledge_chunks"
    registry_file: str = "document_registry.json"
    # Guide Markdown files, loaded at every backend start (app.knowledge.guide_loader).
    guides_directory: str = "guides"
    top_k: int = Field(default=5, ge=1, le=20)
    # Chroma distance (lower is closer). Hits above the limit count as no match.
    # Measured with all-mpnet-base-v2 on the Event Details guide: right answers
    # scored 0.35-1.33, unrelated questions 1.37 and above.
    # Limit for the screen the user is on (lenient: the model still has to find
    # the answer in the passage).
    screen_max_distance: float = Field(default=1.4, gt=0)
    # Limit for guides of other screens, and for guides named in the question.
    max_distance: float = Field(default=1.35, gt=0)
    # Another screen's guide wins over the current one only if this much closer.
    other_screen_margin: float = Field(default=0.15, ge=0)
    # all-mpnet-base-v2 reads ~384 tokens, so guide chunks stay small.
    chunk_size: int = Field(default=1500, ge=200)
    chunk_overlap: int = Field(default=150, ge=0)
    # Earlier messages resent with each question; fewer keeps follow-ups fast.
    history_messages: int = Field(default=6, ge=0, le=30)
    no_answer_message: str = (
        "I couldn't find that in the guides available to you. "
        "Say **report an issue** if you want to raise a support ticket."
    )
    prompt_template: str = Field(
        default=(
            "You are the in-app assistant of an event management system.\n"
            "The user is currently on the screen: {screen}.\n"
            "Answer ONLY from the Context below. Each passage names the screen "
            "it describes. If the passage is about a different screen than the "
            "one the user is on, say which screen it is done on.\n"
            "Use the exact button and field names from the Context and keep steps in "
            "the order the Context gives them. Never mention other organisations or "
            "tenants.\n"
            "Write only the answer, in plain sentences or a short list. Do not "
            "repeat passage titles and do not add headings.\n"
            "If the Context does not answer the Question, reply with exactly: "
            "I don't know\n\n"
            "Context:\n{context}\n\nQuestion:\n{question}\n\n"
            "Answer (concise Markdown):"
        ),
    )

    @field_validator("prompt_template")
    @classmethod
    def prompt_has_placeholders(cls, v: str) -> str:
        for name in ("{context}", "{question}", "{screen}"):
            if name not in v:
                raise ValueError(f"app_chat.prompt_template must include {name}")
        return v


class LLMConfig(BaseModel):
    provider: str
    temperature: float = Field(ge=0.0, le=2.0)
    model: str
    base_url: str
    system_message: Optional[str] = None
    missing_api_key_message: str = "Set NVIDIA_API_KEY in .env or your environment."
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    local_base_url: str = "http://localhost:11434"
    local_model_name: str = "llama3.2:1b"
    # How long Ollama keeps the model in memory after a request.
    local_keep_alive: str = "30m"

    @field_validator("provider")
    @classmethod
    def provider_allowed(cls, v: str) -> str:
        allowed = {"nvidia", "local", "ollama"}
        if v not in allowed:
            raise ValueError(f"llm.provider must be one of {sorted(allowed)}")
        return v


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

    nvidia_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="NVIDIA_API_KEY",
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
