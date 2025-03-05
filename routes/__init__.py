from flask import Flask


def register_routes(app: Flask):
    """Register all route blueprints with the app."""
    from .active_orders import active_orders_bp
    from .archived_orders import archived_orders_bp

    # Register blueprints with correct URL prefixes
    app.register_blueprint(active_orders_bp, url_prefix='/')
    app.register_blueprint(archived_orders_bp, url_prefix='/archive')