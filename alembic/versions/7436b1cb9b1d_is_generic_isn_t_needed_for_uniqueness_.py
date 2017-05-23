"""is_generic isn't needed for uniqueness any more

Revision ID: 7436b1cb9b1d
Revises: 406a2a8bd71a
Create Date: 2017-05-23 15:52:57.020891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7436b1cb9b1d'
down_revision = '406a2a8bd71a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'product_unique', 'product', type_='unique')
    op.create_unique_constraint('product_unique', 'product', ['regno', 'nappi_code', 'pack_size', 'num_packs', 'schedule', 'dosage_form'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('product_unique', 'product', type_='unique')
    op.create_unique_constraint(u'product_unique', 'product', ['regno', 'nappi_code', 'pack_size', 'num_packs', 'schedule', 'is_generic', 'dosage_form'])
    # ### end Alembic commands ###
