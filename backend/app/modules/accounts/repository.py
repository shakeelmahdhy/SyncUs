from .schema import AccountProfile, AccountProfileUpdate, UserCreate


_DEMO_ACCOUNT_ID = 1
_accounts: dict[int, AccountProfile] = {
    _DEMO_ACCOUNT_ID: AccountProfile(
        id=_DEMO_ACCOUNT_ID,
        first_name="Alex",
        last_name="Johnson",
        email="alex.johnson@email.com",
        phone="+61 400 000 000",
        location="Sydney, NSW, Australia",
        title="Senior Product Designer",
        experience="5+ years",
        bio=(
            "Passionate product designer with 5+ years of experience creating "
            "intuitive digital experiences. Specialised in design systems and user research."
        ),
        linkedin="linkedin.com/in/alexjohnson",
        portfolio="alexjohnson.design",
        education="Bachelor of Design, University of Sydney, 2019",
        company="Freelance",
        skills=["Figma", "User Research", "Prototyping", "Design Systems"],
    )
}


def get_demo_account() -> AccountProfile:
    return _accounts[_DEMO_ACCOUNT_ID]


def save_demo_account(data: AccountProfileUpdate) -> AccountProfile:
    profile = AccountProfile(id=_DEMO_ACCOUNT_ID, **data.model_dump())
    _accounts[_DEMO_ACCOUNT_ID] = profile
    return profile


def save_user(data: UserCreate) -> AccountProfile:
    name_parts = data.name.split(maxsplit=1)
    profile = AccountProfile(
        id=_DEMO_ACCOUNT_ID,
        first_name=name_parts[0] if name_parts else "",
        last_name=name_parts[1] if len(name_parts) > 1 else "",
        email=data.email,
    )
    _accounts[_DEMO_ACCOUNT_ID] = profile
    return profile
