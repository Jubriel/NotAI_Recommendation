from typing import Iterable, Any, Dict
import numpy as np


class SimilarityCalculator:
    """Calculate four similarity scores, each bounded between zero and one."""

    METRICS = ("cosine", "pearson", "euclidean", "manhattan")

    @staticmethod
    def _vectors(left: Iterable[float], right: Iterable[float]
                 ) -> tuple[np.ndarray, np.ndarray]:
        try:
            a = np.asarray(list(left), dtype=float)
            b = np.asarray(list(right), dtype=float)
        except (TypeError, ValueError) as exc:
            raise exc
        return a, b

    @classmethod
    def cosine_similarity(cls, left: Iterable[float], right: Iterable[float]
                          ) -> float:
        """Map cosine similarity from [-1, 1] to [0, 1]."""
        a, b = cls._vectors(left, right)
        denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denominator == 0:
            return 0.0
        raw = float(np.dot(a, b) / denominator)
        return float(np.clip((raw + 1.0) / 2.0, 0.0, 1.0))

    @classmethod
    def pearson_similarity(cls, left: Iterable[float], right: Iterable[float]
                           ) -> float:
        """Map Pearson correlation from [-1, 1] to [0, 1]."""
        a, b = cls._vectors(left, right)
        if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
            return 0.0
        raw = float(np.corrcoef(a, b)[0, 1])
        if not np.isfinite(raw):
            return 0.0
        return float(np.clip((raw + 1.0) / 2.0, 0.0, 1.0))

    @classmethod
    def euclidean_similarity(cls, left: Iterable[float], right: Iterable[float]
                             ) -> float:
        """Convert Euclidean distance to a bounded similarity score."""
        a, b = cls._vectors(left, right)
        return float(1.0 / (1.0 + np.linalg.norm(a - b)))

    @classmethod
    def manhattan_similarity(cls, left: Iterable[float], right: Iterable[float]
                             ) -> float:
        """Convert Manhattan distance to a bounded similarity score."""
        a, b = cls._vectors(left, right)
        return float(1.0 / (1.0 + np.abs(a - b).sum()))

    @classmethod
    def calculate(cls, metric: str, left: Iterable[float],
                  right: Iterable[float]) -> float:
        """Dispatch a metric by name."""
        methods = {
            "cosine": cls.cosine_similarity,
            "pearson": cls.pearson_similarity,
            "euclidean": cls.euclidean_similarity,
            "manhattan": cls.manhattan_similarity,
        }
        key = metric.strip().lower()
        if key not in methods:
            raise (f"Unknown metric '{metric}'. Choose: {', '.join(cls.METRICS)}.")
        return methods[key](left, right)


class RecommendationEngine:
    """Compare tracks or artists using shared numeric audio features."""

    DEFAULT_FEATURES = (
        "danceability", "energy", "valence", "tempo", "acousticness",
        "instrumentalness", "liveness", "speechiness", "popularity",
    )

    def __init__(self, records: Dict[str, Any],
                 feature_columns: Iterable[str] | None = None,
                 id_column: str = "track_id",
                 artist_column: str = "artist_name",
                 track_name_column: str = "track_name") -> None:
        if not records:
            raise ValueError("At least one dataset record is required.")
        self.records = records
        self.id_column = id_column
        self.artist_column = artist_column
        self.track_name_column = track_name_column
        first = next(iter(records.values()))
        candidates = list(feature_columns or self.DEFAULT_FEATURES)
        self.feature_columns = [
            col for col in candidates
            if col in first and self._has_numeric_value(col)
        ]
        if not self.feature_columns:
            raise ValueError(
                "No usable numeric features found. Check feature columns"
                "and the dataset schema."
            )
        self.calculator = SimilarityCalculator()
        self._scaled_vectors = self._build_scaled_vectors()

    def _has_numeric_value(self, column: str) -> bool:
        for record in self.records.values():
            try:
                value = float(record.get(column))
                if np.isfinite(value):
                    return True
            except (TypeError, ValueError):
                continue
        return False

    def _build_scaled_vectors(self) -> dict[str, np.ndarray]:
        """Min-max scale each feature; missing values use the feature median.
        """
        ids = list(self.records)
        matrix = []
        for track_id in ids:
            values = []
            for feature in self.feature_columns:
                try:
                    value = float(self.records[track_id].get(feature))
                    values.append(value if np.isfinite(value) else np.nan)
                except (TypeError, ValueError):
                    values.append(np.nan)
            matrix.append(values)
        array = np.asarray(matrix, dtype=float)
        for col in range(array.shape[1]):
            valid = array[:, col][np.isfinite(array[:, col])]
            median = float(np.median(valid)) if len(valid) else 0.0
            array[~np.isfinite(array[:, col]), col] = median
            minimum, maximum = float(array[:, col].min()), float(array[:, col].max())
            if maximum > minimum:
                array[:, col] = (array[:, col] - minimum) / (maximum - minimum)
            else:
                array[:, col] = 0.0
        return {track_id: array[index] for index, track_id in enumerate(ids)}

    def _score(self, left_id: str, right_id: str, metric: str) -> float:
        return self.calculator.calculate(metric, self._scaled_vectors[left_id],
                                         self._scaled_vectors[right_id])

    def _track_label(self, track_id: str) -> str:
        record = self.records[track_id]
        name = record.get(self.track_name_column) or "Unknown track"
        artist = record.get(self.artist_column) or "Unknown artist"
        return f"{name} — {artist} (ID: {track_id})"

    def track_similarity(self, first_id: str, second_id: str,
                         metric: str = "cosine") -> dict[str, Any]:
        """Return a score and display labels for two track IDs."""
        first_id, second_id = str(first_id).strip(), str(second_id).strip()
        for track_id in (first_id, second_id):
            if track_id not in self.records:
                raise (f"Track ID '{track_id}' was not found.")
        return {
            "first": self._track_label(first_id),
            "second": self._track_label(second_id),
            "score": self._score(first_id, second_id, metric),
            "metric": metric.lower(),
        }

    def top_similar_tracks(self, track_id: str, metric: str = "cosine",
                           limit: int = 5) -> list[dict[str, Any]]:
        """Return the highest-scoring other tracks for a given track ID."""
        track_id = str(track_id).strip()
        if track_id not in self.records:
            raise (f"Track ID '{track_id}' was not found.")
        if limit < 1:
            raise ("Recommendation limit must be at least 1.")
        ranked = [
            (self._score(track_id, other_id, metric), other_id)
            for other_id in self.records if other_id != track_id
        ]
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [
            {"track_id": other_id, "label": self._track_label(other_id),
             "score": score}
            for score, other_id in ranked[:limit]
        ]

    def artist_similarity(self, first_artist: str, second_artist: str,
                          metric: str = "cosine") -> dict[str, Any]:
        """Compare artists by the mean feature vector of their tracks."""
        first_artist, second_artist = first_artist.strip(), second_artist.strip()
        artist_vectors = self._artist_vectors()
        if first_artist not in artist_vectors:
            raise (f"Artist '{first_artist}' was not found.")
        if second_artist not in artist_vectors:
            raise (f"Artist '{second_artist}' was not found.")
        score = self.calculator.calculate(metric, artist_vectors[first_artist],
                                          artist_vectors[second_artist])
        return {"first": first_artist, "second": second_artist, "score": score,
                "metric": metric.lower()}

    def _artist_vectors(self) -> dict[str, np.ndarray]:
        groups: dict[str, list[np.ndarray]] = {}
        for track_id, record in self.records.items():
            artist = record.get(self.artist_column)
            if artist is not None and str(artist).strip():
                groups.setdefault(str(artist).strip(), []).append(
                    self._scaled_vectors[track_id])
        return {artist: np.mean(vectors, axis=0)
                for artist, vectors in groups.items()}

    def top_similar_artists(self, artist: str, metric: str = "cosine",
                            limit: int = 5) -> list[dict[str, Any]]:
        """Rank artists by similarity to the average feature
        vector of a given artist."""
        artist = artist.strip()
        vectors = self._artist_vectors()
        if artist not in vectors:
            raise (f"Artist '{artist}' was not found.")
        if limit < 1:
            raise ("Recommendation limit must be at least 1.")
        ranked = [
            (self.calculator.calculate(metric, vectors[artist], vector), other)
            for other, vector in vectors.items() if other != artist
        ]
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [
            {"artist_name": other, "label": other, "score": score}
            for score, other in ranked[:limit]
        ]