import sqlite3
from typing import Dict

from utils.shipping import get_tracking_url
from .formatters import format_amount, format_record_dict


def format_order_dict(order: sqlite3.Row) -> Dict:
    """
    Format order dictionary with order-specific fields
    """
    order_dict = format_record_dict(order)
    if not order_dict:
        return {}

    # Add amount formatting
    if order_dict.get('amount') and order_dict['amount'] != '':
        order_dict['amount_formatted'], order_dict['amount_display'] = format_amount(order_dict['amount'])
    else:
        order_dict['amount_formatted'] = ''
        order_dict['amount_display'] = ''

    # Add tracking URL if available
    if order_dict.get('shipper') and order_dict.get('tracking_no'):
        order_dict['tracking_url'] = get_tracking_url(
            order_dict['shipper'],
            order_dict['tracking_no']
        )

    return order_dict


def get_order_not_null_columns() -> set:
    """
    Get the set of columns that should not be null for orders
    """
    return {
        'order_date', 'vendor', 'item_name',
        'order_status', 'color', 'currency', 'amount', 'last_updated'
    }
