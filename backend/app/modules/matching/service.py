from __future__ import annotations

import math
import re
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status

from app.core.supabase_client import get_supabase_service_client


class MatchingService:
    """AI-assisted matching backed by the canonical Supabase contract tables."""

    _token_pattern = re.compile(r"[a-z0-9+#.]+")

    def __init__(self) -> None:
        self._embedding_model: Any | None = None
        self._embedding_util: Any | None = None
        self._embedding_checked = False

    def _client(self):
        return get_supabase_service_client()

    def _safe_list(self, value: Any) -> list[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value).strip()]

    def _tokens(self, text: str) -> set[str]:
        return set(self._token_pattern.findall(text.lower()))

    def _semantic_similarity(self, left: str, right: str) -> float:
        """
        Prefer sentence-transformers when installed; fall back to a deterministic
        cosine score so matching endpoints remain operational in lean installs.
        """
        if not left.strip() or not right.strip():
            return 0.0

        if not self._embedding_checked:
            self._embedding_checked = True
            try:
                from sentence_transformers import SentenceTransformer, util

                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                self._embedding_util = util
            except ImportError:
                self._embedding_model = None
                self._embedding_util = None

        if self._embedding_model is not None and self._embedding_util is not None:
            embeddings = self._embedding_model.encode(
                [left, right],
                convert_to_tensor=True,
            )
            score = self._embedding_util.cos_sim(embeddings[0], embeddings[1]).item()
            return round(max(0.0, min(float(score), 1.0)), 4)

        left_tokens = self._tokens(left)
        right_tokens = self._tokens(right)
        if not left_tokens or not right_tokens:
            return 0.0

        overlap = len(left_tokens & right_tokens)
        score = overlap / math.sqrt(len(left_tokens) * len(right_tokens))
        return round(max(0.0, min(score, 1.0)), 4)

    def _candidate_skills(self, candidate_id: UUID | str) -> list[str]:
        client = self._client()
        join_response = (
            client.table("job_seeker_skills")
            .select("skill_id")
            .eq("job_seeker_id", str(candidate_id))
            .execute()
        )
        skill_ids = [row["skill_id"] for row in (join_response.data or []) if row.get("skill_id")]
        if not skill_ids:
            return []

        skill_response = client.table("skills").select("name").in_("id", skill_ids).execute()
        return [row["name"] for row in (skill_response.data or []) if row.get("name")]

    def _candidate_profile(self, user_id: UUID | str) -> dict[str, Any]:
        response = (
            self._client()
            .table("job_seekers")
            .select("id, first_name, last_name, education, major, academic_units, years_of_experience, is_active")
            .eq("id", str(user_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job seeker profile not found")

        candidate = rows[0]
        candidate["skills"] = self._candidate_skills(candidate["id"])
        return candidate

    def _published_jobs(self) -> list[dict[str, Any]]:
        response = (
            self._client()
            .table("jobs")
            .select("id, employer_id, title, description, required_skills, location, work_mode, experience_required, status, created_at")
            .eq("status", "published")
            .execute()
        )
        return response.data or []

    def _job(self, job_id: UUID | str) -> dict[str, Any]:
        response = (
            self._client()
            .table("jobs")
            .select("id, employer_id, title, description, required_skills, location, work_mode, experience_required, status, created_at")
            .eq("id", str(job_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return rows[0]

    def _candidates(self) -> list[dict[str, Any]]:
        response = (
            self._client()
            .table("job_seekers")
            .select("id, first_name, last_name, education, major, academic_units, years_of_experience, is_active")
            .execute()
        )
        candidates = response.data or []
        for candidate in candidates:
            candidate["skills"] = self._candidate_skills(candidate["id"])
        return candidates

    def _ensure_job_owner(self, job: dict[str, Any], user_id: UUID) -> None:
        if str(job.get("employer_id")) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the employer that owns this job can view candidate matches",
            )

    def _candidate_text(self, candidate: dict[str, Any]) -> str:
        return " ".join(
            [
                " ".join(self._safe_list(candidate.get("skills"))),
                str(candidate.get("education") or ""),
                str(candidate.get("major") or ""),
                " ".join(self._safe_list(candidate.get("academic_units"))),
            ]
        )

    def _job_text(self, job: dict[str, Any]) -> str:
        return " ".join(
            [
                str(job.get("title") or ""),
                str(job.get("description") or ""),
                " ".join(self._safe_list(job.get("required_skills"))),
                str(job.get("location") or ""),
                str(job.get("work_mode") or ""),
            ]
        )

    def calculate_skill_score(self, candidate_skills: Any, job_skills: Any) -> float:
        candidate_text = " ".join(self._safe_list(candidate_skills))
        job_text = " ".join(self._safe_list(job_skills))
        return self._semantic_similarity(candidate_text, job_text)

    def calculate_profile_score(self, candidate: dict[str, Any], job: dict[str, Any]) -> float:
        return self._semantic_similarity(self._candidate_text(candidate), self._job_text(job))

    def calculate_experience_score(self, candidate: dict[str, Any], job: dict[str, Any]) -> float:
        candidate_exp = candidate.get("years_of_experience") or 0
        required_exp = job.get("experience_required") or 0
        if required_exp <= 0:
            return 1.0
        return round(min(float(candidate_exp) / float(required_exp), 1.0), 4)

    def calculate_total_score(self, candidate: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        skill_score = self.calculate_skill_score(
            candidate.get("skills", []),
            job.get("required_skills", []),
        )
        profile_score = self.calculate_profile_score(candidate, job)
        experience_score = self.calculate_experience_score(candidate, job)
        total_score = (0.6 * skill_score) + (0.3 * profile_score) + (0.1 * experience_score)

        return {
            "score": round(total_score, 4),
            "breakdown": {
                "skill": skill_score,
                "profile": profile_score,
                "experience": experience_score,
            },
        }

    def _recommendation_payload(self, candidate: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        result = self.calculate_total_score(candidate, job)
        return {
            "job_id": job["id"],
            "title": job["title"],
            "location": job.get("location"),
            "work_mode": job.get("work_mode"),
            "required_skills": job.get("required_skills") or [],
            "score": result["score"],
            "breakdown": result["breakdown"],
        }

    def get_job_recommendations(self, user_id: UUID) -> list[dict[str, Any]]:
        candidate = self._candidate_profile(user_id)
        results = [self._recommendation_payload(candidate, job) for job in self._published_jobs()]
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:10]

    def get_candidate_recommendations(self, job_id: UUID, user_id: UUID) -> list[dict[str, Any]]:
        job = self._job(job_id)
        self._ensure_job_owner(job, user_id)

        results = []
        for candidate in self._candidates():
            result = self.calculate_total_score(candidate, job)
            results.append(
                {
                    "candidate_id": candidate["id"],
                    "name": f"{candidate.get('first_name') or ''} {candidate.get('last_name') or ''}".strip(),
                    "skills": candidate.get("skills") or [],
                    "score": result["score"],
                    "breakdown": result["breakdown"],
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:10]

    def get_match_explanation(self, match_id: UUID, user_id: UUID) -> dict[str, Any]:
        response = (
            self._client()
            .table("matches")
            .select("id, job_id, job_seeker_id, score, breakdown_json")
            .eq("id", str(match_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

        match = rows[0]
        job = self._job(match["job_id"])
        is_candidate_owner = str(match.get("job_seeker_id")) == str(user_id)
        is_employer_owner = str(job.get("employer_id")) == str(user_id)
        if not is_candidate_owner and not is_employer_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this match")

        return {
            "match_id": match["id"],
            "job_id": match["job_id"],
            "job_seeker_id": match["job_seeker_id"],
            "score": float(match["score"] or 0),
            "breakdown": match.get("breakdown_json") or {},
        }

    def _upsert_matches(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        self._client().table("matches").upsert(
            rows,
            on_conflict="job_id,job_seeker_id",
        ).execute()
        return len(rows)

    def recompute_matches(self, user_id: UUID, job_id: UUID | None = None) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []

        if job_id is not None:
            job = self._job(job_id)
            self._ensure_job_owner(job, user_id)
            for candidate in self._candidates():
                result = self.calculate_total_score(candidate, job)
                rows.append(
                    {
                        "job_id": job["id"],
                        "job_seeker_id": candidate["id"],
                        "score": result["score"],
                        "breakdown_json": result["breakdown"],
                    }
                )
        else:
            candidate = self._candidate_profile(user_id)
            for job in self._published_jobs():
                result = self.calculate_total_score(candidate, job)
                rows.append(
                    {
                        "job_id": job["id"],
                        "job_seeker_id": candidate["id"],
                        "score": result["score"],
                        "breakdown_json": result["breakdown"],
                    }
                )

        return {
            "status": "recomputed",
            "matches_updated": self._upsert_matches(rows),
            "job_id": str(job_id) if job_id else None,
            "user_id": str(user_id),
        }
