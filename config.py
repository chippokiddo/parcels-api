import logging
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = "identifier.sqlite"

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

SHIPPING_CARRIERS = {
    "FedEx": "https://www.fedex.com/fedextrack/?trknbr={}",
    # "UPS": "https://www.ups.com/track?tracknum={}",
}
