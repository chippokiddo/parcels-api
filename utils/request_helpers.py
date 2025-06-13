def extract_filters(request):
    """
    Extract common filter parameters from request
    """
    return {
        'status_filter': request.args.get('status'),
        'year_filter': request.args.get('year'),
        'month_filter': request.args.get('month')
    }


def extract_form_data(request, fields):
    """
    Extract and strip form data for specified fields
    """
    return {
        field: request.form.get(field, '').strip()
        for field in fields
    }


def validate_required_fields(data, required_fields):
    """
    Return list of missing required fields
    """
    return [field for field in required_fields if not data.get(field)]
