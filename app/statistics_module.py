from typing import Any, Dict
import pandas as pd


class StatisticsAnalyzer:
    """Calculate descriptive statistics with explicit input validation."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None or dataframe.empty:
            raise ValueError("A non-empty dataframe is required.")
        self.dataframe = dataframe.copy()

    def numeric_summary(self, column: str) -> Dict[str, float | int]:
        """Return count, mean, median, mode, standard deviation,
        variance, min, max."""
        if column not in self.dataframe.columns:
            raise ValueError(f"Column '{column}' does not exist.")
        series = pd.to_numeric(self.dataframe[column],
                               errors="coerce").dropna()
        if series.empty:
            raise ValueError(f"Column '{column}' has no valid numeric values.")

        modes = series.mode()
        return {
            "count": int(series.count()), "mean": float(series.mean()),
            "median": float(series.median()),
            "mode": float(modes.iloc[0]) if not modes.empty else float("nan"),
            "std": float(series.std(ddof=1)) if len(series) > 1 else 0.0,
            "variance": float(series.var(ddof=1)) if len(series) > 1 else 0.0,
            "min": float(series.min()), "max": float(series.max()),
        }

    def categorical_summary(self, column: str, top_n: int = 10
                            ) -> Dict[str, Any]:
        """Summarise non-null categorical values by count and
        most common value."""
        if column not in self.dataframe.columns:
            raise ValueError(f"Column '{column}' does not exist.")
        series = self.dataframe[column].dropna().astype(str)
        if series.empty:
            raise ValueError(f"Column '{column}' has no valid values.")
        counts = series.value_counts().head(max(1, int(top_n)))
        return {
            "count": int(series.size), "unique": int(series.nunique()),
            "mode": str(counts.index[0]), "top_values": counts.to_dict(),
        }

    def available_numeric_columns(self) -> list[str]:
        """Return columns that contain at least one numeric value."""
        return [
            column for column in self.dataframe.columns
            if pd.to_numeric(self.dataframe[column],
                             errors="coerce").notna().any()
        ]