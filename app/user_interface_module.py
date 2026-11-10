"""Tkinter graphical user interface for music similarity analysis."""

import tkinter as tk
from tkinter import ttk, messagebox

from app.similarity_module import RecommendationEngine
from app.statistics_module import StatisticsAnalyzer


class MusicSimilarityApp:
    """Provide a simple GUI for track/artist similarity and recommendations."""

    def __init__(self, root: tk.Tk, engine: RecommendationEngine, dataframe
                 ) -> None:
        self.root = root
        self.engine = engine
        self.dataframe = dataframe
        self.root.title("Music Similarity Explorer")
        self.root.geometry("900x650")
        self.root.minsize(720, 520)
        self.metric_var = tk.StringVar(value="cosine")
        self.mode_var = tk.StringVar(value="Track")
        self.query_var = tk.StringVar()
        self.second_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Music Similarity Explorer",
                  font=("TkDefaultFont", 18, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Compare tracks or artists and discover the five closest matches.",
        ).pack(anchor="w", pady=(2, 12))

        controls = ttk.LabelFrame(outer, text="Analysis settings", padding=12)
        controls.pack(fill="x", pady=(0, 12))

        row1 = ttk.Frame(controls)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="Compare:").pack(side="left")
        mode = ttk.Combobox(row1, textvariable=self.mode_var,
                            values=("Track", "Artist"), state="readonly",
                            width=12)
        mode.pack(side="left", padx=(6, 18))
        mode.bind("<<ComboboxSelected>>", self._update_labels)
        ttk.Label(row1, text="Metric:").pack(side="left")
        ttk.Combobox(
            row1, textvariable=self.metric_var,
            values=("cosine", "pearson", "euclidean", "manhattan"),
            state="readonly", width=14,
        ).pack(side="left", padx=6)

        row2 = ttk.Frame(controls)
        row2.pack(fill="x", pady=4)
        self.query_label = ttk.Label(row2, text="Track ID:")
        self.query_label.pack(side="left")
        self.query_entry = ttk.Entry(row2, textvariable=self.query_var,
                                     width=28)
        self.query_entry.pack(side="left", padx=(6, 16), fill="x", expand=True)
        self.second_label = ttk.Label(row2, text="Compare with ID:")
        self.second_label.pack(side="left")
        self.second_entry = ttk.Entry(row2, textvariable=self.second_var,
                                      width=28)
        self.second_entry.pack(side="left", padx=6, fill="x", expand=True)

        actions = ttk.Frame(controls)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Find Similar Items",
                   command=self._run_recommendations).pack(side="left")
        ttk.Button(actions, text="Compare Two",
                   command=self._compare_two).pack(side="left", padx=8)
        ttk.Button(actions, text="Dataset Statistics",
                   command=self._show_statistics).pack(side="left")
        ttk.Button(actions, text="Clear Results",
                   command=self._clear).pack(side="left", padx=8)
        ttk.Button(actions, text="Quit",
                   command=self.root.destroy).pack(side="right")

        results_frame = ttk.LabelFrame(outer, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True)
        self.output = tk.Text(results_frame, wrap="word", height=18,
                              state="disabled", font=("TkFixedFont", 10))
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical",
                                  command=self.output.yview)
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.status_var = tk.StringVar(
            value=f"Loaded {len(self.engine.records)} tracks.")
        ttk.Label(outer, textvariable=self.status_var, relief="sunken",
                  anchor="w").pack(fill="x", pady=(8, 0))

    def _update_labels(self, _event=None) -> None:
        is_track = self.mode_var.get() == "Track"
        self.query_label.configure(text="Track ID:" if is_track
                                   else "Artist name:")
        self.second_label.configure(text="Compare with ID:" if is_track
                                    else "Compare with artist:")
        self.query_entry.configure(width=28)
        self.second_entry.configure(width=28)

    def _write(self, content: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", content)
        self.output.configure(state="disabled")

    def _run_recommendations(self) -> None:
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Input required",
                                   "Enter a track ID or artist name first.")
            return
        metric = self.metric_var.get()
        try:
            if self.mode_var.get() == "Track":
                items = self.engine.top_similar_tracks(query, metric, 5)
                lines = [f"Top similar tracks to ID {query} using"
                         f"{metric.title()} similarity: ", ""]
                lines += [f"{i}. {item['label']}\n"
                          f"Similarity: {item['score']:.4f}"
                          for i, item in enumerate(items, 1)]
            else:
                items = self.engine.top_similar_artists(query, metric, 5)
                lines = [f"Top similar artists to {query} using"
                         f"{metric.title()} similarity: ", ""]
                lines += [f"{i}. {item['artist_name']} — similarity "
                          f"{item['score']:.4f}"
                          for i, item in enumerate(items, 1)]
            if not items:
                lines.append("No other items are available to recommend.")
            self._write("\n\n".join(lines))
            self.status_var.set("Completed recommendation search using %s."
                                 % metric)
        except ValueError as exc:
            messagebox.showerror("Could not calculate similarity", str(exc))
            self.status_var.set("Please correct the input and try again.")

    def _compare_two(self) -> None:
        first, second = (self.query_var.get().strip(),
                         self.second_var.get().strip())
        if not first or not second:
            messagebox.showwarning("Input required",
                                   "Fill in both input fields to compare two items.")
            return
        metric = self.metric_var.get()
        try:
            if self.mode_var.get() == "Track":
                result = self.engine.track_similarity(first, second, metric)
            else:
                result = self.engine.artist_similarity(first, second, metric)
            self._write(
                f"{result['metric'].title()} similarity\n\n"
                f"First:  {result['first']}\nSecond: {result['second']}\n\n"
                f"Score: {result['score']:.4f} "
                "(0 = lower similarity, 1 = higher similarity)"
            )
            self.status_var.set("Comparison completed.")
        except ValueError as exc:
            messagebox.showerror("Could not compare items", str(exc))
            self.status_var.set("Please correct the input and try again.")

    def _show_statistics(self) -> None:
        try:
            analyzer = StatisticsAnalyzer(self.dataframe)
            numeric = analyzer.available_numeric_columns()
            lines = ["Descriptive statistics", ""]
            for column in numeric[:12]:
                try:
                    summary = analyzer.numeric_summary(column)
                    lines.append(
                        f"{column}: n={summary['count']}, mean={summary['mean']:.3f}, "
                        f"median={summary['median']:.3f}, std={summary['std']:.3f}, "
                        f"min={summary['min']:.3f}, max={summary['max']:.3f}"
                    )
                except ValueError:
                    continue
            self._write("\n".join(lines))
            self.status_var.set("Statistics calculated.")
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Statistics unavailable", str(exc))

    def _clear(self) -> None:
        self._write("")
        self.status_var.set("Results cleared.")