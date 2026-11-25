import json
from collections import deque
from pathlib import Path

from .models import _FLIP, JoinEdge


class JoinPathCatalog:
    """Registry of tables and how they join, with join-path lookup."""

    def __init__(self):
        self._tables: dict[str, set[str]] = {}
        self._graph: dict[str, list[JoinEdge]] = {}
        self._joins: list[JoinEdge] = []

    # ---------- registration ----------
    def add_table(self, name: str, columns: list[str]) -> None:
        self._tables[name] = set(columns)
        self._graph.setdefault(name, [])

    def add_join(
        self,
        left_table: str,
        left_column: str,
        right_table: str,
        right_column: str,
        join_type: str = "INNER",
        cardinality: str = "many-to-one",
    ) -> None:
        for table, column in ((left_table, left_column), (right_table, right_column)):
            if table not in self._tables:
                raise ValueError(f"Unknown table: {table}")
            if column not in self._tables[table]:
                raise ValueError(f"Unknown column: {table}.{column}")
        if cardinality not in _FLIP:
            raise ValueError(f"Unknown cardinality: {cardinality}")

        edge = JoinEdge(left_table, left_column, right_table, right_column, join_type, cardinality)
        self._joins.append(edge)
        self._graph[left_table].append(edge)
        self._graph[right_table].append(edge.reversed())

    # ---------- lookup ----------
    def tables(self) -> list[str]:
        return sorted(self._tables)

    def joins(self) -> list[JoinEdge]:
        """Every relationship once, in the direction it was registered."""
        return list(self._joins)

    def find_path(self, source: str, target: str) -> list[JoinEdge] | None:
        """Shortest join path (fewest joins) from source to target, or None."""
        self._check_tables(source, target)
        if source == target:
            return []

        queue = deque([(source, [])])
        visited = {source}
        while queue:
            table, path = queue.popleft()
            for edge in self._graph[table]:
                nxt = edge.right_table
                if nxt in visited:
                    continue
                new_path = path + [edge]
                if nxt == target:
                    return new_path
                visited.add(nxt)
                queue.append((nxt, new_path))
        return None

    def find_all_paths(self, source: str, target: str, max_joins: int = 4) -> list[list[JoinEdge]]:
        """All simple paths up to max_joins joins, shortest first."""
        self._check_tables(source, target)
        results: list[list[JoinEdge]] = []

        def walk(table: str, path: list[JoinEdge], seen: set[str]) -> None:
            if table == target:
                results.append(list(path))
                return
            if len(path) >= max_joins:
                return
            for edge in self._graph[table]:
                if edge.right_table not in seen:
                    path.append(edge)
                    walk(edge.right_table, path, seen | {edge.right_table})
                    path.pop()

        walk(source, [], {source})
        return sorted(results, key=len)

    # ---------- SQL generation ----------
    def build_join_sql(self, tables: list[str], select: str = "*") -> str:
        """SQL that connects all given tables, starting from the first one."""
        if not tables:
            raise ValueError("Provide at least one table")
        self._check_tables(*tables)

        included = [tables[0]]
        edges_used: list[JoinEdge] = []
        for target in tables[1:]:
            if target in included:
                continue
            best = None
            for start in included:
                path = self.find_path(start, target)
                if path is not None and (best is None or len(path) < len(best)):
                    best = path
            if best is None:
                raise ValueError(f"No join path from {included} to {target}")
            for edge in best:
                if edge.right_table not in included:
                    included.append(edge.right_table)
                    edges_used.append(edge)

        lines = [f"SELECT {select}", f"FROM {tables[0]}"]
        for e in edges_used:
            lines.append(f"{e.join_type} JOIN {e.right_table} ON {e.on_clause()}")
        return "\n".join(lines) + ";"

    # ---------- persistence ----------
    def save(self, file: str | Path) -> None:
        data = {
            "tables": {name: sorted(cols) for name, cols in self._tables.items()},
            "joins": [
                {
                    "left_table": e.left_table,
                    "left_column": e.left_column,
                    "right_table": e.right_table,
                    "right_column": e.right_column,
                    "join_type": e.join_type,
                    "cardinality": e.cardinality,
                }
                for e in self.joins()
            ],
        }
        Path(file).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, file: str | Path) -> "JoinPathCatalog":
        data = json.loads(Path(file).read_text(encoding="utf-8"))
        catalog = cls()
        for name, columns in data["tables"].items():
            catalog.add_table(name, columns)
        for j in data["joins"]:
            catalog.add_join(**j)
        return catalog

    def _check_tables(self, *names: str) -> None:
        for name in names:
            if name not in self._tables:
                raise ValueError(f"Unknown table: {name}")
