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
    llm: LLMConfig
    logging: LoggingConfig
    messages: MessagesConfig

    nvidia_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="NVIDIA_API_KEY",
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
