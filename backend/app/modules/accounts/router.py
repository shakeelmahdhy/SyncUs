from fastapi import APIRouter, status

from .schema import AccountProfile, AccountProfileUpdate, UserCreate
from .service import create_user, get_current_profile, update_current_profile


router = APIRouter(prefix="/skill-sync/v1/accounts", tags=["accounts"])


@router.post(
    "",
    response_model=AccountProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Create account profile",
)
def register_user(user: UserCreate) -> AccountProfile:
    return create_user(user)


@router.get(
    "/me",
    response_model=AccountProfile,
    summary="Get current account profile",
)
def get_my_profile() -> AccountProfile:
    return get_current_profile()


@router.put(
    "/me",
    response_model=AccountProfile,
    summary="Update current account profile",
)
def update_my_profile(profile: AccountProfileUpdate) -> AccountProfile:
    return update_current_profile(profile)
