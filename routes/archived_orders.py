import csv
import io

from flask import Blueprint, make_response, render_template, request

from config import logger
from models.orders import OrdersDB

archived_orders_bp = Blueprint('archived_orders', __name__, template_folder='templates')


@archived_orders_bp.route("")
def archive():
    """Display archived orders without pagination."""
    try:
        status_filter = request.args.get('status')
        month_filter = request.args.get('month')
        year_filter = request.args.get('year')

        logger.info(f"Archive request: status={status_filter}, month={month_filter}, year={year_filter}")

        orders, available_years, available_months = OrdersDB.get_archived_orders(
            status_filter=status_filter,
            year_filter=year_filter,
            month_filter=month_filter
        )

        logger.info(f"Retrieved {len(orders)} archived orders")

        return render_template(
            "archive.html",
            orders=orders,
            available_years=available_years,
            available_months=available_months,
            pagination=None
        )
    except Exception as e:
        logger.error(f"Error in archive route: {str(e)}", exc_info=True)
        return "An error occurred loading the archive", 500


@archived_orders_bp.route("/export_csv")
def export_archive_csv():
    """Export archived orders to CSV."""
    try:
        status_filter = request.args.get('status')
        date_filter = request.args.get('date')

        archived_orders = OrdersDB.export_archived_orders(status_filter, date_filter)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            'Order Date', 'Vendor', 'Order Number', 'Item', 'Shipper',
            'Tracking Number', 'Location', 'Amount', 'Currency', 'Shipped Date',
            'Notes', 'Status', 'Last Updated', 'Color'
        ])

        for order in archived_orders:
            writer.writerow(order)

        filename = "archived_orders"
        if status_filter:
            filename += f"_{status_filter}"
        if date_filter:
            filename += f"_{date_filter}"
        filename += ".csv"

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "text/csv"

        return response

    except Exception as e:
        logger.error(f"Error exporting archive CSV: {str(e)}", exc_info=True)
        return "Error exporting archive", 500