from datetime import datetime
from typing import Dict, Optional

from flask import request


def build_order_data_from_form(order_no: Optional[str] = None) -> Dict:
    """
    Build order data dictionary from form request
    """
    current_datetime = datetime.now().strftime("%Y-%m-%d")

    order_data = {
        "order_date": request.form.get("order_date", "").strip(),
        "vendor": request.form.get("vendor", "").strip(),
        "item_name": request.form.get("item_name", "").strip(),
        "quantity": request.form.get("quantity", "").strip(),
        "currency": request.form.get("currency", "").strip(),
        "amount": request.form.get("amount", "").strip(),
        "color": request.form.get("color", "").strip(),
        "shipped_date": request.form.get("shipped_date", "").strip(),
        "shipper": request.form.get("shipper", "").strip().upper(),
        "tracking_no": request.form.get("tracking_no", "").strip(),
        "location": request.form.get("location", "").strip(),
        "delivery": request.form.get("delivery", "").strip(),
        "last_updated": current_datetime,
        "notes": request.form.get("notes", "").strip(),
        "order_status": request.form.get("order_status", "active").strip()
    }

    if order_no:
        order_data["order_no"] = order_no

    return order_data


def determine_redirect_source(default_source: str = "active_orders.index") -> str:
    """
    Determine the source for redirects based on form data or referrer
    """
    # First check form data
    source = request.form.get("source")
    if source:
        return source

    # Then check query args
    source = request.args.get("source")
    if source:
        return source

    # Finally check referrer
    if request.referrer and "archive" in request.referrer:
        return "archived_orders.archive"

    return default_source


def get_order_form_fields() -> list:
    """
    Get the standard order form field names
    """
    return [
        'order_date', 'vendor', 'order_no', 'item_name',
        'quantity', 'currency', 'amount', 'color',
        'shipped_date', 'shipper', 'tracking_no', 'location',
        'delivery', 'notes', 'order_status'
    ]


def get_required_order_fields() -> list:
    """
    Get required fields for order creation
    """
    return ['vendor', 'order_no', 'item_name', 'amount']
