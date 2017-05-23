import matplotlib.pyplot as plt
import sys
from models import Product
from config import get_session

equivalence_key = sys.argv[1]
styles = ['-o', '-|', '-x', '-*',]
figure = plt.figure(figsize=(12, 6))

session = get_session()
related_products = sorted(session.query(Product).filter_by(equivalence_key=equivalence_key).all())

fig = plt.figure(1)
ax = fig.add_subplot(1, 1, 1)

for i, p in enumerate(related_products):
    xs = []
    ys = []
    for price in p.prices:
        xs.append(price.effective_date)
        ys.append(price.cost_per_unit)
    ax.plot_date(xs, ys, styles[i%len(styles)], label=p.unique_name, figure=figure)

ax.set_ylabel('Unit Price')
ax.set_xlabel('Effective Date')
ax.set_title(equivalence_key)
lgd = ax.legend(loc=2, bbox_to_anchor=(0., -1.1, 1., 1.))
filename = equivalence_key.replace("/", "-") + '.png'
plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
