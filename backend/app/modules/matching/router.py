from uuid import UUID

from fastapi import APIRouter, Query

from app.core.auth import CurrentUserIdDep
from app.modules.matching.service import MatchingService

router = APIRouter()

_service: MatchingService | None = None


def _matching_service() -> MatchingService:
    """Lazy singleton so app startup does not load sentence-transformers."""
    global _service
    if _service is None:
        _service = MatchingService()
    return _service


@router.get("/recommendations")
def get_job_recommendations(user_id: CurrentUserIdDep):
    """Return the top job recommendations for the authenticated candidate."""
    return _matching_service().get_job_recommendations(user_id)


@router.get("/jobs/{job_id}/candidates")
def get_candidate_recommendations(job_id: UUID, user_id: CurrentUserIdDep):
    """Return the top candidate matches for a job owned by the authenticated employer."""
    return _matching_service().get_candidate_recommendations(job_id, user_id)


@router.get("/explanations/{match_id}")
def get_match_explanation(match_id: UUID, user_id: CurrentUserIdDep):
    """Return an authorized match score breakdown."""
    return _matching_service().get_match_explanation(match_id, user_id)


@router.post("/recompute")
def recompute_matches(
    user_id: CurrentUserIdDep,
    job_id: UUID | None = Query(None),
):
    """Recompute matches for the authenticated user or one owned job."""
    return _matching_service().recompute_matches(user_id, job_id)
