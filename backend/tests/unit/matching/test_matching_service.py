"""Regression tests for matching service schema compatibility."""

from __future__ import annotations

from uuid import UUID

from app.modules.matching.service import MatchingService


class _Response:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, client: "_FakeClient", table_name: str):
        self.client = client
        self.table_name = table_name
        self.filters: list[tuple[str, str]] = []
        self.in_filters: list[tuple[str, set[str]]] = []
        self.limit_count: int | None = None
        self.operation = "select"
        self.payload = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column: str, value):
        self.filters.append((column, str(value)))
        return self

    def in_(self, column: str, values):
        self.in_filters.append((column, {str(value) for value in values}))
        return self

    def limit(self, count: int):
        self.limit_count = count
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def execute(self):
        return self.client.execute(self)


class _FakeClient:
    def __init__(self, tables):
        self.tables = tables

    def table(self, table_name: str):
        return _Query(self, table_name)

    def execute(self, query: _Query):
        rows = self.tables.setdefault(query.table_name, [])
        if query.operation == "insert":
            rows.append(dict(query.payload))
            return _Response([query.payload])

        matched = []
        for row in rows:
            if all(str(row.get(column)) == value for column, value in query.filters) and all(
                str(row.get(column)) in values for column, values in query.in_filters
            ):
                matched.append(row)

        if query.operation == "update":
            for row in matched:
                row.update(query.payload)
            return _Response(matched)

        if query.limit_count is not None:
            matched = matched[: query.limit_count]
        return _Response(matched)


def test_candidate_profile_resolves_by_user_id_and_merges_skills() -> None:
    auth_user_id = UUID("11111111-1111-1111-1111-111111111111")
    profile_id = "22222222-2222-2222-2222-222222222222"
    skill_id = "33333333-3333-3333-3333-333333333333"
    service = MatchingService(
        _FakeClient(
            {
                "job_seekers": [
                    {
                        "id": profile_id,
                        "user_id": str(auth_user_id),
                        "first_name": "Ava",
                        "last_name": "Singh",
                        "skills": ["Python", "SQL"],
                    }
                ],
                "job_seeker_skills": [
                    {"job_seeker_id": profile_id, "skill_id": skill_id}
                ],
                "skills": [{"id": skill_id, "name": "FastAPI"}],
            }
        )
    )

    profile = service._candidate_profile(auth_user_id)

    assert profile["id"] == profile_id
    assert profile["skills"] == ["Python", "SQL", "FastAPI"]


def test_match_persistence_updates_existing_pair_without_unique_constraint() -> None:
    job_id = "44444444-4444-4444-4444-444444444444"
    first_candidate_id = "55555555-5555-5555-5555-555555555555"
    second_candidate_id = "66666666-6666-6666-6666-666666666666"
    tables = {
        "matches": [
            {
                "id": "77777777-7777-7777-7777-777777777777",
                "job_id": job_id,
                "job_seeker_id": first_candidate_id,
                "score": 0.2,
                "breakdown_json": {"skill": 0.2},
            }
        ]
    }
    service = MatchingService(_FakeClient(tables))

    updated = service._upsert_matches(
        [
            {
                "job_id": job_id,
                "job_seeker_id": first_candidate_id,
                "score": 0.9,
                "breakdown_json": {"skill": 1.0},
            },
            {
                "job_id": job_id,
                "job_seeker_id": second_candidate_id,
                "score": 0.7,
                "breakdown_json": {"skill": 0.7},
            },
        ]
    )

    assert updated == 2
    assert len(tables["matches"]) == 2
    assert tables["matches"][0]["score"] == 0.9
    assert tables["matches"][0]["breakdown_json"] == {"skill": 1.0}
    assert tables["matches"][1]["job_seeker_id"] == second_candidate_id


def test_skill_score_rewards_required_skill_coverage() -> None:
    service = MatchingService(_FakeClient({}))

    assert service.calculate_skill_score(["Python", "React"], ["python"]) == 1.0
    assert service.calculate_skill_score([], ["python"]) == 0.0
    assert service.calculate_skill_score(["Python"], []) == 1.0


def test_work_mode_score_accepts_profile_work_mode_alias() -> None:
    service = MatchingService(_FakeClient({}))

    assert service.calculate_work_mode_score({"work_mode": "Remote"}, {"work_mode": "remote"}) == 1.0
    assert service.calculate_work_mode_score({"working_preferences": "Hybrid work"}, {"work_mode": "hybrid"}) == 1.0
    assert service.calculate_work_mode_score({"work_mode": "onsite"}, {"work_mode": "remote"}) == 0.0
