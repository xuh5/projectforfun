from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from supabase import Client, create_client

# Security scheme for extracting Bearer token
security = HTTPBearer()


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) must be set in environment variables"
        )
    
    return create_client(supabase_url, supabase_key)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify JWT token and return user information.
    
    This dependency can be used in FastAPI endpoints to require authentication.
    
    Example:
        @app.get("/api/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["sub"]}
    """
    token = credentials.credentials
    
    try:
        # Get Supabase client to verify token
        supabase = get_supabase_client()
        
        # Use Supabase client to get user from token
        # This verifies the token and returns user information
        try:
            user_response = supabase.auth.get_user(token)
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = user_response.user
            
            # Return user information in a consistent format
            return {
                "id": user.id,
                "email": user.email,
                "sub": user.id,  # Standard JWT claim
                "role": user.role or "authenticated",
                "app_metadata": user.app_metadata or {},
                "user_metadata": user.user_metadata or {},
            }
        except Exception as e:
            # If Supabase client verification fails, try manual JWT verification as fallback
            # This handles cases where the token format might differ
            supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_anon_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Supabase configuration error",
                )
            
            try:
                # Manual JWT verification (fallback)
                # Note: Supabase tokens are typically signed with a JWT secret, not the anon key
                # For production, consider using JWKS verification
                payload = jwt.decode(
                    token,
                    supabase_anon_key,
                    algorithms=["HS256"],
                    options={"verify_signature": True, "verify_exp": True},
                )
                
                user_id: Optional[str] = payload.get("sub")
                if user_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token: missing user ID",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                return {
                    "id": user_id,
                    "email": payload.get("email"),
                    "sub": user_id,
                    "role": payload.get("role", "authenticated"),
                    "app_metadata": payload.get("app_metadata", {}),
                    "user_metadata": payload.get("user_metadata", {}),
                }
            except JWTError as jwt_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid authentication token: {str(jwt_error)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
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
        return get_current_user(credentials)
    except HTTPException:
        return None

