from uuid import UUID

from fastapi import APIRouter, Query

from app.core.auth import CandidateUserDep, CurrentUserDep, EmployerUserDep
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
def get_job_recommendations(current_candidate: CandidateUserDep):
    """Return the top job recommendations for the authenticated candidate."""
    return _matching_service().get_job_recommendations(current_candidate.sub)


@router.get("/jobs/{job_id}/candidates")
def get_candidate_recommendations(job_id: UUID, current_employer: EmployerUserDep):
    """Return the top candidate matches for a job owned by the authenticated employer."""
    return _matching_service().get_candidate_recommendations(job_id, current_employer.sub)


@router.get("/explanations/{match_id}")
def get_match_explanation(match_id: UUID, current_user: CurrentUserDep):
    """Return an authorized match score breakdown."""
    return _matching_service().get_match_explanation(match_id, current_user.sub)


@router.post("/recompute")
def recompute_matches(
    current_user: CurrentUserDep,
    job_id: UUID | None = Query(None),
):
    """Recompute matches for the authenticated user or one owned job."""
    return _matching_service().recompute_matches(current_user.sub, job_id)
