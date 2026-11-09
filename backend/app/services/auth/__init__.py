"""Validación del JWT de Keycloak (ACO-014)."""

from .config import CLIENT_ID, AuthSettings, load_settings
from .errors import AuthError, AuthErrorCode
from .models import Principal
from .tokens import JWKSClient, validate_token
from .whitelist import (
    EMAILS_AUTORIZADOS_ENV,
    is_email_authorized,
    load_authorized_emails,
    log_whitelist_summary,
    parse_authorized_emails,
)

__all__ = [
    "AuthError",
    "AuthErrorCode",
    "AuthSettings",
    "CLIENT_ID",
    "EMAILS_AUTORIZADOS_ENV",
    "JWKSClient",
    "Principal",
    "is_email_authorized",
    "load_authorized_emails",
    "load_settings",
    "log_whitelist_summary",
    "parse_authorized_emails",
    "validate_token",
]
