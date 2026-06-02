"""Regression tests for top-level API router prefixes."""

from app.api.router import api_router


def test_api_router_includes_expected_module_prefixes() -> None:
    paths = [route.path for route in api_router.routes]

    assert any(path.startswith("/accounts") for path in paths)
    assert any(path.startswith("/jobs") for path in paths)
    assert any(path.startswith("/matching") for path in paths)
    assert any(path.startswith("/tracking") for path in paths)
    assert any(path.startswith("/search") for path in paths)
