from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from config import logger
from models.orders import OrdersDB

active_orders_bp = Blueprint('active_orders', __name__, template_folder='templates')


@active_orders_bp.route("/")
def index():
    """Display active orders."""
    try:
        orders = OrdersDB.get_active_orders()
        return render_template("index.html", orders=orders)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}", exc_info=True)
        return "An error occurred loading the page", 500


@active_orders_bp.route("/form")
def form():
    """Display order form."""
    return render_template("form.html")


@active_orders_bp.route("/check_order_no/<order_no>")
def check_order_no(order_no: str):
    """Check if order number exists."""
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
        required_fields = ['vendor', 'order_no', 'item_name', 'amount']

        form_data = {
            field: request.form.get(field, '').strip()
            for field in [
                'order_date', 'vendor', 'order_no', 'item_name', 'amount',
                'currency', 'shipper', 'tracking_no', 'location',
                'delivery', 'notes', 'color', 'shipped_date', 'order_status'
            ]
        }

        missing_fields = [field for field in required_fields if not form_data.get(field)]
        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        if OrdersDB.check_order_exists(form_data['order_no']):
            return jsonify({
                "success": False,
                "message": "An active order with this number already exists"
            }), 400

        OrdersDB.create_order(form_data)
        return jsonify({
            "success": True,
            "message": "Order created successfully!"
        })

    except Exception as e:
        logger.error(f"Error in submit_order: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Server error occurred"
        }), 500


@active_orders_bp.route("/update_order/<order_no>", methods=["POST"])
def update_order(order_no: str):
    """Handle order updates."""
    try:
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        order_data = {
            "order_date": request.form.get("order_date", "").strip(),
            "vendor": request.form.get("vendor", "").strip(),
            "order_no": order_no,
            "item_name": request.form.get("item_name", "").strip(),
            "shipper": request.form.get("shipper", "").strip().upper(),
            "tracking_no": request.form.get("tracking_no", "").strip(),
            "location": request.form.get("location", "").strip(),
            "amount": request.form.get("amount", "").strip(),
            "currency": request.form.get("currency", "").strip(),
            "last_updated": current_datetime,
            "shipped_date": request.form.get("shipped_date", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "order_status": request.form.get("order_status", "active").strip(),
            "color": request.form.get("color", "").strip(),
            "delivery": request.form.get("delivery", "").strip(),
        }

        OrdersDB.update_order(order_no, order_data)

        source = request.form.get("source", "active_orders.index")

        redirect_url = url_for(source)

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
    """Display order edit form."""
    try:
        order = OrdersDB.get_order(order_no)
        if not order:
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        source = request.args.get('source')
        if not source:
            if request.referrer and "archive" in request.referrer:
                source = "archived_orders.archive"
            else:
                source = "active_orders.index"

        return render_template("edit.html", order=order, source=source)

    except Exception as e:
        logger.error(f"Error loading order for editing: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Error loading order"
        }), 500


@active_orders_bp.route("/delete_order/<order_no>", methods=["POST"])
def delete_order(order_no: str):
    """Delete an order."""
    try:
        OrdersDB.delete_order(order_no)

        source = request.form.get("source", "active_orders.index")

        return redirect(url_for(source))
    except Exception as e:
        logger.error(f"Error deleting order: {str(e)}", exc_info=True)
        return "Error deleting order", 500
