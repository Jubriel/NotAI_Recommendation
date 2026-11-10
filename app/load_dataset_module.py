from pathlib import Path
import ast
import pandas as pd
from typing import Dict, Any


class DatasetLoader:

    DEFAULT_REQUIRED_COLUMNS = ["id", "name", "artists"]
    DEFAULT_NUMERIC_COLUMNS = [
        "danceability", "energy", "valence", "tempo", "acousticness", "key",
        "mode",
        "instrumentalness", "liveness", "speechiness", "popularity",
        "loudness", "duration_ms",
    ]

    def __init__(self, data_path: str, id_column: str = "id"):
        self.data_path = Path(data_path)
        self.df: pd.DataFrame = None
        self.records: Dict[str, Dict[str, Any]] = {}
        self.id_column: str = id_column

    def load_data(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        self.df = self.clean_data()
        self.validate_data()
        return self.df

    def clean_data(self) -> pd.DataFrame:
        try:
            if self.df is None or self.df.columns.empty:
                raise ValueError("No data loaded.")

            self.df = self.df.dropna()
            self.df = self.df.drop_duplicates()

            def _parse_artists(value):
                try:
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, (list, tuple)):
                        return ", ".join(str(a) for a in parsed)
                except (ValueError, SyntaxError):
                    pass
                return str(value)

            self.df["artists"] = self.df["artists"].apply(_parse_artists)
            self.df[self.DEFAULT_NUMERIC_COLUMNS] = self.df[
                self.DEFAULT_NUMERIC_COLUMNS].apply(pd.to_numeric,
                                                    errors='coerce')
            return self.df
        except Exception as e:
            raise ValueError(f"Error cleaning data: {e}")

    def validate_data(self) -> bool:
        missing_columns = pd.Index(self.DEFAULT_REQUIRED_COLUMNS).difference(
            self.df.columns)

        if not missing_columns.empty:
            raise ValueError(
                f"Missing required columns: {missing_columns.tolist()}")

        return True

    def get_record(self) -> Dict[str, Any]:
        if self.df is None:
            raise ValueError("No data loaded. Please load data first.")
        self.records = self.df.set_index(self.id_column,
                                         drop=False).to_dict("index")
        return self.records
