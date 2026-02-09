from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import verify_token
from typing import Dict, Any
import logging


security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current user from the JWT token.
    
    Args:
        credentials: HTTP authorization credentials from the request header
        
    Returns:
        User ID from the token if valid
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    # Log minimal information to help debug missing/malformed Authorization headers
    try:
        scheme = credentials.scheme
        token = credentials.credentials
    except Exception:
        logger.warning("No credentials provided in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("Authorization header received: scheme=%s, token_len=%d", scheme, len(token) if token else 0)
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Prefer explicit `user_id`, fall back to `sub` claim for compatibility.
    user_id = payload.get("user_id") or payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Normalize to string and strip whitespace to avoid accidental mismatches
    try:
        normalized = str(user_id).strip()
    except Exception:
        normalized = user_id

    logger.debug("Authenticated user id: %s", normalized)
    return normalized


def verify_user_id(user_id_from_token: str, user_id_from_path: str):
    """
    Verify that the user ID in the token matches the user ID in the path.
    
    Args:
        user_id_from_token: User ID extracted from the JWT token
        user_id_from_path: User ID from the URL path
        
    Raises:
        HTTPException: If the user IDs don't match
    """
    # Normalize both values to strings and strip whitespace before comparing.
    try:
        token_id = str(user_id_from_token).strip()
    except Exception:
        token_id = user_id_from_token

    try:
        path_id = str(user_id_from_path).strip()
    except Exception:
        path_id = user_id_from_path

    if token_id != path_id:
        logger.warning("User ID mismatch: token=%s path=%s", token_id, path_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User ID mismatch"
        )