from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.role_guard import require_roles
from app.models.user import UserRole


def test_admin_role_guard_allows_admin():
    dependency = require_roles(UserRole.ADMIN)
    user = SimpleNamespace(role=UserRole.ADMIN)

    assert dependency.__wrapped__(user) if hasattr(dependency, "__wrapped__") else dependency(user) is user


def test_employee_role_guard_rejects_employee():
    dependency = require_roles(UserRole.ADMIN)
    user = SimpleNamespace(role=UserRole.EMPLOYEE)

    with pytest.raises(HTTPException) as exc:
        dependency(user)

    assert exc.value.status_code == 403


def test_auditor_role_guard_allows_auditor():
    dependency = require_roles(UserRole.ADMIN, UserRole.AUDITOR)
    user = SimpleNamespace(role=UserRole.AUDITOR)

    assert dependency(user) is user
