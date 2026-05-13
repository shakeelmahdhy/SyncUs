"""
Application status transition rules for the tracking module.

Used by the service layer before persisting a PATCH; routers stay unaware.
Same-status updates are treated as allowed no-ops.
"""

from __future__ import annotations

from .schema import ApplicationStatus


#define which next statuses are allowed from a certain status
#for example, an applied application can only be shortlisted, interviewed, rejected, or withdrawn
#rejected and withdrawn are terminal states, so they cannot be transitioned to any other status
_ALLOWED: dict[ApplicationStatus, frozenset[ApplicationStatus]] = {
    "applied": frozenset(
        {"shortlisted", "interview", "rejected", "withdrawn"}
    ),
    "shortlisted": frozenset({"interview", "offered", "rejected", "withdrawn"}),
    "interview": frozenset({"offered", "rejected", "withdrawn"}),
    "offered": frozenset({"rejected", "withdrawn"}),
    "rejected": frozenset(),
    "withdrawn": frozenset(),
}


def can_transition(from_status: ApplicationStatus, to_status: ApplicationStatus) -> bool:
    """Return True if moving from `from_status` to `to_status` is allowed (including no-op)."""
    if from_status == to_status:
        return True
    return to_status in _ALLOWED.get(from_status, frozenset())
