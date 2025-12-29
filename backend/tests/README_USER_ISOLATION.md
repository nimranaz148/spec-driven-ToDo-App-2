# User Isolation Tests - Quick Guide

## Overview

This test suite (`test_user_isolation.py`) contains 24 comprehensive tests that verify user data isolation across all task endpoints.

## Test Setup

The tests use fixtures to create two users (User A and User B) and verify they cannot access each other's tasks.

### Fixtures

- `user_a_auth`: Registers/authenticates User A, returns token and user_id
- `user_b_auth`: Registers/authenticates User B, returns token and user_id
- `user_a_task`: Creates a task for User A
- `user_b_task`: Creates a task for User B

## Running Tests

### Run All Isolation Tests
```bash
cd backend
pytest tests/test_user_isolation.py -v
```

### Run Specific Test Category
```bash
# List isolation tests
pytest tests/test_user_isolation.py -k "list" -v

# Get isolation tests
pytest tests/test_user_isolation.py -k "get" -v

# Update isolation tests
pytest tests/test_user_isolation.py -k "update" -v

# Delete isolation tests
pytest tests/test_user_isolation.py -k "delete" -v

# Toggle completion isolation tests
pytest tests/test_user_isolation.py -k "toggle" -v

# URL path manipulation tests
pytest tests/test_user_isolation.py -k "path" -v
```

### Run Single Test
```bash
pytest tests/test_user_isolation.py::test_user_a_cannot_list_user_b_tasks -v
```

### Run with Coverage
```bash
pytest tests/test_user_isolation.py --cov=src.routes.tasks --cov=src.services.task_service --cov-report=html
```

## Test Coverage

### 1. List Isolation (2 tests)
- `test_user_a_cannot_list_user_b_tasks`: User A's list doesn't include User B's tasks
- `test_user_b_cannot_list_user_a_tasks`: User B's list doesn't include User A's tasks

### 2. Get Isolation (2 tests)
- `test_user_a_cannot_get_user_b_task_returns_404`: Returns 404 (security)
- `test_user_b_cannot_get_user_a_task_returns_404`: Returns 404 (security)

### 3. Update Isolation (3 tests)
- `test_user_a_cannot_update_user_b_task_returns_404`: Returns 404 (security)
- `test_user_b_cannot_update_user_a_task_returns_404`: Returns 404 (security)
- `test_update_does_not_modify_other_users_task`: Verify no modification occurs

### 4. Delete Isolation (3 tests)
- `test_user_a_cannot_delete_user_b_task_returns_404`: Returns 404 (security)
- `test_user_b_cannot_delete_user_a_task_returns_404`: Returns 404 (security)
- `test_delete_does_not_remove_other_users_task`: Verify task still exists

### 5. Toggle Completion Isolation (3 tests)
- `test_user_a_cannot_toggle_user_b_task_completion_returns_404`: Returns 404 (security)
- `test_user_b_cannot_toggle_user_a_task_completion_returns_404`: Returns 404 (security)
- `test_toggle_does_not_modify_other_users_task`: Verify no modification occurs

### 6. URL Path Manipulation (6 tests)
- `test_list_tasks_with_wrong_user_id_in_path_returns_403`: Blocks URL manipulation
- `test_create_task_with_wrong_user_id_in_path_returns_403`: Blocks URL manipulation
- `test_get_task_with_wrong_user_id_in_path_returns_403`: Blocks URL manipulation
- `test_update_task_with_wrong_user_id_in_path_returns_403`: Blocks URL manipulation
- `test_delete_task_with_wrong_user_id_in_path_returns_403`: Blocks URL manipulation
- `test_toggle_task_with_wrong_user_id_in_path_returns_403`: Blocks URL manipulation

### 7. JWT Validation (2 tests)
- `test_jwt_user_id_extraction_is_correct`: Verify JWT user_id matches task owner
- `test_all_operations_filter_by_jwt_user_id`: Comprehensive JWT filtering test

### 8. Edge Cases (3 tests)
- `test_nonexistent_task_returns_404_not_different_error`: Same error as unauthorized access
- `test_multiple_users_see_only_their_own_tasks`: Multi-user isolation verification

## Security Principles Tested

### 1. Defense in Depth
- JWT authentication required (401 if missing/invalid)
- Path parameter validation (403 if user_id mismatch)
- Database query filtering (404 if task not owned)

### 2. Information Security
- Returns **404** when task belongs to another user (not 403)
- Prevents task ID enumeration
- Doesn't reveal task existence to unauthorized users

### 3. Attack Scenario Coverage
- Direct task ID guessing
- URL path manipulation
- Create task for another user
- Update another user's task
- Delete another user's task
- Token theft/replay

## Expected Results

All tests should **PASS** because the implementation correctly:

1. Extracts `user_id` from JWT token
2. Validates path parameter matches JWT `user_id` (403 if not)
3. Filters all database queries by authenticated `user_id`
4. Returns 404 when task doesn't exist or belongs to another user

## Troubleshooting

### Test Fails: User Can Access Other User's Task

**Symptom**: Test expects 404 but gets 200 with task data

**Cause**: Database query not filtering by user_id

**Fix**: Verify `task_service.py` queries include `Task.user_id == user_id`

### Test Fails: Wrong Status Code (403 instead of 404)

**Symptom**: Test expects 404 but gets 403

**Cause**: Path validation error message instead of database lookup

**Fix**: Ensure path user_id matches JWT user_id (403 is correct for path mismatch)

### Test Fails: Authentication Error

**Symptom**: Tests fail with 401 Unauthorized

**Cause**: JWT token not generated or expired

**Fix**: Check `user_a_auth` and `user_b_auth` fixtures return valid tokens

## Dependencies

Required packages (from `pyproject.toml`):
- pytest >= 8.0.0
- pytest-asyncio >= 0.24.0
- httpx >= 0.28.0
- fastapi >= 0.115.0
- sqlmodel >= 0.0.24

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

## Integration with CI/CD

Add to GitHub Actions workflow:
```yaml
- name: Run User Isolation Tests
  run: |
    cd backend
    pytest tests/test_user_isolation.py -v --cov=src --cov-report=xml
```

## Related Files

- `backend/src/routes/tasks.py`: Task endpoints with isolation logic
- `backend/src/services/task_service.py`: Database queries with user_id filtering
- `backend/src/auth.py`: JWT authentication and user_id extraction
- `backend/tests/conftest.py`: Test fixtures and database setup
- `backend/USER_ISOLATION_ANALYSIS.md`: Detailed security analysis

## Security Audit Checklist

- [ ] All endpoints require JWT authentication
- [ ] JWT user_id extracted correctly
- [ ] Path parameter validation implemented
- [ ] Database queries filter by user_id
- [ ] Returns 404 (not 403) for unauthorized task access
- [ ] Returns 403 for URL path manipulation
- [ ] No information leakage about task IDs
- [ ] All 24 isolation tests pass

## Support

If tests fail, refer to:
1. `USER_ISOLATION_ANALYSIS.md` for implementation details
2. `backend/CLAUDE.md` for project conventions
3. `specs/api/endpoints.md` for API specifications

---

**Test Suite Status**: Ready for execution
**Security Status**: Production-ready implementation
**Total Tests**: 24 comprehensive isolation tests
