"""OAuth token management with automatic refresh for social media platforms."""

import os
import json
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import requests
from pulsepilot.core.secrets import get_secrets_manager

logger = logging.getLogger(__name__)


@dataclass
class OAuthToken:
    """OAuth token data with expiration tracking."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # seconds
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: float = 0.0  # Unix timestamp

    def __post_init__(self):
        """Set created_at if not provided."""
        if self.created_at == 0.0:
            self.created_at = time.time()

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_in <= 0:
            return False  # Never expires
        expiration_time = self.created_at + self.expires_in
        # Consider expired if less than 5 minutes remaining
        return time.time() >= (expiration_time - 300)

    @property
    def expires_at(self) -> datetime:
        """Get token expiration datetime."""
        return datetime.fromtimestamp(self.created_at + self.expires_in)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthToken":
        """Create from dictionary."""
        return cls(**data)


class OAuthTokenManager:
    """Manages OAuth tokens with automatic refresh."""

    def __init__(self, platform: str, secrets_manager=None):
        """
        Initialize OAuth token manager.

        Args:
            platform: Platform name (e.g., 'instagram', 'google')
            secrets_manager: Optional secrets manager instance
        """
        self.platform = platform.lower()
        self.secrets_manager = secrets_manager or get_secrets_manager()
        self._token_cache: Optional[OAuthToken] = None

    def _get_token_secret_name(self) -> str:
        """Get the secret name for storing tokens."""
        return f"{self.platform.upper()}_OAUTH_TOKEN"

    def _get_credentials_secret_name(self) -> str:
        """Get the secret name for OAuth credentials."""
        return f"{self.platform.upper()}_OAUTH_CREDENTIALS"

    def get_token(self, force_refresh: bool = False) -> Optional[OAuthToken]:
        """
        Get valid OAuth token, refreshing if necessary.

        Args:
            force_refresh: Force token refresh even if not expired

        Returns:
            Valid OAuth token or None if unavailable
        """
        # Check cache first
        if not force_refresh and self._token_cache and not self._token_cache.is_expired:
            logger.debug(f"Using cached token for {self.platform}")
            return self._token_cache

        # Load token from secrets manager
        token_data = self.secrets_manager.get_secret_dict(self._get_token_secret_name())
        if token_data:
            token = OAuthToken.from_dict(token_data)

            # Check if expired and refresh if possible
            if force_refresh or token.is_expired:
                if token.refresh_token:
                    logger.info(f"Refreshing expired token for {self.platform}")
                    refreshed_token = self._refresh_token(token.refresh_token)
                    if refreshed_token:
                        token = refreshed_token
                        self._save_token(token)
                    else:
                        logger.error(f"Failed to refresh token for {self.platform}")
                        return None
                else:
                    logger.warning(
                        f"Token for {self.platform} is expired and no refresh token available"
                    )
                    return None

            self._token_cache = token
            return token

        logger.warning(f"No token found for {self.platform}")
        return None

    def set_token(self, token: OAuthToken) -> bool:
        """
        Store OAuth token.

        Args:
            token: OAuth token to store

        Returns:
            True if successful
        """
        self._token_cache = token
        return self._save_token(token)

    def _save_token(self, token: OAuthToken) -> bool:
        """Save token to secrets manager."""
        token_data = json.dumps(token.to_dict())
        return self.secrets_manager.set_secret(
            self._get_token_secret_name(),
            token_data
        )

    def _refresh_token(self, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh OAuth token.

        Args:
            refresh_token: Refresh token

        Returns:
            New OAuth token or None if refresh failed
        """
        if self.platform == "instagram":
            return self._refresh_instagram_token(refresh_token)
        elif self.platform == "google":
            return self._refresh_google_token(refresh_token)
        elif self.platform == "facebook":
            return self._refresh_facebook_token(refresh_token)
        else:
            logger.error(f"Token refresh not implemented for {self.platform}")
            return None

    def _refresh_instagram_token(self, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh Instagram access token.

        Instagram uses long-lived tokens that can be refreshed before expiration.
        """
        try:
            # Instagram Graph API token refresh
            url = "https://graph.instagram.com/refresh_access_token"
            params = {
                "grant_type": "ig_refresh_token",
                "access_token": refresh_token
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "access_token" in data:
                return OAuthToken(
                    access_token=data["access_token"],
                    token_type=data.get("token_type", "Bearer"),
                    expires_in=data.get("expires_in", 5184000),  # 60 days default
                    refresh_token=refresh_token  # Keep same refresh token
                )
            else:
                logger.error(f"Instagram token refresh failed: {data.get('error', {})}")
                return None

        except Exception as e:
            logger.error(f"Error refreshing Instagram token: {e}")
            return None

    def _refresh_google_token(self, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh Google OAuth token.
        """
        try:
            # Get OAuth credentials
            creds_data = self.secrets_manager.get_secret_dict(
                self._get_credentials_secret_name()
            )
            if not creds_data:
                logger.error("Google OAuth credentials not found")
                return None

            client_id = creds_data.get("client_id")
            client_secret = creds_data.get("client_secret")

            if not client_id or not client_secret:
                logger.error("Missing Google client_id or client_secret")
                return None

            # Refresh token
            url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }

            response = requests.post(url, data=data, timeout=10)
            response_data = response.json()

            if "access_token" in response_data:
                return OAuthToken(
                    access_token=response_data["access_token"],
                    token_type=response_data.get("token_type", "Bearer"),
                    expires_in=response_data.get("expires_in", 3600),
                    refresh_token=refresh_token,  # Keep same refresh token
                    scope=response_data.get("scope")
                )
            else:
                logger.error(f"Google token refresh failed: {response_data.get('error')}")
                return None

        except Exception as e:
            logger.error(f"Error refreshing Google token: {e}")
            return None

    def _refresh_facebook_token(self, current_token: str) -> Optional[OAuthToken]:
        """
        Refresh Facebook access token.

        Facebook uses token exchange to get long-lived tokens.
        """
        try:
            # Get OAuth credentials
            creds_data = self.secrets_manager.get_secret_dict(
                self._get_credentials_secret_name()
            )
            if not creds_data:
                logger.error("Facebook OAuth credentials not found")
                return None

            app_id = creds_data.get("app_id")
            app_secret = creds_data.get("app_secret")

            if not app_id or not app_secret:
                logger.error("Missing Facebook app_id or app_secret")
                return None

            # Exchange for long-lived token
            url = "https://graph.facebook.com/v19.0/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": current_token
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "access_token" in data:
                return OAuthToken(
                    access_token=data["access_token"],
                    token_type=data.get("token_type", "Bearer"),
                    expires_in=data.get("expires_in", 5184000),  # 60 days default
                    refresh_token=None  # Facebook doesn't use refresh tokens
                )
            else:
                logger.error(f"Facebook token refresh failed: {data.get('error', {})}")
                return None

        except Exception as e:
            logger.error(f"Error refreshing Facebook token: {e}")
            return None

    def revoke_token(self) -> bool:
        """
        Revoke the current OAuth token.

        Returns:
            True if successful
        """
        token = self.get_token()
        if not token:
            logger.warning(f"No token to revoke for {self.platform}")
            return False

        # Platform-specific revocation
        success = False
        if self.platform == "google":
            success = self._revoke_google_token(token.access_token)
        else:
            logger.warning(f"Token revocation not implemented for {self.platform}")
            success = True  # Just delete locally

        # Delete from secrets manager
        if success:
            self.secrets_manager.delete_secret(self._get_token_secret_name())
            self._token_cache = None

        return success

    def _revoke_google_token(self, access_token: str) -> bool:
        """Revoke Google OAuth token."""
        try:
            url = "https://oauth2.googleapis.com/revoke"
            params = {"token": access_token}
            response = requests.post(url, params=params, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error revoking Google token: {e}")
            return False


class InstagramOAuthManager(OAuthTokenManager):
    """Instagram-specific OAuth manager."""

    def __init__(self, secrets_manager=None):
        """Initialize Instagram OAuth manager."""
        super().__init__("instagram", secrets_manager)

    def get_user_id(self) -> Optional[str]:
        """Get Instagram user ID from stored credentials."""
        return self.secrets_manager.get_secret("INSTAGRAM_IG_USER_ID")


class GoogleOAuthManager(OAuthTokenManager):
    """Google-specific OAuth manager."""

    def __init__(self, secrets_manager=None):
        """Initialize Google OAuth manager."""
        super().__init__("google", secrets_manager)

    def get_credentials_for_service(self, service: str) -> Optional[Dict[str, str]]:
        """
        Get Google credentials for a specific service.

        Args:
            service: Service name (e.g., 'youtube', 'gmail', 'analytics')

        Returns:
            Credentials dictionary with access_token
        """
        token = self.get_token()
        if not token:
            return None

        return {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "service": service
        }


class FacebookOAuthManager(OAuthTokenManager):
    """Facebook-specific OAuth manager."""

    def __init__(self, secrets_manager=None):
        """Initialize Facebook OAuth manager."""
        super().__init__("facebook", secrets_manager)

    def get_page_id(self) -> Optional[str]:
        """Get Facebook page ID from stored credentials."""
        return self.secrets_manager.get_secret("FACEBOOK_PAGE_ID")
