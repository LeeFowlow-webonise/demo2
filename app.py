from datetime import datetime, timedelta
import io
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yfinance as yf
from flask import Flask, render_template, request

app = Flask(__name__)


def fetch_last_week(ticker: str):
    end = datetime.now().date()
    start = end - timedelta(days=7)
    data = yf.download(
        ticker.upper(),
        start=start,
        end=end + timedelta(days=1),
        progress=False,
    )
    return data


def get_close_prices(data):
    close = data["Close"]
    if hasattr(close, "squeeze"):
        close = close.squeeze()
    return close.dropna()


def plot_to_base64(close, ticker: str) -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(close.index, close.values, color="#2563eb", linewidth=2)
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price (USD)")
    ax.set_title(f"{ticker.upper()} — Last 7 Days")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def index():
    ticker = request.form.get("ticker", "").strip().upper()
    chart = None
    error = None
    rows = None

    if request.method == "POST":
        if not ticker:
            error = "Please enter a stock ticker."
        else:
            try:
                data = fetch_last_week(ticker)
                close = get_close_prices(data)

                if close.empty:
                    error = f"No data found for ticker '{ticker}'."
                else:
                    chart = plot_to_base64(close, ticker)
                    rows = [
                        {
                            "date": date.strftime("%Y-%m-%d"),
                            "close": f"${price:.2f}",
                        }
                        for date, price in close.items()
                    ]
            except Exception:
                error = f"Could not fetch data for ticker '{ticker}'."

    return render_template(
        "index.html",
        ticker=ticker,
        chart=chart,
        error=error,
        rows=rows,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
