import logging
import os
import sys
from config import get_session
from models import Product, ProductIngredient, Ingredient, ProductSEP


logging.basicConfig(
    level='DEBUG',
    format='%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s',
)
logger = logging.getLogger(__name__)


def main():
    session = get_session()
    print session.query(Product).count()

if __name__ == "__main__":
    main()
