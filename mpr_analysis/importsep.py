import logging
import os
import sys
from config import DB_URI
from models import Product, ProductIngredient, Ingredient, ProductSEP
import xlrd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from copy import copy

name_change = {
    "amoxycillin": "Amoxicillin",
}

logging.basicConfig(
    level='DEBUG',
    format='%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s',
)
logger = logging.getLogger(__name__)

def str_int_or_none(x):
    try:
        return str(int(x))
    except (ValueError, TypeError):
        return ''

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


def get_or_create(session, model, as_dict, update=[]):
    search_args = copy(as_dict)
    for k in update:
        del search_args[k]
    instance = session.query(model).filter_by(**search_args).first()
    if instance:
        for attr_name in update:
            old_val = getattr(instance, attr_name)
            new_val = as_dict[attr_name]
            if new_val and new_val != old_val:
                setattr(instance, attr_name, new_val)
        return instance, False
    else:
        instance = model(**as_dict)
        session.add(instance)
        session.flush()
        return instance, True


def parse(filename):
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_index(0)

    product = None
    skip_ingredients = False
    latest_date = None
    for idx in range(0, worksheet.nrows):
        nappi_code = worksheet.cell_value(idx, 3)
        regno = worksheet.cell_value(idx, 2).lower()
        pack_size = int_or_none(worksheet.cell_value(idx, 11))
        num_packs = int_or_none(worksheet.cell_value(idx, 12))
        sep = worksheet.cell_value(idx, 16)
        excel_effective_date = worksheet.cell_value(idx, 18)
        name = worksheet.cell_value(idx, 6).title()

        if "medicine" in regno.lower():
            continue

        if regno.strip() != "":
            if product and not skip_ingredients: yield product

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
                skip_ingredients = True
                continue

            if not sep:
                print "Could not process %s (%s) due to lack of SEP" % (name, nappi_code)
                skip_ingredients = True
                continue
            pack_size = pack_size or 1
            num_packs = num_packs or 1
            try:
                effective_date = xlrd.xldate.xldate_as_datetime(excel_effective_date, workbook.datemode)
                latest_date = effective_date
            except ValueError, e:
                print e
                if latest_date:
                    effective_date = latest_date
                else:
                    print "Could not process %s (%s) due to lack of effective_date"
                    skip_ingredients = True
                    continue

            product = {
                "nappi_code" : nappi_code.strip(),
                "regno" : regno.strip(),
                "schedule" : worksheet.cell_value(idx, 5),
                "name" : name.strip(),
                "dosage_form" : worksheet.cell_value(idx, 10).title(),
                "pack_size" : pack_size,
                "num_packs" : num_packs,
                "sep" : sep,
                "effective_date": effective_date,
                "is_generic" : is_generic,
                "ingredients" : []
            }
            skip_ingredients = False

        if not skip_ingredients:
            ingredient_name = worksheet.cell_value(idx, 7).title().strip()

            product["ingredients"].append({
                "name" : name_change.get(ingredient_name.lower(), ingredient_name),
                "strength" : str_int_or_none(worksheet.cell_value(idx, 8)),
                "unit" : worksheet.cell_value(idx, 9).lower().strip(),
            })


def main():
    filename = sys.argv[1]

    engine = create_engine(DB_URI)
    Session = sessionmaker(bind=engine)

    product_count = 0
    ingredient_count = 0
    price_count = 0
    new_product_count = 0
    new_ingredient_count = 0
    new_price_count = 0

    for p in parse(filename):
        session = Session()
        if (product_count % 100) == 0:
            print "---------------------\n"\
                "products    %d (%d)\n"\
                "prices      %d (%d)\n"\
                "ingredients %d (%d)" % \
                (product_count, new_product_count,
                 price_count, new_price_count,
                 ingredient_count, new_ingredient_count)
            print(p)

        ingredient_dicts = p['ingredients']
        sep = p['sep']
        effective_date = p['effective_date']
        del p['ingredients']
        del p['sep']
        del p['effective_date']

        product, new_product = get_or_create(session, Product, p, ['name', 'is_generic'])
        product_count += 1
        if new_product:
            new_product_count += 1

        product_sep, new_product_sep = get_or_create(
            session,
            ProductSEP,
            {
                'sep': sep,
                'product': product,
                'effective_date': effective_date,
            }
        )
        price_count += 1
        if new_product_sep:
            new_price_count += 1

        unique_ingredients = {}
        for i in ingredient_dicts:
            unique_ingredients[json.dumps(i, sort_keys=True)] = i
        ingredient_dicts = unique_ingredients.values()
        for i in ingredient_dicts:
            strength = i['strength']
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
            ingredient_count += 1
            if new_ingredient:
                new_ingredient_count += 1
        session.commit()


if __name__ == "__main__":
    main()
