from flask import jsonify


def success_response(message, **kwargs):
    """
    Create standardized success response
    """
    response = {"success": True, "message": message}
    response.update(kwargs)
    return jsonify(response)


def error_response(message, status_code=500):
    """
    Create standardized error response
    """
    return jsonify({"success": False, "message": message}), status_code
