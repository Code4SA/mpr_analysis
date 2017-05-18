-- price changes
with changes as (with price_counts as (select product.id, nappi_code, name, pack_size, is_generic, count(sep.id) from product, product_sep as sep where product.id = sep.product_id group by product.id, nappi_code, name, pack_size, is_generic) select * from price_counts where count > 1) select nappi_code, name, pack_size, is_generic, sep, effective_date from changes, product_sep where changes.id = product_sep.product_id order by nappi_code, effective_date;
