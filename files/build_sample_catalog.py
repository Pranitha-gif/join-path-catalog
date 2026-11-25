"""Builds catalog.json with a small sales-style sample model."""
from join_path_catalog import JoinPathCatalog

c = JoinPathCatalog()
c.add_table("customers", ["customer_id", "name", "region_id"])
c.add_table("regions", ["region_id", "region_name"])
c.add_table("orders", ["order_id", "customer_id", "order_date"])
c.add_table("order_items", ["order_item_id", "order_id", "product_id", "quantity"])
c.add_table("products", ["product_id", "product_name", "category_id"])
c.add_table("categories", ["category_id", "category_name"])

c.add_join("orders", "customer_id", "customers", "customer_id")
c.add_join("customers", "region_id", "regions", "region_id")
c.add_join("order_items", "order_id", "orders", "order_id")
c.add_join("order_items", "product_id", "products", "product_id")
c.add_join("products", "category_id", "categories", "category_id")

c.save("catalog.json")
print("Wrote catalog.json")
