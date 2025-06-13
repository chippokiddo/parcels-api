from typing import Optional, Tuple, List


def build_date_filter_conditions(year_filter: Optional[str] = None,
                                 month_filter: Optional[str] = None,
                                 date_field: str = 'order_date') -> Tuple[str, List]:
    """
    Build date-based query filter conditions

    Args:
        year_filter: Year to filter by (YYYY format)
        month_filter: Month to filter by (MM format)
        date_field: Name of the date field to filter on

    Returns:
        Tuple of (query_conditions, query_params)
    """
    query_conditions = ""
    query_params = []

    if year_filter:
        query_conditions += f" AND strftime('%Y', {date_field}) = ?"
        query_params.append(year_filter)

    if month_filter:
        query_conditions += f" AND strftime('%m', {date_field}) = ?"
        query_params.append(month_filter)

    return query_conditions, query_params


def build_status_filter_conditions(status_filter: Optional[str] = None,
                                   status_field: str = 'order_status') -> Tuple[str, List]:
    """
    Build status-based query filter conditions
    """
    query_conditions = ""
    query_params = []

    if status_filter:
        query_conditions += f" AND {status_field} = ?"
        query_params.append(status_filter)

    return query_conditions, query_params


def combine_filter_conditions(*conditions: Tuple[str, List]) -> Tuple[str, List]:
    """
    Combine multiple filter conditions into a single query condition and params list
    """
    all_conditions = []
    all_params = []

    for condition, params in conditions:
        if condition:
            all_conditions.append(condition)
            all_params.extend(params)

    return ''.join(all_conditions), all_params
