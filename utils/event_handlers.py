def handle_route_error(e, context, logger, default_message="An error occurred"):
    """
    Standardized error handling for routes
    """
    logger.error(f"Error in {context}: {str(e)}", exc_info=True)
    return default_message, 500


def handle_api_error(e, context, logger, default_message="Server error occurred"):
    """
    Standardized error handling for API endpoints
    """
    logger.error(f"Error in {context}: {str(e)}", exc_info=True)
    return error_response(default_message)
