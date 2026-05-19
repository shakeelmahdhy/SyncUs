from fastapi import APIRouter, Query

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
def get_job_recommendations(user_id: str = Query(...)):
    """Returns Top-K (10) job recommendations for a candidate."""
    return _matching_service().get_job_recommendations(user_id)


@router.get("/jobs/{job_id}/candidates")
def get_candidate_recommendations(job_id: str):
    """Returns Top-N (10) candidates for a job."""
    return _matching_service().get_candidate_recommendations(job_id)


@router.get("/explanations/{match_id}")
def get_match_explanation(match_id: str):
    """Returns score breakdown for explainability."""
    return _matching_service().get_match_explanation(match_id)


@router.post("/recompute")
def recompute_matches(
    user_id: str = Query(None),
    job_id: str = Query(None),
):
    """Force recomputation of matches."""
    return _matching_service().recompute_matches(user_id, job_id)
