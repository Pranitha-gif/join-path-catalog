import unittest

from join_path_catalog import JoinPathCatalog


def build() -> JoinPathCatalog:
    c = JoinPathCatalog()
    c.add_table("customers", ["customer_id", "region_id"])
    c.add_table("regions", ["region_id"])
    c.add_table("orders", ["order_id", "customer_id"])
    c.add_table("order_items", ["order_id", "product_id"])
    c.add_table("products", ["product_id"])
    c.add_table("lonely", ["id"])
    c.add_join("orders", "customer_id", "customers", "customer_id")
    c.add_join("customers", "region_id", "regions", "region_id")
    c.add_join("order_items", "order_id", "orders", "order_id")
    c.add_join("order_items", "product_id", "products", "product_id")
    return c


class JoinPathCatalogTest(unittest.TestCase):
    def test_shortest_path(self):
        path = build().find_path("order_items", "regions")
        self.assertEqual(
            [e.right_table for e in path], ["orders", "customers", "regions"]
        )

    def test_path_works_in_reverse_direction(self):
        path = build().find_path("regions", "orders")
        self.assertEqual([e.right_table for e in path], ["customers", "orders"])

    def test_no_path(self):
        self.assertIsNone(build().find_path("orders", "lonely"))

    def test_same_table(self):
        self.assertEqual(build().find_path("orders", "orders"), [])

    def test_unknown_table(self):
        with self.assertRaises(ValueError):
            build().find_path("orders", "nope")

    def test_unknown_column_rejected(self):
        c = build()
        with self.assertRaises(ValueError):
            c.add_join("orders", "missing_col", "customers", "customer_id")

    def test_sql_multi_table(self):
        sql = build().build_join_sql(["orders", "regions", "products"])
        self.assertIn("FROM orders", sql)
        self.assertIn("JOIN customers ON orders.customer_id = customers.customer_id", sql)
        self.assertIn("JOIN regions ON customers.region_id = regions.region_id", sql)
        self.assertIn("JOIN products", sql)

    def test_all_paths_finds_alternatives(self):
        c = build()
        c.add_join("orders", "order_id", "regions", "region_id")  # artificial shortcut
        paths = c.find_all_paths("orders", "regions")
        self.assertEqual(len(paths), 2)
        self.assertEqual(len(paths[0]), 1)

    def test_save_and_load_roundtrip(self):
        import tempfile, os
        c = build()
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "c.json")
            c.save(f)
            loaded = JoinPathCatalog.load(f)
        self.assertEqual(loaded.tables(), c.tables())
        self.assertEqual(len(loaded.joins()), len(c.joins()))


if __name__ == "__main__":
    unittest.main()
