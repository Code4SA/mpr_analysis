import logging
import os
import sys
from config import get_session
from models import Product, ProductIngredient, Ingredient, ProductSEP
import xlrd


name_change = {
    "amoxycillin": "Amoxicillin",
}

logging.basicConfig(
    level='DEBUG',
    format='%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s',
)
logger = logging.getLogger(__name__)


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


def parse(filename):
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_index(0)

    product = None
    for idx in range(1, worksheet.nrows):
        nappi_code = worksheet.cell_value(idx, 3)
        regno = worksheet.cell_value(idx, 2).lower()
        pack_size = worksheet.cell_value(idx, 11)
        num_packs = worksheet.cell_value(idx, 12)
        sep = worksheet.cell_value(idx, 16)
        effective_date = worksheet.cell_value(idx, 18)
        name = worksheet.cell_value(idx, 6).title()

        if "medicine" in regno.lower():
            continue

        if regno.strip() != "":
            if product: yield product

            generic_value = worksheet.cell_value(idx, 20)
            if "originator" in generic_value.lower():
                is_generic = "Originator"
            elif "generic" in generic_value.lower():
                is_generic = "Generic"
            else:
                is_generic = None

            try:
                nappi_code = "%s" % int(nappi_code)
            except ValueError:
                print "Could not process %s (%s) due to lack of nappi code" % (name, regno)
                continue

            if not sep:
                print "Could not process %s (%s) due to lack of SEP" % (name, nappi_code)
                continue
            pack_size = pack_size or 1
            num_packs = num_packs or 1

            product = {
                "nappi_code" : nappi_code,
                "regno" : regno,
                "schedule" : worksheet.cell_value(idx, 5),
                "name" : name,
                "dosage_form" : worksheet.cell_value(idx, 10).title(),
                "pack_size" : pack_size,
                "num_packs" : num_packs,
                "sep" : sep,
                "effective_date": effective_date,
                "is_generic" : is_generic,
                "ingredients" : []
            }

        ingredient_name = worksheet.cell_value(idx, 7).title()
        product["ingredients"].append({
            "name" : name_change.get(ingredient_name.lower(), ingredient_name),
            "strength" : worksheet.cell_value(idx, 8),
            "unit" : worksheet.cell_value(idx, 9).lower(),
        })


def main():
    filename = sys.argv[1]

    def int_or_none(x):
        try:
            return int(x)
        except (ValueError, TypeError):
            return None

    def float_or_none(x):
        try:
            return float(x)
        except (ValueError, TypeError):
            return None

    for p in parse(filename):
        session = get_session()
        print p

        ingredient_dicts = p['ingredients']
        sep = p['sep']
        effective_date = p['effective_date']
        del p['ingredients']
        del p['sep']
        del p['effective_date']

        product, new_product = get_or_create(session, Product, p)

        product_sep, new_product_sep = get_or_create(
            session,
            ProductSEP,
            {
                'sep': sep,
                'product': product,
                'effective_date': effective_date,
            }
        )

        for i in ingredients:
            strength = i['strenghth']
            del i['strength']
            ingredient, new_ingredient = get_or_create(session, Ingredient, i)

            product_ingredient, new_product_ingredient = get_or_create(
                session,
                ProductIngredient,
                {
                    'product': product,
                    'ingredient': ingredient,
                    'strength': strength,
                }
            )
        session.commit()

if __name__ == "__main__":
    main()
