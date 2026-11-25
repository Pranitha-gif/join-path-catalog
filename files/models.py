from dataclasses import dataclass

_FLIP = {
    "many-to-one": "one-to-many",
    "one-to-many": "many-to-one",
    "one-to-one": "one-to-one",
    "many-to-many": "many-to-many",
}


@dataclass(frozen=True)
class JoinEdge:
    """A join relationship from left_table to right_table."""

    left_table: str
    left_column: str
    right_table: str
    right_column: str
    join_type: str = "INNER"
    cardinality: str = "many-to-one"  # describes left -> right

    def reversed(self) -> "JoinEdge":
        """The same relationship seen from the other table."""
        return JoinEdge(
            self.right_table,
            self.right_column,
            self.left_table,
            self.left_column,
            self.join_type,
            _FLIP[self.cardinality],
        )

    def on_clause(self) -> str:
        return (
            f"{self.left_table}.{self.left_column} = "
            f"{self.right_table}.{self.right_column}"
        )

    def __str__(self) -> str:
        return f"{self.left_table}.{self.left_column} -> {self.right_table}.{self.right_column}"
