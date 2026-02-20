"""Query utilities for filtering, searching, and expanding relations"""
from typing import List, Optional, Any
from sqlalchemy import Select, or_, func
from sqlalchemy.orm import selectinload, joinedload


def apply_filters(query: Select, filters: dict) -> Select:
    """
    Apply filters to query dynamically

    Args:
        query: SQLAlchemy select query
        filters: Dictionary of field: value filters

    Returns:
        Modified query with filters applied
    """
    for field, value in filters.items():
        if value is not None and hasattr(query.column_descriptions[0]['entity'], field):
            model = query.column_descriptions[0]['entity']
            query = query.where(getattr(model, field) == value)

    return query


def apply_search(
    query: Select,
    model: Any,
    search_fields: List[str],
    search_term: Optional[str]
) -> Select:
    """
    Apply text search across multiple fields

    Args:
        query: SQLAlchemy select query
        model: SQLAlchemy model class
        search_fields: List of field names to search in
        search_term: Search term

    Returns:
        Modified query with search applied
    """
    if not search_term:
        return query

    search_conditions = []
    for field in search_fields:
        if hasattr(model, field):
            search_conditions.append(
                func.lower(getattr(model, field)).contains(search_term.lower())
            )

    if search_conditions:
        query = query.where(or_(*search_conditions))

    return query


def apply_ordering(query: Select, model: Any, ordering: Optional[str]) -> Select:
    """
    Apply ordering to query

    Args:
        query: SQLAlchemy select query
        model: SQLAlchemy model class
        ordering: Ordering string (e.g., '-created_at' for descending)

    Returns:
        Modified query with ordering applied
    """
    if not ordering:
        return query

    # Handle descending order (prefix with -)
    if ordering.startswith('-'):
        field_name = ordering[1:]
        descending = True
    else:
        field_name = ordering
        descending = False

    if hasattr(model, field_name):
        field = getattr(model, field_name)
        query = query.order_by(field.desc() if descending else field.asc())

    return query


def apply_expansion(
    query: Select,
    model: Any,
    expand_fields: List[str]
) -> Select:
    """
    Apply eager loading for specified relationships

    Args:
        query: SQLAlchemy select query
        model: SQLAlchemy model class
        expand_fields: List of relationship names to expand

    Returns:
        Modified query with eager loading applied

    Examples:
        expand_fields = ['poste', 'user_account']
        expand_fields = ['poste.service', 'poste.group']
        expand_fields = ['user.employe.poste']
    """
    if not expand_fields:
        return query

    # Process each expand field independently
    for field in expand_fields:
        if '.' not in field:
            # Simple expansion like 'poste'
            if hasattr(model, field):
                query = query.options(selectinload(getattr(model, field)))
        else:
            # Nested expansion like 'poste.service' or 'user.employe.poste'
            parts = field.split('.')

            # Build the loader chain from the parts
            current_model = model
            loader = None

            for i, part in enumerate(parts):
                if hasattr(current_model, part):
                    attr = getattr(current_model, part)

                    if i == 0:
                        # First level
                        loader = selectinload(attr)
                    else:
                        # Subsequent levels
                        loader = loader.selectinload(attr)

                    # Get the related model for next iteration
                    if hasattr(attr.property, 'mapper'):
                        current_model = attr.property.mapper.class_
                else:
                    # Attribute doesn't exist, skip this expansion
                    break

            # Apply the complete loader chain
            if loader is not None:
                query = query.options(loader)

    return query


def parse_expand_param(expand: Optional[str]) -> List[str]:
    """
    Parse expand query parameter into list of fields

    Args:
        expand: Comma-separated string of fields to expand

    Returns:
        List of field names

    Example:
        'poste_id,user_account' -> ['poste_id', 'user_account']
    """
    if not expand:
        return []

    return [field.strip() for field in expand.split(',') if field.strip()]
