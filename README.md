# pythia
A Python stock price slideshow application that fetches historical data,
performs technical analysis with Bollinger Bands and Third Sigma, generates
charts, and presents them in a Tkinter-based slideshow.

This script implements a stock price slideshow application Tkinter for the
graphical user interface (GUI) and Yahoo Finance API (yfinance) for fetching
stock data. The application allows a user to view charts and Bollinger Bands
and Third Sigma for a list of predefined stock tickers. The script downloads
historical stock data, calculates the necessary technical indicators, generates
charts and saves them as images.

The images are displayed in a slideshow allowing the user to navigate to the
next and previous slides. There's also a play/pause button for automated
slideshow progression. The script also provides feedback on teh data
generation process, ensuring that the charts are up-to-date and relevant.

This script is unfinished. It performs a technical analysis on historical data
only. The **Buy** and **Sell** markers are just for demonstrations purposes
and are drawn on historical data: they are not an indicator of when to actually
buy and sell the stocks. This is for educational use only, but if you figure
out how to make millions with it, you could buy me a Winnebago or something.

## Usage

Run with Python or make the script executable, your choice:

```python
python3 pythia.py
```

Note: the program will create a directory named **graphs** for storing the
plot images.

While the script is running:

```
Press q to quit.
```

# Acknowlegdements

The development of this application benefited from the assistance of language
models, including GPT-3.5 and GPT-4, provided by OpenAI. The author
acknowledges the valuable contributions made by these language models in
generating design ideas and providing insights during the development process.
