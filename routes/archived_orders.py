import csv
import io

from flask import Blueprint, make_response, render_template, request

from config import logger
from models.orders import OrdersDB

archived_orders_bp = Blueprint('archived_orders', __name__, template_folder='templates')


@archived_orders_bp.route("")
def archive():
    """
    Display archived orders with pagination
    """
    try:
        status_filter = request.args.get('status')
        month_filter = request.args.get('month')
        year_filter = request.args.get('year')

        try:
            page = int(request.args.get('page', 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        limit = 10  # Fixed limit of 10 orders per page

        logger.info(f"Archive request: status={status_filter}, month={month_filter}, year={year_filter}, page={page}")

        orders, available_years, available_months, pagination, currency_totals = OrdersDB.get_archived_orders(
            status_filter=status_filter,
            year_filter=year_filter,
            month_filter=month_filter,
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
        logger.error(f"Error in archive route: {str(e)}", exc_info=True)
        return "An error occurred loading the archive", 500


@archived_orders_bp.route("/export_csv")
def export_archive_csv():
    """
    Export archived orders to CSV
    """
    try:
        status_filter = request.args.get('status')
        year_filter = request.args.get('year')
        month_filter = request.args.get('month')

        date_filter = None
        if year_filter and month_filter:
            date_filter = f"{year_filter}-{month_filter}"

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
        if year_filter:
            filename += f"_{year_filter}"
        if month_filter:
            filename += f"_{month_filter}"
        filename += ".csv"

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "text/csv"

        return response

    except Exception as e:
        logger.error(f"Error exporting archive CSV: {str(e)}", exc_info=True)
        return "Error exporting archive", 500
