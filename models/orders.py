import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import logger
from utils.database import get_db_connection
from utils.shipping import get_tracking_url

def format_order_dict(order: sqlite3.Row) -> Dict:
    """Format order dictionary and handle None values."""
    if not order:
        return {}

    order_dict = dict(order)
    for key in order_dict:
        if order_dict[key] is None:
            order_dict[key] = ''

    if order_dict.get('shipper') and order_dict.get('tracking_no'):
        order_dict['tracking_url'] = get_tracking_url(
            order_dict['shipper'],
            order_dict['tracking_no']
        )

    return order_dict


class OrdersDB:
    @staticmethod
    def get_active_orders() -> List[Dict]:
        """Retrieve all active orders."""
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT *
                    FROM orders 
                    WHERE order_status = 'active'
                    ORDER BY order_date DESC, last_updated DESC
                """)
                return [format_order_dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"Error getting active orders: {str(e)}")
                raise

    @staticmethod
    def get_order(order_no: str) -> Optional[Dict]:
        """Retrieve a specific order regardless of status."""
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
        """Check if an order number already exists."""
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                if current_order:
                    cursor.execute("""
                        SELECT 1 
                        FROM orders 
                        WHERE order_no = ? 
                        AND order_status = 'active'
                        AND order_no != ?
                    """, (order_no, current_order))
                else:
                    cursor.execute("""
                        SELECT 1 
                        FROM orders 
                        WHERE order_no = ? 
                        AND order_status = 'active'
                    """, (order_no,))
                return cursor.fetchone() is not None
            except Exception as e:
                logger.error(f"Error checking if order exists: {str(e)}")
                raise

    @staticmethod
    def create_order(order_data: Dict) -> None:
        """Create a new order."""
        with get_db_connection() as conn:
            try:
                current_datetime = datetime.now().strftime("%Y-%m-%d")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (
                        order_date, vendor, order_no, item_name, amount,
                        currency, shipper, tracking_no, location, delivery,
                        notes, color, order_status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
                """, (
                    current_datetime,
                    order_data['vendor'],
                    order_data['order_no'],
                    order_data['item_name'],
                    order_data['amount'],
                    order_data.get('currency', ''),
                    order_data.get('shipper', ''),
                    order_data.get('tracking_no', ''),
                    order_data.get('location', ''),
                    order_data.get('delivery', ''),
                    order_data.get('notes', ''),
                    order_data.get('color', ''),
                    current_datetime
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error creating order: {str(e)}")
                raise

    @staticmethod
    def update_order(order_no: str, order_data: Dict) -> None:
        """Update an existing order."""
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE orders SET 
                        order_date = COALESCE(NULLIF(?, ''), order_date),
                        vendor = COALESCE(NULLIF(?, ''), vendor),
                        item_name = COALESCE(NULLIF(?, ''), item_name),
                        shipper = ?,
                        tracking_no = ?,
                        location = ?,
                        amount = COALESCE(NULLIF(?, ''), amount),
                        currency = ?,
                        last_updated = ?,
                        shipped_date = ?,
                        notes = ?,
                        order_status = COALESCE(NULLIF(?, ''), order_status),
                        color = ?,
                        delivery = ?
                    WHERE order_no = ?
                """, (
                    order_data["order_date"],
                    order_data["vendor"],
                    order_data["item_name"],
                    order_data["shipper"],
                    order_data["tracking_no"],
                    order_data["location"],
                    order_data["amount"],
                    order_data["currency"],
                    order_data["last_updated"],
                    order_data["shipped_date"],
                    order_data["notes"],
                    order_data["order_status"],
                    order_data["color"],
                    order_data["delivery"],
                    order_no,
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error updating order {order_no}: {str(e)}")
                raise

    @staticmethod
    def delete_order(order_no: str) -> None:
        """Delete an order."""
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
    def get_archived_orders(
            status_filter: Optional[str] = None,
            year_filter: Optional[str] = None,
            month_filter: Optional[str] = None,
            page: int = 1,
            limit: int = 10
    ) -> Tuple[List[Dict], List[str], List[Tuple[str, str]], Dict]:
        """Get archived orders with optional filters and pagination.

        Args:
            status_filter: Filter by order status
            year_filter: Filter by year
            month_filter: Filter by month
            page: Page number (starting from 1)
            limit: Number of orders per page

        Returns:
            Tuple containing:
                - List of orders for the current page
                - Available years for filtering
                - Available months for filtering
                - Pagination information dictionary
        """
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT DISTINCT 
                        strftime('%Y', order_date) as year,
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

                query_params = []

                if status_filter:
                    base_query += " AND order_status = ?"
                    query_params.append(status_filter)

                if year_filter:
                    base_query += " AND strftime('%Y', order_date) = ?"
                    query_params.append(year_filter)

                if month_filter:
                    base_query += " AND strftime('%m', order_date) = ?"
                    query_params.append(month_filter)

                count_query = f"SELECT COUNT(*) as total {base_query}"
                cursor.execute(count_query, query_params)
                total_count = cursor.fetchone()['total']

                offset = (page - 1) * limit
                total_pages = (total_count + limit - 1) // limit

                data_query = f"""
                    SELECT * {base_query}
                    ORDER BY order_date DESC, last_updated DESC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(data_query, query_params + [limit, offset])
                orders = [format_order_dict(row) for row in cursor.fetchall()]

                pagination = {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'has_prev': page > 1,
                    'has_next': page < total_pages,
                    'limit': limit
                }

                return orders, available_years, available_months, pagination

            except Exception as e:
                logger.error(f"Error getting archived orders: {str(e)}", exc_info=True)
                raise

    @staticmethod
    def export_archived_orders(
            status_filter: Optional[str] = None,
            date_filter: Optional[str] = None
    ) -> List[sqlite3.Row]:
        """Export archived orders with optional filters."""
        with get_db_connection() as conn:
            try:
                query = """
                    SELECT order_date, vendor, order_no, item_name, shipper, tracking_no, 
                           location, amount, currency, shipped_date, notes, order_status, 
                           last_updated, color
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