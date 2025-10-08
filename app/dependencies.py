from fastapi import Query, HTTPException
from typing import Literal, Optional


# soritng dependency
def sorting_params(
    sort_by: str = Query("id", description="sorting field"),
    order: Literal["asc", "desc"] = Query("asc", description="sorting order"),
):
    """Return validated sorting parameters."""
    valid_fields = ["id", "title", "priority", "completed"]
    if sort_by.lower() not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")
    return {"sort_by": sort_by, "order": order}


# pagination dependency
def pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, le=100, description="Number of itmes to return"),
):
    """
    Reusable dependency for pagination parameters.
    Returns a dict with 'skip' and 'limit'.
    """
    return {"skip": skip, "limit": limit}


# filtering dependency
def filtering_params(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[int] = Query(None, description="Filtering by priority"),
    title: Optional[str] = Query(None, description="Filtering by title"),
):
    """
    Reusable dependency for filtering Task objects.
    Returns a dictionary of non-null filters.
    """
    filters = {}
    if completed is not None:
        filters["completed"] = completed
    if priority is not None:
        filters["priority"] = priority
    if title is not None:
        filters["title"] = title

    return filters
