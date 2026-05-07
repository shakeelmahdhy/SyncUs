from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os


# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# HTTP Bearer token authentication
security = HTTPBearer()


def get_supabase_client() -> Client:
    """
    Get Supabase client instance

    Returns:
        Supabase client

    Raises:
        HTTPException: If Supabase credentials are not configured
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing"
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> dict:

    try:
        token = credentials.credentials

        # Verify JWT token with Supabase
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        user = user_response.user

        # Get user profile with role information
        profile_response = supabase.table('user_profiles').select('*').eq(
            'id', user.id
        ).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        profile = profile_response.data[0]

        return {
            'id': user.id,
            'email': user.email,
            'role': profile.get('role'),
            'profile': profile
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_current_employer(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if current_user.get('role') != 'employer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employers"
        )

    return current_user


async def get_current_candidate(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if current_user.get('role') != 'candidate':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to job seekers"
        )

    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> Optional[dict]:

    if not credentials:
        return None

    try:
        return await get_current_user(credentials, supabase)
    except HTTPException:
        return None
