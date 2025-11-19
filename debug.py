import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulacion_debug.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

from main import main
main()