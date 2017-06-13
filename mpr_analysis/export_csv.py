import unicodecsv as csv
from mpr_analysis.models import ProductSEP
from mpr_analysis.config import get_session

session = get_session()
seps = session.query(ProductSEP).all()

with open('products-seps-cleaned.csv', 'w') as csvfile:
    fieldnames = [
        'applicant_name',
        'applicant_licence_no',
        'regno',
        'nappi_code',
        'name',
        'schedule',
        'dosage_form',
        'pack_size',
        'is_generic',
        'num_packs',
        'equivalence_key',
        'sep',
        'effective_date',
        'unit_price',
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for sep in seps:
        writer.writerow({
            'applicant_name': sep.product.applicant_name,
            'applicant_licence_no': sep.product.applicant_licence_no,
            'regno': sep.product.regno,
            'nappi_code': sep.product.nappi_code,
            'name': sep.product.name,
            'schedule': sep.product.schedule,
            'dosage_form': sep.product.dosage_form,
            'pack_size': sep.product.pack_size,
            'is_generic': sep.product.is_generic,
            'num_packs': sep.product.num_packs,
            'equivalence_key': sep.product.equivalence_key,
            'sep': sep.sep,
            'effective_date': sep.effective_date.isoformat(),
            'unit_price': sep.cost_per_unit,
        })
