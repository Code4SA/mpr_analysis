import plotly as py
import plotly.graph_objs as go
from models import Product
from config import get_session
import sys


py.offline.init_notebook_mode(connected=True)

equivalence_key = sys.argv[1]

session = get_session()
related_products = session.query(Product).filter_by(equivalence_key=equivalence_key).all()

data = []

for p in related_products:
    xs = []
    ys = []
    for price in p.prices:
        xs.append(price.effective_date)
        ys.append(price.cost_per_unit)
    trace = go.Scatter(
        x = xs,
        y = ys,
        mode = 'lines+markers',
        name = p.unique_name
    )
    # print trace
    data.append(trace)
filename = equivalence_key.replace("/", "-") + '.html'
py.offline.plot(
    {
        'data': data,
        'layout': {
            'title': equivalence_key
        }
    },
    filename=filename,
    auto_open=False,
)
