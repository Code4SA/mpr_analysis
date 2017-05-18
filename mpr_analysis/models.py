from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    nappi_code = Column(String, unique=True, nullable=False)
    regno = Column(String, nullable=False)
    name = Column(String, nullable=False)
    schedule = Column(String)
    dosage_form = Column(String)
    pack_size = Column(Float, nullable=False)
    is_generic = Column(String)
    num_packs = Column(Integer)
    ingredients = relationship("ProductIngredient",
                               back_populates="product")
    prices = relationship("ProductSEP", back_populates="product")

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<Product: %s>" % self.name


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
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True)
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
