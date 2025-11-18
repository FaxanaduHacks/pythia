#!/usr/bin/env python3
"""
pythia.py

Stock price slideshow generator and viewer.

This module retrieves historical price data for a set of tickers, computes
Bollinger Bands and third-sigma envelopes, generates annotated charts, and
presents them through a Tkinter-based slideshow interface. Generated plots are
cached under the graphs/ directory and reused when up to date.
"""

from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import tkinter as tk
from PIL import ImageTk, Image

def progress_bar(current: int, total: int, width: int = 40) -> None:
    """
    Render a minimal progress bar.

    Args:
        current (int): Current iteration index (0-based).
        total (int): Total number of iterations.
        width (int): Width of the bar in characters.
    """
    ratio = (current + 1) / total if total > 0 else 1.0
    filled = int(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    print(f"\r[{bar}] {current + 1}/{total}", end="", flush=True)

class Pythia:
    """
    Stock price chart generator and slideshow presenter.

    Attributes:
        tickers (list[str]): Stock symbols to process and display.
        current_image_index (int): Index of the currently displayed ticker.
        is_playing (bool): Playback state for the slideshow.
        next_image_scheduled (int | None): Tkinter scheduling handle for the
        next image transition.
        window (tk.Tk): Tk root window for the slideshow UI.
        label (tk.Label): Image display widget.
        previous_button (tk.Button): UI control for previous-image navigation.
        play_pause_button (tk.Button): UI control for play/pause state.
        next_button (tk.Button): UI control for next-image navigation.
    """

    def __init__(self, tickers: List[str]) -> None:
        """
        Initialize the slideshow application.

        Args:
            tickers (list[str]): Stock symbols to visualize.
        """
        self.tickers: List[str] = tickers
        self.current_image_index: int = 0
        self.is_playing: bool = True
        self.next_image_scheduled: Optional[int] = None

        self.window: tk.Tk = tk.Tk()
        self.window.title("Stock Price Slideshow")

        self.label: tk.Label = tk.Label(self.window)
        self.label.pack()

        self.previous_button: tk.Button = tk.Button(
            self.window,
            text="Previous",
            command=self.show_previous_image,
        )
        self.previous_button.pack(side="left")

        self.play_pause_button: tk.Button = tk.Button(
            self.window,
            text="Pause",
            command=self.toggle_slideshow,
        )
        self.play_pause_button.pack(side="left")

        self.next_button: tk.Button = tk.Button(
            self.window,
            text="Next",
            command=self.show_next_image,
        )
        self.next_button.pack(side="right")

        self.window.bind("q", self.quit_slideshow)
        self.window.bind("<Escape>", self.quit_slideshow)

    def check_latest_data(self, ticker: str) -> bool:
        """
        Determine whether cached image data for a ticker is current.

        Args:
            ticker (str): Stock symbol.

        Returns:
            bool: True if a plot exists for the previous trading day,
            otherwise False.
        """
        path = f"graphs/{ticker}.png"
        if os.path.exists(path):
            ts = os.path.getmtime(path)
            file_date = datetime.fromtimestamp(ts).date()
            previous_day = datetime.now().date() - timedelta(days=1)
            return file_date == previous_day
        return False

    def is_market_open(self) -> bool:
        """
        Check whether the U.S. market is currently open.

        Returns:
            bool: True if local time is between 09:30 and 16:00.
        """
        now = datetime.now().time()
        open_t = datetime.strptime("09:30", "%H:%M").time()
        close_t = datetime.strptime("16:00", "%H:%M").time()
        return open_t <= now <= close_t

    def get_data_save_plot(self, ticker: str) -> Optional[Tuple[Figure, float]]:
        """
        Retrieve price data, compute analysis overlays, and cache a plot.

        Args:
            ticker (str): Stock symbol.

        Returns:
            Optional[tuple[Figure, float]]: A tuple containing the generated
            Matplotlib figure and the absolute distance between the latest
            closing price and the rolling mean, or None if the plot is
            skipped or data retrieval fails.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=134)

        try:
            data = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), progress=False, auto_adjust=False)
        except Exception as e:
            print(f"Error downloading {ticker}: {e}")
            return None

        if data.empty or "Close" not in data:
            print(f"No valid data for {ticker}, it may be delisted or suspended.")
            return None

        if self.check_latest_data(ticker) and self.is_market_open():
            print(f"Skipping {ticker}: cached data is current.")
            return None

        # Normalize Close to a clean Series:
        close_raw = data["Close"]

        if isinstance(close_raw, pd.DataFrame):
            close = close_raw.iloc[:, 0].astype(float)
        else:
            close = pd.Series(close_raw, dtype=float)

        close = close.copy()
        close.index = pd.to_datetime(close.index)
        close = close[~close.index.duplicated(keep="last")].sort_index()

        # Align the main DataFrame to the normalized close index:
        data = data.copy()
        data.index = pd.to_datetime(data.index)
        data = data[~data.index.duplicated(keep="last")].sort_index()
        data = data.reindex(close.index)

        # Rolling statistics:
        window = 20
        rolling_mean = close.rolling(window=window, min_periods=window).mean()
        sigma = close.rolling(window=window, min_periods=window).std()

        if rolling_mean.dropna().empty:
            print(f"Insufficient data for rolling statistics: {ticker}")
            return None

        boll_high = (rolling_mean + 2 * sigma).astype(float)
        boll_low = (rolling_mean - 2 * sigma).astype(float)
        sig3_high = (rolling_mean + 3 * sigma).astype(float)
        sig3_low = (rolling_mean - 3 * sigma).astype(float)

        data["Rolling Mean"] = rolling_mean
        data["Bollinger High"] = boll_high
        data["Bollinger Low"] = boll_low
        data["Third Sigma High"] = sig3_high
        data["Third Sigma Low"] = sig3_low

        # Buy/sell detection with aligned operands:
        aligned_close_low, aligned_low = close.align(boll_low, join="inner")
        aligned_close_high, aligned_high = close.align(boll_high, join="inner")

        buy_mask = aligned_close_low < aligned_low
        sell_mask = aligned_close_high > aligned_high

        buy_index = buy_mask[buy_mask].index
        sell_index = sell_mask[sell_mask].index

        buy_points = data.loc[buy_index]
        sell_points = data.loc[sell_index]

        # Plot construction:
        fig = Figure(figsize=(10, 5))
        ax = fig.subplots()

        ax.plot(data.index, close, label="Close")
        ax.plot(data.index, data["Rolling Mean"], label="Rolling Mean")
        ax.plot(
            data.index,
            data["Bollinger High"],
            linestyle="--",
            label="Bollinger High",
        )
        ax.plot(
            data.index,
            data["Bollinger Low"],
            linestyle="--",
            label="Bollinger Low",
        )
        ax.plot(
            data.index,
            data["Third Sigma High"],
            linestyle=":",
            label="Third Sigma High",
        )
        ax.plot(
            data.index,
            data["Third Sigma Low"],
            linestyle=":",
            label="Third Sigma Low",
        )

        ax.fill_between(
            data.index,
            data["Bollinger High"],
            data["Bollinger Low"],
            color="grey",
            alpha=0.3,
        )
        ax.fill_between(
            data.index,
            data["Third Sigma High"],
            data["Third Sigma Low"],
            color="grey",
            alpha=0.1,
        )

        ax.scatter(
            buy_points.index,
            buy_points["Close"],
            color="green",
            marker="^",
            label="Buy",
        )
        ax.scatter(
            sell_points.index,
            sell_points["Close"],
            color="red",
            marker="v",
            label="Sell",
        )

        ax.set_title(f"{ticker} Price with Bollinger Bands and Third Sigma")
        ax.legend()
        fig.autofmt_xdate(rotation=45, ha="right")
        ax.tick_params(axis="x", labelsize=8)

        if not os.path.exists("graphs"):
            os.makedirs("graphs")

        fig.savefig(f"graphs/{ticker}.png", dpi=300)
        plt.close(fig)

        dist = abs(close.iloc[-1] - rolling_mean.iloc[-1])
        return fig, dist

    def generate_data_and_plots(self) -> None:
        """
        Generate charts for all tickers and reorder them by signal strength.

        Sorts tickers in descending order of the distance between the latest
        closing price and the rolling mean. Terminates the UI if no images are
        generated.
        """
        ticker_data: List[Tuple[str, float]] = []
        total = len(self.tickers)

        for index, ticker in enumerate(self.tickers):
            progress_bar(index, total)
            result = self.get_data_save_plot(ticker)
            if result is not None:
                _, distance = result
                ticker_data.append((ticker, distance))

        print()

        ticker_data.sort(key=lambda x: x[1], reverse=True)
        self.tickers = [item[0] for item in ticker_data]

        if not ticker_data:
            print("No images were generated. Exiting.")
            self.window.quit()

    def show_image(self, index: int) -> None:
        """
        Display the chart associated with a specific ticker index.

        Args:
            index (int): Position of the ticker in the ticker list.
        """
        ticker = self.tickers[index]
        self.label.config(text="")

        path = f"graphs/{ticker}.png"
        img = Image.open(path).resize((1024, 768), resample=Image.BICUBIC)
        photo = ImageTk.PhotoImage(img)

        self.label.config(image=photo)
        self.label.image = photo

    def schedule_next_image(self) -> None:
        """
        Schedule automatic transition to the next image.

        Uses a five-second delay between transitions when playback is active.
        """
        if self.is_playing:
            self.next_image_scheduled = self.window.after(
                5000,
                self.show_next_image,
            )

    def show_next_image(self) -> None:
        """
        Advance to and display the next ticker chart.
        """
        self.current_image_index = (
            self.current_image_index + 1
        ) % len(self.tickers)
        self.show_image(self.current_image_index)
        self.schedule_next_image()

    def show_previous_image(self) -> None:
        """
        Display the previous ticker chart.
        """
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.tickers) - 1
        self.show_image(self.current_image_index)

    def toggle_slideshow(self) -> None:
        """
        Toggle slideshow playback state.

        Pauses or resumes scheduled image transitions.
        """
        self.is_playing = not self.is_playing
        label = "Play" if not self.is_playing else "Pause"
        self.play_pause_button.config(text=label)

        if self.is_playing:
            self.schedule_next_image()
        else:
            if self.next_image_scheduled is not None:
                self.window.after_cancel(self.next_image_scheduled)
                self.next_image_scheduled = None

    def quit_slideshow(self, event: Optional[tk.Event] = None) -> None:
        """
        Terminate the slideshow and close the user interface.

        Args:
            event (tk.Event | None): Optional Tkinter event object.
        """
        _ = event  # Unused, retained for Tkinter binding signature.
        self.window.quit()

    def start(self) -> None:
        """
        Initialize data generation, display the first image, and start the
        Tkinter event loop.
        """
        self.generate_data_and_plots()
        if self.tickers:
            self.show_image(self.current_image_index)
            self.schedule_next_image()
            self.window.mainloop()
        else:
            print("No tickers available for display. Exiting.")

def main() -> None:
    """
    Entry point for the slideshow application.

    Initializes a predefined list of Dow 30 tickers and starts the UI loop.
    """
    tickers: List[str] = [
        "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT",
        "CRM", "CSCO", "CVX", "DIS", "GS", "HD",
        "HON", "IBM", "JNJ", "JPM", "KO", "MCD",
        "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG",
        "SHW", "TRV", "UNH", "V", "VZ", "WMT"
    ]

    app = Pythia(tickers)
    app.start()

if __name__ == "__main__":
    main()

