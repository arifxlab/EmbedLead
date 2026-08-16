from app.core.config import Settings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.app_name == "EmbedLead"
    assert settings.app_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"


def test_cors_origins_are_parsed() -> None:
    settings = Settings(cors_allowed_origins="https://example.com, https://app.example.com")

    assert settings.cors_origins == [
        "https://example.com",
        "https://app.example.com",
    ]


def test_submission_payload_limit_is_positive() -> None:
    settings = Settings()

    assert settings.max_submission_payload_bytes > 0
