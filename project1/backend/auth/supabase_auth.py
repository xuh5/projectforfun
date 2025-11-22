from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Security scheme for extracting Bearer token
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    Verify JWT token and return user information.
    Automatically creates user record in database on first login.
    """
    token = credentials.credentials
    
    # Get JWT Secret from environment variables
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        logger.error("SUPABASE_JWT_SECRET not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret not configured. Please set SUPABASE_JWT_SECRET in your .env file.",
        )
    
    try:
        # Decode and verify JWT token using the JWT Secret
        # Verify signature and expiration, but skip audience and issuer verification
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,
                "verify_iss": False,
            }
        )
        
        user_id = payload.get("sub")
        user_email = payload.get("email") or ""
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Sync user to database (create if first login)
        try:
            user_repo = UserRepository(db)
            user_repo.get_or_create_user(user_id, user_email)
        except Exception as e:
            logger.error(f"Failed to sync user to database: {str(e)}", exc_info=True)
            # Don't fail authentication if user sync fails, but log the error
        
        # Return user information
        return {
            "id": user_id,
            "email": user_email,
            "sub": user_id,
            "role": "authenticated",
            "app_metadata": {},
            "user_metadata": {},
        }
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """
    Optionally verify JWT token and return user information.
    
    This dependency can be used when authentication is optional.
    Returns None if no token is provided.
    
    Example:
        @app.get("/api/optional-auth")
        async def optional_route(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                return {"user_id": user["sub"], "authenticated": True}
            return {"authenticated": False}
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

