import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class ChartView:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.canvas = None

    def show_player_sport_trend(self, df, metric="Speed"):
        # clear area
        for w in self.parent_frame.winfo_children():
            w.destroy()

        if df is None or df.empty:
            import tkinter as tk
            tk.Label(self.parent_frame, text="No records to plot", bg="white").pack(pady=20)
            return

        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date")

        fig, ax = plt.subplots(figsize=(8,3), dpi=100)
        if metric in df.columns:
            ax.plot(df["Date"], df[metric], marker="o", linestyle="-", linewidth=2)
            ax.set_ylabel(metric)
        else:
            ax.plot(df["Date"], df["Speed"], marker="o", linestyle="-", linewidth=2)
            ax.set_ylabel("Speed")

        ax.set_xlabel("Date")
        ax.set_title(f"{metric} over time")
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
