from fastapi import Query


def pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, le=100, description="Number of itmes to return"),
):
    """
    Reusable dependency for pagination parameters.
    Returns a dict with 'skip' and 'limit'.
    """
    return {"skip": skip, "limit": limit}
