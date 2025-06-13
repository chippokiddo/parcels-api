def validate_page_number(page_str, default=1):
    """
    Validate and return page number
    """
    try:
        page = int(page_str) if page_str else default
        return page if page >= 1 else default
    except ValueError:
        return default


def create_pagination_info(current_page, total_count, limit):
    """
    Create pagination information dictionary
    """
    total_pages = (total_count + limit - 1) // limit
    return {
        'current_page': current_page,
        'total_pages': total_pages,
        'total_count': total_count,
        'has_prev': current_page > 1,
        'has_next': current_page < total_pages,
        'limit': limit
    }
