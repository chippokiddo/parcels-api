from flask import Blueprint, render_template, request

from config import logger
from models.orders import OrdersDB
from utils.csv_helpers import create_csv_response, build_export_filename
from utils.error_handlers import handle_route_error
from utils.pagination import validate_page_number
from utils.request_helpers import extract_filters

archived_orders_bp = Blueprint('archived_orders', __name__, template_folder='templates')


@archived_orders_bp.route("")
def archive():
    """
    Display archived orders with pagination
    """
    try:
        filters = extract_filters(request)
        page = validate_page_number(request.args.get('page', 1))

        limit = 10
        logger.info(f"Archive request: {filters}, page={page}")

        orders, available_years, available_months, pagination, currency_totals = OrdersDB.get_archived_orders(
            status_filter=filters['status_filter'],
            year_filter=filters['year_filter'],
            month_filter=filters['month_filter'],
            page=page,
            limit=limit
        )

        logger.info(f"Retrieved {len(orders)} archived orders (page {page} of {pagination['total_pages']})")
        logger.info(f"Currency totals: {currency_totals}")

        return render_template(
            "archive.html",
            orders=orders,
            available_years=available_years,
            available_months=available_months,
            pagination=pagination,
            currency_totals=currency_totals
        )
    except Exception as e:
        return handle_route_error(e, "archive route", logger, "An error occurred loading the archive")


@archived_orders_bp.route("/export_csv")
def export_archive_csv():
    """
    Export archived orders to CSV
    """
    try:
        # Extract filters
        status_filter = request.args.get('status')
        year_filter = request.args.get('year')
        month_filter = request.args.get('month')

        date_filter = None
        if year_filter and month_filter:
            date_filter = f"{year_filter}-{month_filter}"

        # Get data
        archived_orders = OrdersDB.export_archived_orders(status_filter, date_filter)

        # Define headers
        headers = [
            'Order Date', 'Vendor', 'Order Number', 'Item', 'Quantity',
            'Currency', 'Amount', 'Shipped Date', 'Shipper',
            'Tracking Number', 'Location', 'Last Updated', 'Notes', 'Status'
        ]

        filename = build_export_filename(
            "archived_orders",
            status=status_filter,
            year=year_filter,
            month=month_filter
        )

        return create_csv_response(archived_orders, headers, filename)

    except Exception as e:
        return handle_route_error(e, "export_archive_csv", logger, "Error exporting archive")
