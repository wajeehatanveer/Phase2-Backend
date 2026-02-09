import jwt
from datetime import datetime, timedelta
from typing import Optional
import logging
try:
    from ..settings import settings
except Exception:
    from backend.settings import settings

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with the given data and expiration time.
    
    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional timedelta for token expiration (defaults to 15 minutes)
        
    Returns:
        Encoded JWT token as a string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.better_auth_secret, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str):
    """
    Verify a JWT token and return the decoded data.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token data if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
        # Log a compact view of the payload (avoid logging secrets)
        logger.debug("JWT verified, payload keys: %s", list(payload.keys()))
        # Ensure there is a user identifier
        if "user_id" not in payload and "sub" not in payload:
            logger.warning("JWT missing 'user_id' or 'sub' claims: %s", payload)
            return None
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.warning("JWT expired: %s", e)
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid JWT token: %s", e)
        return None
    except Exception as e:
        logger.exception("Unexpected error while verifying JWT: %s", e)
        return None