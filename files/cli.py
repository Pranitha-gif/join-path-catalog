import argparse
import sys

from .catalog import JoinPathCatalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="join-path-catalog", description="Find join paths between tables.")
    parser.add_argument("--catalog", default="catalog.json", help="Path to catalog JSON file")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List tables and registered joins")

    p_path = sub.add_parser("path", help="Show join paths between two tables")
    p_path.add_argument("source")
    p_path.add_argument("target")
    p_path.add_argument("--all", action="store_true", help="Show all paths, not just the shortest")

    p_sql = sub.add_parser("sql", help="Generate JOIN SQL connecting tables")
    p_sql.add_argument("tables", nargs="+")
    p_sql.add_argument("--select", default="*")

    args = parser.parse_args(argv)

    try:
        catalog = JoinPathCatalog.load(args.catalog)

        if args.command == "list":
            print("Tables:")
            for t in catalog.tables():
                print(f"  {t}")
            print("Joins:")
            for e in catalog.joins():
                print(f"  {e}  [{e.join_type}, {e.cardinality}]")

        elif args.command == "path":
            if args.all:
                paths = catalog.find_all_paths(args.source, args.target)
            else:
                shortest = catalog.find_path(args.source, args.target)
                paths = [shortest] if shortest is not None else []
            if not paths:
                print(f"No join path from {args.source} to {args.target}")
                return 1
            for i, path in enumerate(paths, 1):
                print(f"Path {i} ({len(path)} joins):")
                for edge in path:
                    print(f"  {edge}")

        elif args.command == "sql":
            print(catalog.build_join_sql(args.tables, args.select))

    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
