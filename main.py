"""Application entry point and dataset configuration."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from app.load_dataset_module import DatasetLoader
from app.similarity_module import RecommendationEngine
from app.user_interface_module import MusicSimilarityApp


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "data.csv"

ID_COLUMN = "id"
TRACK_NAME_COLUMN = "name"
ARTIST_COLUMN = "artists"


def main() -> None:
    try:
        # Load data and initialize engine BEFORE starting Tkinter
        loader = DatasetLoader(data_path=str(DATASET_PATH),
                               id_column=ID_COLUMN)

        dataframe = loader.load_data()
        records = loader.get_record()

        engine = RecommendationEngine(
            records,
            feature_columns=list(dataframe.columns),
            id_column=ID_COLUMN,
            artist_column=ARTIST_COLUMN,
            track_name_column=TRACK_NAME_COLUMN,
        )

        # Initialize the GUI only after data is ready
        root = tk.Tk()
        MusicSimilarityApp(root, engine, dataframe)
        root.mainloop()

    except (FileNotFoundError, ValueError, KeyError) as exc:
        # Create a temporary root just to show the error message
        err_root = tk.Tk()
        err_root.withdraw()
        messagebox.showerror(
            "Application startup error",
            str(exc)
        )
        err_root.destroy()
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
