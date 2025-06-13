import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import logger
from utils.data_processing import process_record_data
from utils.database import get_db_connection
from utils.order_helpers import format_order_dict, get_order_not_null_columns
from utils.pagination import create_pagination_info
from utils.query_builders import (
    build_date_filter_conditions,
    build_status_filter_conditions,
    combine_filter_conditions
)


class OrdersDB:
    @staticmethod
    def get_active_orders() -> List[Dict]:
        """
        Retrieve all active orders (including those with empty status)
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                               SELECT *
                               FROM orders
                               WHERE order_status NOT IN ('completed', 'cancelled')
                               ORDER BY order_date DESC, last_updated DESC
                               """)
                return [format_order_dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"Error getting active orders: {str(e)}")
                raise

    @staticmethod
    def get_order(order_no: str) -> Optional[Dict]:
        """
        Retrieve a specific order regardless of status
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                               SELECT *
                               FROM orders
                               WHERE order_no = ?
                               """, (order_no,))
                order = cursor.fetchone()
                return format_order_dict(order) if order else None
            except Exception as e:
                logger.error(f"Error getting order {order_no}: {str(e)}")
                raise

    @staticmethod
    def check_order_exists(
            order_no: str,
            current_order: Optional[str] = None
    ) -> bool:
        """
        Check if an order number already exists
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                if current_order:
                    cursor.execute("""
                                   SELECT 1
                                   FROM orders
                                   WHERE order_no = ?
                                     AND order_no != ?
                                   """, (order_no, current_order))
                else:
                    cursor.execute("""
                                   SELECT 1
                                   FROM orders
                                   WHERE order_no = ?
                                   """, (order_no,))
                return cursor.fetchone() is not None
            except Exception as e:
                logger.error(f"Error checking if order exists: {str(e)}")
                raise

    @staticmethod
    def create_order(order_data: Dict) -> None:
        """
        Create a new order
        """
        with get_db_connection() as conn:
            try:
                current_datetime = datetime.now().strftime("%Y-%m-%d")
                cursor = conn.cursor()

                processed_data = process_record_data(order_data, get_order_not_null_columns())

                cursor.execute("""
                               INSERT INTO orders (order_date, vendor, order_no, item_name,
                                                   quantity, currency, amount, color,
                                                   shipped_date, shipper, tracking_no, location,
                                                   delivery, last_updated, notes, order_status)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                               """, (
                                   processed_data['order_date'],
                                   processed_data['vendor'],
                                   processed_data['order_no'],
                                   processed_data['item_name'],
                                   processed_data.get('quantity'),
                                   processed_data['currency'],
                                   processed_data['amount'],
                                   processed_data['color'],
                                   processed_data.get('shipped_date'),
                                   processed_data.get('shipper'),
                                   processed_data.get('tracking_no'),
                                   processed_data.get('location'),
                                   processed_data.get('delivery'),
                                   current_datetime,
                                   processed_data.get('notes'),
                                   processed_data['order_status']
                               ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error creating order: {str(e)}")
                raise

    @staticmethod
    def update_order(order_no: str, order_data: Dict) -> None:
        """
        Update an existing order
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                processed_data = process_record_data(order_data, get_order_not_null_columns())

                cursor.execute("""
                               UPDATE orders
                               SET order_date   = COALESCE(NULLIF(?, ''), order_date),
                                   vendor       = COALESCE(NULLIF(?, ''), vendor),
                                   item_name    = COALESCE(NULLIF(?, ''), item_name),
                                   quantity     = ?,
                                   currency     = COALESCE(NULLIF(?, ''), currency),
                                   amount       = COALESCE(NULLIF(?, ''), amount),
                                   color        = COALESCE(NULLIF(?, ''), color),
                                   shipped_date = ?,
                                   shipper      = ?,
                                   tracking_no  = ?,
                                   location     = ?,
                                   delivery     = ?,
                                   last_updated = COALESCE(NULLIF(?, ''), last_updated),
                                   notes        = ?,
                                   order_status = COALESCE(NULLIF(?, ''), order_status)
                               WHERE order_no = ?
                               """, (
                                   processed_data["order_date"],
                                   processed_data["vendor"],
                                   processed_data["item_name"],
                                   processed_data.get("quantity"),
                                   processed_data["currency"],
                                   processed_data["amount"],
                                   processed_data["color"],
                                   processed_data.get("shipped_date"),
                                   processed_data.get("shipper"),
                                   processed_data.get("tracking_no"),
                                   processed_data.get("location"),
                                   processed_data.get("delivery"),
                                   processed_data["last_updated"],
                                   processed_data.get("notes"),
                                   processed_data["order_status"],
                                   order_no
                               ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error updating order {order_no}: {str(e)}")
                raise

    @staticmethod
    def delete_order(order_no: str) -> None:
        """
        Delete an order
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM orders WHERE order_no = ?", (order_no,))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error deleting order {order_no}: {str(e)}")
                raise

    @staticmethod
    def get_archived_orders_totals(
            status_filter: Optional[str] = None,
            year_filter: Optional[str] = None,
            month_filter: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get currency totals for archived orders with filters applied
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()

                base_query = """
                             SELECT currency, SUM(CAST(amount as REAL)) as total
                             FROM orders
                             WHERE order_status IN ('completed', 'cancelled')
                               AND amount IS NOT NULL
                               AND amount != ''
                               AND currency IS NOT NULL
                               AND currency != '' \
                             """

                # Build filter conditions
                status_conditions = build_status_filter_conditions(status_filter)
                date_conditions = build_date_filter_conditions(year_filter, month_filter)
                query_conditions, query_params = combine_filter_conditions(
                    status_conditions, date_conditions
                )

                full_query = base_query + query_conditions + " GROUP BY currency ORDER BY currency"

                cursor.execute(full_query, query_params)
                results = cursor.fetchall()

                # Convert to dictionary with proper formatting
                totals = {}
                for row in results:
                    currency = row['currency']
                    total = row['total']
                    if currency and total is not None:
                        totals[currency] = float(f"{total:.2f}")

                return totals

            except Exception as e:
                logger.error(f"Error getting archived orders totals: {str(e)}", exc_info=True)
                return {}

    @staticmethod
    def get_archived_orders(
            status_filter: Optional[str] = None,
            year_filter: Optional[str] = None,
            month_filter: Optional[str] = None,
            page: int = 1,
            limit: int = 10
    ) -> Tuple[List[Dict], List[str], List[Tuple[str, str]], Dict, Dict[str, float]]:
        """
        Get archived orders with optional filters and pagination
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()

                # Get available filter options
                cursor.execute("""
                               SELECT DISTINCT strftime('%Y', order_date) as year,
                                               strftime('%m', order_date) as month
                               FROM orders
                               WHERE order_status IN ('completed', 'cancelled')
                               ORDER BY year DESC, month DESC
                               """)
                dates = cursor.fetchall()

                available_years = sorted(set(row['year'] for row in dates), reverse=True) if dates else []
                available_months = [
                    ('01', 'January'), ('02', 'February'), ('03', 'March'),
                    ('04', 'April'), ('05', 'May'), ('06', 'June'),
                    ('07', 'July'), ('08', 'August'), ('09', 'September'),
                    ('10', 'October'), ('11', 'November'), ('12', 'December')
                ]

                base_query = """
                    FROM orders 
                    WHERE order_status IN ('completed', 'cancelled')
                """

                # Build filter conditions
                status_conditions = build_status_filter_conditions(status_filter)
                date_conditions = build_date_filter_conditions(year_filter, month_filter)
                query_conditions, query_params = combine_filter_conditions(
                    status_conditions, date_conditions
                )

                # Get total count
                count_query = f"SELECT COUNT(*) as total {base_query}{query_conditions}"
                cursor.execute(count_query, query_params)
                total_count = cursor.fetchone()['total']

                # Get paginated data
                offset = (page - 1) * limit
                data_query = f"""
                    SELECT * {base_query}{query_conditions}
                    ORDER BY order_date DESC, last_updated DESC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(data_query, query_params + [limit, offset])
                orders = [format_order_dict(row) for row in cursor.fetchall()]

                pagination = create_pagination_info(page, total_count, limit)
                currency_totals = OrdersDB.get_archived_orders_totals(
                    status_filter, year_filter, month_filter
                )

                return orders, available_years, available_months, pagination, currency_totals

            except Exception as e:
                logger.error(f"Error getting archived orders: {str(e)}", exc_info=True)
                raise

    @staticmethod
    def export_archived_orders(
            status_filter: Optional[str] = None,
            date_filter: Optional[str] = None
    ) -> List[sqlite3.Row]:
        """
        Export archived orders with optional filters
        """
        with get_db_connection() as conn:
            try:
                query = """
                        SELECT order_date, \
                               vendor, \
                               order_no, \
                               item_name, \
                               quantity,
                               currency, \
                               amount, \
                               shipped_date, \
                               shipper, \
                               tracking_no,
                               location, \
                               last_updated, \
                               notes, \
                               order_status
                        FROM orders
                        WHERE order_status IN ('completed', 'cancelled')
                        """
                params = []

                if status_filter:
                    query += " AND order_status = ?"
                    params.append(status_filter)

                if date_filter:
                    query += " AND strftime('%Y-%m', order_date) = ?"
                    params.append(date_filter)

                query += " ORDER BY order_date DESC"

                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()

            except Exception as e:
                logger.error(f"Error exporting archived orders: {str(e)}")
                raise
