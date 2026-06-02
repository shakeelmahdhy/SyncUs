"""Regression tests for jobs route matching order."""

from app.modules.jobs.router import router


def test_static_jobs_routes_are_registered_before_dynamic_job_id() -> None:
    paths = [route.path for route in router.routes]

    dynamic_index = paths.index("/{job_id}")

    assert paths.index("/employer/my-jobs") < dynamic_index
    assert paths.index("/stats/overview") < dynamic_index
