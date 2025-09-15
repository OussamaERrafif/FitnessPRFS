# Test Failures Analysis and Solutions

## 1. 403 Forbidden vs 401 Unauthorized
- **Cause:**
  - Many tests expect a 401 Unauthorized response for unauthenticated requests, but the API returns 403 Forbidden. This is likely due to the authentication/authorization middleware or dependency raising 403 instead of 401 when credentials are missing or invalid.
- **Solution:**
  - Review authentication dependencies (e.g., FastAPI's `Depends(get_current_user)`) and ensure they raise `HTTPException(status_code=401)` for missing/invalid credentials.
  - Update tests to expect 403 if this is the intended behavior, or update the code to return 401 if that is correct per your API design.

## 2. 404 Not Found or 422 Unprocessable Entity for `/api/v1/v1/...` Endpoints
- **Cause:**
  - Tests are calling endpoints like `/api/v1/v1/trainers/`, but these do not exist (404) or are misconfigured (422). This suggests a possible typo or incorrect route registration in the API or in the tests.
- **Solution:**
  - Check your route registration in FastAPI. Ensure you are not double-prefixing with `/v1`.
  - Update tests to use the correct endpoint paths (e.g., `/api/v1/trainers/` instead of `/api/v1/v1/trainers/`).

## 3. OpenAPI Schema/Endpoint Coverage Failures
- **Cause:**
  - Tests expect certain endpoints (like trainers, exercises, programs, meals) to be present in the OpenAPI schema, but they are missing.
- **Solution:**
  - Ensure all routers are included in your FastAPI app and registered with the correct prefixes.
  - Check for typos or missing imports in your `main.py` or wherever routers are included.

## 4. SQLAlchemy `InvalidRequestError` for 'CancellationPolicy'
- **Cause:**
  - The `Trainer` model references a class or table `CancellationPolicy` in a relationship, but this class is not defined or not imported.
- **Solution:**
  - Define the `CancellationPolicy` model in `app/models/cancellation.py` (or the appropriate file).
  - Import `CancellationPolicy` in `trainer.py` or wherever the relationship is declared.
  - Ensure all models are imported in `app/models/__init__.py` if using automap or similar.

## 5. Error Handling Tests Expecting 404, Getting 403
- **Cause:**
  - Tests for non-existent endpoints expect 404, but the API returns 403, likely due to authentication middleware intercepting the request before the route handler.
- **Solution:**
  - Adjust middleware to allow 404 for non-existent endpoints, or update tests to expect 403 if this is the intended behavior.

## 6. Endpoint Category Coverage (e.g., Trainer Management endpoints not found)
- **Cause:**
  - The OpenAPI schema does not list endpoints for some categories, likely due to missing router registration or import errors.
- **Solution:**
  - Ensure all routers are registered in the FastAPI app.
  - Check for import errors or typos in router files.

---

**General Recommendations:**
- Review all route registrations and ensure consistency in endpoint paths.
- Ensure all models referenced in relationships are defined and imported.
- Decide on consistent error codes for authentication/authorization and update both code and tests accordingly.
- Rerun tests after each fix to verify progress.
