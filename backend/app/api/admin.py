"""Admin-gated endpoints.

For S10 only ``/admin/ping`` exists; it proves the RBAC middleware
blocks non-admins with a 403 and admits admins with a 200. The full
admin API (applications queue, users/roles, payments, KPIs) lands with
the admin dashboard work in slice S26.
"""

from fastapi import APIRouter, Depends

from app.api.deps import requires_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
def admin_ping(
    user: User = Depends(requires_role(UserRole.admin)),
) -> dict:
    """Liveness check, admin-only.

    Used by BUILD_PLAN S10 to prove role gating works end to end.
    """
    return {"ok": True, "email": user.email}
