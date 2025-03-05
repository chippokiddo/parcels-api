from typing import Optional
from urllib.parse import quote
from config import SHIPPING_CARRIERS


def get_tracking_url(shipper: str, tracking_no: str) -> Optional[str]:
    """Generate tracking URL for a given shipper and tracking number.

    Args:
        shipper: The shipping carrier code
        tracking_no: The tracking number

    Returns:
        URL string or None if invalid
    """
    if not tracking_no or not shipper:
        return None

    shipper = shipper.upper()
    if shipper not in SHIPPING_CARRIERS:
        return None

    encoded_tracking = quote(str(tracking_no))
    return SHIPPING_CARRIERS[shipper].format(encoded_tracking)