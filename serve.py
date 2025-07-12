import logging
from waitress import serve
import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Launching Waitress WSGI server (20 threads) on 0.0.0.0:5000")
    serve(app.app, host='0.0.0.0', port=5000, threads=20)
