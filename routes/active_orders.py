from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from config import logger
from models.orders import OrdersDB
from utils.error_handlers import handle_api_error, handle_route_error
from utils.request_helpers import extract_form_data, validate_required_fields
from utils.response_helpers import success_response, error_response
from utils.route_helpers import (
    build_order_data_from_form,
    determine_redirect_source,
    get_order_form_fields,
    get_required_order_fields
)

active_orders_bp = Blueprint('active_orders', __name__, template_folder='templates')


@active_orders_bp.route("/")
def index():
    """
    Display active orders
    """
    try:
        orders = OrdersDB.get_active_orders()
        return render_template("index.html", orders=orders)
    except Exception as e:
        return handle_route_error(e, "index route", logger, "An error occurred loading the page")


@active_orders_bp.route("/form")
def form():
    """
    Display order form
    """
    return render_template("form.html")


@active_orders_bp.route("/check_order_no/<order_no>")
def check_order_no(order_no: str):
    """
    Check if order number exists
    """
    try:
        current_order = request.args.get('current')
        exists = OrdersDB.check_order_exists(order_no, current_order)
        return jsonify({"exists": exists})
    except Exception as e:
        logger.error(f"Error checking order number: {str(e)}", exc_info=True)
        return jsonify({"error": "Database error"}), 500


@active_orders_bp.route("/submit_order", methods=["POST"])
def submit_order():
    """
    Handle order submission
    """
    try:
        form_data = extract_form_data(request, get_order_form_fields())

        missing_fields = validate_required_fields(form_data, get_required_order_fields())
        if missing_fields:
            return error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                400
            )

        if OrdersDB.check_order_exists(form_data['order_no']):
            return error_response("An active order with this number already exists", 400)

        OrdersDB.create_order(form_data)
        return success_response("Order created successfully!")

    except Exception as e:
        return handle_api_error(e, "submit_order", logger, "Server error occurred")


@active_orders_bp.route("/update_order/<order_no>", methods=["POST"])
def update_order(order_no: str):
    """
    Handle order updates
    """
    try:
        order_data = build_order_data_from_form(order_no)
        OrdersDB.update_order(order_no, order_data)

        redirect_url = url_for(determine_redirect_source())

        return jsonify({
            "success": True,
            "message": "Order updated successfully!",
            "redirect": redirect_url
        })
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the order"
        }), 500


@active_orders_bp.route("/edit_order/<order_no>")
def edit_order(order_no: str):
    """
    Display order edit form
    """
    try:
        order = OrdersDB.get_order(order_no)
        if not order:
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        source = determine_redirect_source()
        return render_template("edit.html", order=order, source=source)

    except Exception as e:
        logger.error(f"Error loading order for editing: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error loading order"
        }), 500


@active_orders_bp.route("/delete_order/<order_no>", methods=["POST"])
def delete_order(order_no: str):
    """
    Delete an order
    """
    try:
        OrdersDB.delete_order(order_no)
        source = determine_redirect_source()
        return redirect(url_for(source))
    except Exception as e:
        return handle_route_error(e, "delete_order", logger, "Error deleting order")
