from .response_helpers import error_response


def handle_route_error(e, context, logger, default_message="An error occurred"):
    logger.error(f"Error in {context}: {str(e)}", exc_info=True)
    return default_message, 500


def handle_api_error(e, context, logger, default_message="Server error occurred"):
    logger.error(f"Error in {context}: {str(e)}", exc_info=True)
    return error_response(default_message)
