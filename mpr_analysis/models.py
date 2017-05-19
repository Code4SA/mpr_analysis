from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
import re

Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    nappi_code = Column(String, nullable=False)
    regno = Column(String, nullable=False)
    name = Column(String, nullable=False)
    schedule = Column(String)
    dosage_form = Column(String)
    pack_size = Column(Float, nullable=False)
    is_generic = Column(String)
    num_packs = Column(Integer)
    ingredients = relationship("ProductIngredient", back_populates="product")
    prices = relationship("ProductSEP", back_populates="product")

    __table_args__ = (
        UniqueConstraint('regno', 'nappi_code', 'pack_size', 'num_packs', 'schedule', 'is_generic', 'dosage_form', name='product_unique'),
    )

    # related products
    # ----------------
    # products that have the same set of ingredients with the same strength
    @property
    def equivalence_key(self):
        ingredients = []
        for pi in self.ingredients:
            fields = [pi.ingredient.name, pi.strength, pi.ingredient.unit]
            id = re.sub("[^\w/%-]", "-", "-".join(fields))
            id = id.lower()
            ingredients.append(id)
        return "-".join(sorted(ingredients))

    def __repr__(self):
        return ("<Product: %s>" % self.name).encode('utf-8')


class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    products = relationship("ProductIngredient",
                            back_populates="ingredient")
    __table_args__ = (
        UniqueConstraint('name', 'unit', name='ingredient_unique_name_unit'),
    )

    def __repr__(self):
        return "<Ingredient: %s>" % self.name


class ProductIngredient(Base):
    __tablename__ = 'product_ingredient'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'))
    strength = Column(String, nullable=False)
    product = relationship("Product", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="products")
    __table_args__ = (
        UniqueConstraint('product_id', 'ingredient_id', 'strength', name='product_ingredient_unique_product_ingredient_strength'),
    )
    def __unicode__(self):
        return "%s %s" % (self.ingredient, self.strength)

    def __repr__(self):
        return "<ProductIngredient: %s %s %s>" % (self.product.name, self.ingredient.name, self.strength)


class ProductSEP(Base):
    __tablename__ = 'product_sep'
    id = Column(Integer, primary_key=True)
    sep = Column(Float, nullable=False)
    effective_date = Column(Date)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return "<ProductSEP: %s %s>" % (self.product.name, self.sep)
