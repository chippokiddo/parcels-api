# Parcels Backend API

![Python](https://img.shields.io/badge/Python-3.9%2B-%233776AB?logo=python)
![python-dotenv](https://img.shields.io/badge/python--dotenv-1.0.1%2B-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.0%2B-black?style=flat&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite3-%23003B57?style=flat&logo=sqlite)
![License](https://img.shields.io/github/license/chippokiddo/parcels-api)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?&logo=buy-me-a-coffee&logoColor=0D0C22)](https://buymeacoffee.com/chippo)

A backend API built with Flask for tracking and managing orders, with tracking details, archiving, and exporting capabilities.

## Overview

This repository contains only the backend portion of the Parcels order tracking and management system. The frontend files (static assets and templates) are not included and should be integrated separately. This system allows users to manage orders with tracking details, archive completed/cancelled orders, and export data.

## Features

- RESTful API endpoints for order management
- Active and archived order tracking
- Order creation, editing, and deletion
- Tracking link generation for shipments
- Filtering and searching capabilities
- CSV export functionality
- SQLite database integration

## Project Structure

```
.
├── .github
├── app.py                    # Main application entry point
├── config.py                 # Application configuration
├── models/
│   └── orders.py             # Order database operations
├── routes/
│   ├── __init__.py           # Route registration
│   ├── active_orders.py      # Active order routes
│   └── archived_orders.py    # Archived order routes
├── utils/
│   ├── __init__.py
│   ├── database.py           # Database connection utilities
│   └── shipping.py           # Shipping carrier tracking URL generation
├── .env.example
├── .gitignore
└── requirements.txt
```

## Requirements

- Python 3.9+
- Flask 3.1.0+
- SQLite3
- python-dotenv 1.0.1+

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/chippokiddo/parcels-api.git
   cd parcels-api
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate	# On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure your environment variables:

   ```
   cp .env.example .env
   ```

   Make sure to set `FLASK_SECRET_KEY` in your .env file.

5. Initialize the database:

   ```
   # You'll need to create a script to initialize the database structure
   # Example:
   # python init_db.py
   ```

   The database should include an 'orders' table with fields for:

   - order_date
   - vendor
   - order_no
   - item_name
   - amount
   - currency
   - shipper
   - tracking_no
   - location
   - delivery
   - notes
   - color
   - order_status
   - last_updated
   - shipped_date

## Running the Application

For production/deployment:

```
flask run
```

For development with debug mode:

```
# Modify app.py by commenting out:
# app = create_app()
# 
# And uncomment these lines:
# if __name__ == "__main__":
#     try:
#         app = create_app()
#         app.run(debug=True, host="0.0.0.0", port=5000)
#     except Exception as e:
#         logger.critical(f"Application failed to start: {str(e)}", exc_info=True)
```

The API will be available at `http://localhost:5000`.

## API Documentation

### Order Management Endpoints

#### Active Orders

- `GET /` - List all active orders
- `GET /form` - Display order creation form (frontend integration point)
- `GET /check_order_no/<order_no>` - Check if order number exists
- `POST /submit_order` - Create a new order
- `GET /edit_order/<order_no>` - Display order edit form (frontend integration point)
- `POST /update_order/<order_no>` - Update an existing order
- `POST /delete_order/<order_no>` - Delete an order

#### Archived Orders

- `GET /archive` - Display archived orders with optional filtering
- `GET /archive/export_csv` - Export archived orders as CSV

### Data Models

#### Order Model

- `order_date` - Date the order was placed
- `vendor` - Supplier or vendor name
- `order_no` - Unique order number
- `item_name` - Description of ordered item
- `amount` - Order amount
- `currency` - Currency for the amount
- `shipper` - Shipping carrier (FedEx, etc.)
- `tracking_no` - Shipment tracking number
- `location` - Location information
- `delivery` - Delivery details
- `notes` - Additional notes
- `color` - Color code or information
- `order_status` - Status (active, completed, cancelled)
- `last_updated` - Last update timestamp
- `shipped_date` - Date the order was shipped

## Frontend Integration

This repository contains only the backend API code. To integrate with a frontend:

1. Create template files that match the routes in the application:
   - `templates/index.html` - For displaying active orders
   - `templates/form.html` - For the order creation form
   - `templates/edit.html` - For the order editing form
   - `templates/archive.html` - For displaying archived orders
2. Make sure your frontend forms match the expected form field names in the routes
3. Add static files (CSS, JavaScript) for frontend interactions

## Configuration

The application uses environment variables for configuration:

- `FLASK_SECRET_KEY` - Secret key for session security (required)
- `DATABASE_PATH` - Path to SQLite database (defaults to "identifier.sqlite")

You can extend the `SHIPPING_CARRIERS` dictionary in `config.py` to add more shipping carriers for tracking URL generation.

## Testing

To create and run tests:

```bash
# Create tests directory first
mkdir tests
# Run tests with pytest
pytest
```

## Deployment

For production deployment:

1. Set up a production WSGI server (Gunicorn, uWSGI)
2. Configure a reverse proxy (Nginx, Apache)
3. Ensure environment variables are properly set
4. Use a production-grade database if needed

Example with Gunicorn:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request
