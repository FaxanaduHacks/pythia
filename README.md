# pythia

A Python stock price slideshow application that fetches historical data, performs technical analysis with Bollinger Bands and Third Sigma, generates charts, and presents them in a Tkinter-based slideshow.

This script implements a stock price slideshow application Tkinter for the graphical user interface (GUI) and Yahoo Finance API (yfinance) for fetching stock data. The application allows a user to view charts and Bollinger Bands and Third Sigma for a list of predefined stock tickers. The script downloads historical stock data, calculates the necessary technical indicators, generates charts and saves them as images. 

The images are displayed in a slideshow allowing the user to navigate to the next and previous slides. There's also a play/pause button for automated slideshow progression. The script also provides feedback on teh data generation process, ensuring that the charts are up-to-date and relevant.

This script is unfinished. It performs a technical analysis on historical data only. The **Buy** and **Sell** markers are just for demonstrations purposes and are drawn on historical data: they are not an indicator of when to actually buy and sell the stocks. This is for educational use only, but if you figure out how to make millions with it, you could buy me a Winnebago or something.

## Prerequisites

Before running the program, make sure you have the following prerequisites:

- Python 3.x
- The following Python libraries: `os`, `yfinance`, `datetime`, `matplotlib`, `tkinter`, `PIL`, `tqdm`

You can install the required libraries using the following command:

```bash
pip install yfinance matplotlib pillow tqdm
```

## Features



## Usage

1. Clone this repository or download the source code.
2. Open a terminal and navigate to the directory containing the downloaded code.
3. Run the following command to execute the program:

```bash
python pythia.py
```

Note: the program will create a directory named **graphs** for storing the
plot images.

While the script is running:

```
Press q to quit.
```

## Configuration

You can customize the list of tickers to be displayed in the slideshow by modifying the tickers list in the main function of the slideshow_app.py script.

## Contribution

Contributions to this project are welcome! If you encounter any issues, have ideas for improvements, or want to add new features, feel free to submit a pull request or open an issue.

## License

This barcode scanner is open-source and licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

This program utilizes the OpenCV library for computer vision tasks. Credits to the OpenCV community for their contributions.

The development of this application benefited from the assistance of language models, including GPT-3.5 and GPT-4, provided by OpenAI. The author acknowledges the valuable contributions made by these language models in generating design ideas and providing insights during the development process.
