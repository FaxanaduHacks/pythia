#!/usr/bin/env python3
################################################################################
# File Name:    pythia.py
# Version:      0.1
# Created:      2023-07-16
# Created By:   Faxanadu
# Modified:     2023-07-16
# Modified By:  Faxanadu
# Env Notes:    vi: set expandtab tabstop=4 shiftwidth=4 softtabstop=4
# Synopsis:     This script implements a stock price slideshow application
#               Tkinter for the graphical user interface (GUI) and Yahoo
#               Finance API (yfinance) for fetching stock data. The application
#               allows a user to view charts and Bollinger Bands and Third
#               Sigma for a list of predefined stock tickers. The script
#               downloads historical stock data, calculates the necessary
#               technical indicators, generates charts and saves them as
#               images. The images are displayed in a slideshow allowing the
#               user to navigate to the next and previous slides. There's also
#               a play/pause button for automated slideshow progression. The
#               script also provides feedback on teh data generation process,
#               ensuring that the charts are up-to-date and relevant. This
#               script is unfinished.
# Changelog:    Note - Stack comments oldest to newest.
#               + 2023-07-16 - File created. -Faxanadu
################################################################################

import os                                                                   # For interacting with the operating system.
import yfinance as yf                                                       # Yahoo Finance library for stock data.
from datetime import datetime, timedelta                                    # For working with dates and times.
from matplotlib.figure import Figure                                        # For creating figures and charts.
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas # For rendering figures to images.
import matplotlib.pyplot as plt                                             # For rendering figures to images.
import tkinter as tk                                                        # For creating graphical user interfaces (GUIs).
from PIL import ImageTk, Image                                              # Python Imaging Library for image manipulation.
import tqdm                                                                 # Progress bar library.

# Define a class for the stock price slideshow application:
class Pythia:
    def __init__(self, tickers):
        # Initialize the class with a list of tickers (stock symbols):
        self.tickers = tickers
        self.current_image_index = 0
        self.is_playing = True
        self.next_image_scheduled = None

        # Create a Tkinter window for displaying the slideshow:
        self.window = tk.Tk()
        self.window.title('Stock Price Slideshow')

        # Create a label for displaying stock price charts:
        self.label = tk.Label(self.window)
        self.label.pack()

        # Add buttons for controlling the slideshow:
        self.previous_button = tk.Button(
            self.window, text='Previous', command=self.show_previous_image
        )
        self.previous_button.pack(side='left')

        self.play_pause_button = tk.Button(
            self.window, text='Pause', command=self.toggle_slideshow
        )
        self.play_pause_button.pack(side='left')

        self.next_button = tk.Button(
            self.window, text='Next', command=self.show_next_image
        )
        self.next_button.pack(side='right')

        # Bind keyboard keys to control the slideshow:
        self.window.bind('q', self.quit_slideshow)
        self.window.bind('<Escape>', self.quit_slideshow)

    # Check if data for a given ticker exists and is up-to-date:
    def check_latest_data(self, ticker):
        data_path = f'graphs/{ticker}.png'
        if os.path.exists(data_path):
            file_timestamp = os.path.getmtime(data_path)
            file_date = datetime.fromtimestamp(file_timestamp).date()
            previous_trading_day = datetime.now().date() - timedelta(days=1)
            if file_date == previous_trading_day:
                return True
        return False

    # Check if the stock market is currently open (between 09:30 and 16:00):
    def is_market_open(self):
        now = datetime.now().time()
        market_open = datetime.strptime('09:30', '%H:%M').time()
        market_close = datetime.strptime('16:00', '%H:%M').time()
        return market_open <= now <= market_close

    # Download stock data, plot a chart, and save it as an image:
    def get_data_save_plot(self, ticker):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=134)
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False,
        )

        if data.empty:
            print(f"No data for {ticker}")
            return None

        # Check if the data for the ticker is already up-to-date and if the
        # market is open:
        if self.check_latest_data(ticker) and self.is_market_open():
            print(f"Skipping {ticker} as it already has the latest data.")
            return None

        # Calculate Bollinger Bands and Third Sigma for the stock price:
        window_size = 20
        data['Rolling Mean'] = data['Close'].rolling(window=window_size).mean()
        data['Bollinger High'] = (
            data['Rolling Mean'] + 2 * data['Close'].rolling(window=window_size).std()
        )
        data['Bollinger Low'] = (
            data['Rolling Mean'] - 2 * data['Close'].rolling(window=window_size).std()
        )
        data['Third Sigma High'] = (
            data['Rolling Mean'] + 3 * data['Close'].rolling(window=window_size).std()
        )
        data['Third Sigma Low'] = (
            data['Rolling Mean'] - 3 * data['Close'].rolling(window=window_size).std()
        )

        # Create and customize the stock price chart:
        fig = Figure(figsize=(10, 5))
        ax = fig.subplots()
        ax.plot(data.index, data['Close'], label='Close')
        ax.plot(data.index, data['Rolling Mean'], label='Rolling Mean')
        ax.plot(
            data.index, data['Bollinger High'], label='Bollinger High', linestyle='--'
        )
        ax.plot(
            data.index, data['Bollinger Low'], label='Bollinger Low', linestyle='--'
        )
        ax.plot(
            data.index, data['Third Sigma High'], label='Third Sigma High', linestyle=':'
        )
        ax.plot(
            data.index, data['Third Sigma Low'], label='Third Sigma Low', linestyle=':'
        )
        ax.fill_between(
            data.index,
            data['Bollinger High'],
            data['Bollinger Low'],
            color='grey',
            alpha=0.3,
        )
        ax.fill_between(
            data.index,
            data['Third Sigma High'],
            data['Third Sigma Low'],
            color='grey',
            alpha=0.1,
        )

        # Mark the "Buy" and "Sell" points on the chart:
        buy_points = data[data['Close'] < data['Bollinger Low']]
        sell_points = data[data['Close'] > data['Bollinger High']]
        ax.scatter(
            buy_points.index,
            buy_points['Close'],
            color='green',
            marker='^',
            label='Buy',
        )
        ax.scatter(
            sell_points.index,
            sell_points['Close'],
            color='red',
            marker='v',
            label='Sell',
        )

        ax.set_title(f'{ticker} Price with Bollinger Bands and Third Sigma')
        ax.legend()

        fig.autofmt_xdate(rotation=45, ha='right')
        ax.tick_params(axis='x', labelsize=8)

        # Create a 'graphs' directory if it does not exist:
        if not os.path.exists('graphs'):
            os.makedirs('graphs')

        # Save the chart as an image:
        fig.savefig(f'graphs/{ticker}.png', dpi=300)
        plt.close(fig)

        # Calculate the absolute distance between the latest closing price and
        # the rolling mean:
        absolute_distance = abs(data['Close'].iloc[-1] - data['Rolling Mean'].iloc[-1])
        return fig, absolute_distance

    # Generate data and plots for all tickers and sort them by distance:
    def generate_data_and_plots(self):
        ticker_data = []
        for ticker in tqdm.tqdm(self.tickers):
            output = self.get_data_save_plot(ticker)
            if output is not None:
                fig, distance = output
                ticker_data.append((ticker, distance))

        ticker_data.sort(key=lambda x: x[1], reverse=True)
        self.tickers = [item[0] for item in ticker_data]

        if len(ticker_data) == 0:
            print("No images were generated. Exiting the slideshow.")
            self.window.quit()

    # Display an image with the given index (ticker):
    def show_image(self, index):
        ticker = self.tickers[index]

        self.label.config(text='')

        data_path = f'graphs/{ticker}.png'
        plot_image = Image.open(data_path)
        plot_image = plot_image.resize((1024, 768), resample=Image.BICUBIC)
        photo = ImageTk.PhotoImage(plot_image)

        self.label.config(image=photo)
        self.label.image = photo

    # Schedule the display of the next image in the slideshow:
    def schedule_next_image(self):
        if self.is_playing:
            self.next_image_scheduled = self.window.after(5000, self.show_next_image)

    # Show the next image in the slideshow:
    def show_next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.tickers):
            self.current_image_index = 0
        self.show_image(self.current_image_index)
        self.schedule_next_image()

    # Show the previous image in the slideshow:
    def show_previous_image(self):
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.tickers) - 1
        self.show_image(self.current_image_index)

    # Toggle between play and pause for the slideshow:
    def toggle_slideshow(self):
        self.is_playing = not self.is_playing
        self.play_pause_button.config(text='Play' if not self.is_playing else 'Pause')
        if self.is_playing:
            self.schedule_next_image()
        else:
            self.window.after_cancel(self.next_image_scheduled)

    # Quit the slideshow and close the Tkinter window:
    def quit_slideshow(self, event=None):
        self.window.quit()

    # Start the stock price slideshow application:
    def start(self):
        self.generate_data_and_plots()
        self.show_image(self.current_image_index)
        self.schedule_next_image()
        self.window.mainloop()

# Main function to run the stock price slideshow application:
def main():
    # List of tickers (stock symbols) to display in the slideshow:
    tickers = ['AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 'CRM',
               'CSCO', 'CVX', 'DOW', 'DIS', 'HD', 'HON',
               'GS', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO',
               'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PG',
               'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT']

    # Create an instance of the Pythia class and start the slideshow:
    app = Pythia(tickers)
    app.start()

# Run the main function if the script is executed directly:
if __name__ == '__main__':
    main()

