from .repository import get_demo_account, save_demo_account, save_user
from .schema import AccountProfile, AccountProfileUpdate, UserCreate


def create_user(data: UserCreate) -> AccountProfile:
    return save_user(data)


def get_current_profile() -> AccountProfile:
    return get_demo_account()


def update_current_profile(data: AccountProfileUpdate) -> AccountProfile:
    return save_demo_account(data)
