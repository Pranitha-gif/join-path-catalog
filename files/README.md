# join-path-catalog

Simple base project: a catalog of tables and how they join, with shortest join-path lookup and JOIN SQL generation. Pure Python 3.10+, no dependencies.

## Layout
```
join-path-catalog/
├── join_path_catalog/
│   ├── models.py     # JoinEdge (one join relationship)
│   ├── catalog.py    # JoinPathCatalog: register, find paths, build SQL, save/load JSON
│   ├── cli.py        # command-line interface
│   └── __main__.py
├── build_sample_catalog.py   # creates catalog.json
├── tests/test_catalog.py
└── README.md
```

## Run
```bash
python build_sample_catalog.py                      # creates catalog.json
python -m join_path_catalog list
python -m join_path_catalog path order_items regions
python -m join_path_catalog path order_items regions --all
python -m join_path_catalog sql orders regions categories --select "orders.order_id, regions.region_name"
python -m unittest discover -s tests -v             # run tests
```

## Use as a library
```python
from join_path_catalog import JoinPathCatalog

catalog = JoinPathCatalog.load("catalog.json")
path = catalog.find_path("order_items", "regions")
print(catalog.build_join_sql(["orders", "regions"]))
```

## Ideas for next steps
- Join weights (prefer trusted or indexed joins) with Dijkstra instead of BFS
- Import joins from foreign keys in a real database
- Flag fan-out risk when a path crosses one-to-many joins
- Table aliases for self-joins
