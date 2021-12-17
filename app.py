"""
App builder
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from utils.risk_measure import Portfolio, RiskMeasures

matplotlib.use("TkAgg")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class App(ttk.Frame):
    options = {"padx": 5, "pady": 5}

    def __init__(self, container):
        super().__init__(container)

        self.tickers_label = ttk.Label(self, text="Portfolio Stocks (insert tickers): ")
        self.tickers_label.grid(column=0, row=0, sticky="e", **App.options)
        self.tickers = tk.StringVar()
        self.tickers_entry = ttk.Entry(self, textvariable=self.tickers)
        self.tickers_entry.grid(column=1, row=0, sticky="e", **App.options)

        self.lookback_label = ttk.Label(self, text="Lookback windows (days): ")
        self.lookback_label.grid(column=0, row=1, sticky="e", **App.options)
        self.lookback = tk.StringVar()
        self.lookback_entry = ttk.Entry(self, textvariable=self.lookback)
        self.lookback_entry.grid(column=1, row=1, sticky="e", **App.options)

        self.port_type = tk.StringVar()
        self.weight_button = ttk.Radiobutton(self, text="Equally Weighted", value="equal_weight",
                                             variable=self.port_type, command=self._conditional_input)
        self.weight_button.grid(column=0, row=2, **App.options)
        self.weight_button = ttk.Radiobutton(self, text="Custom Weights", value="custom_weight",
                                             variable=self.port_type, command=self._conditional_input)
        self.weight_button.grid(column=1, row=2, **App.options)

        self.alpha_label = ttk.Label(self, text="Confidence level (alpha): ")
        self.alpha_label.grid(row=4, column=0, sticky="e", **App.options)
        self.alpha = tk.StringVar()
        self.alpha_entry = ttk.Entry(self, textvariable=self.alpha)
        self.alpha_entry.grid(column=1, row=4, **App.options)

        self.button = ttk.Button(self, text="Get Risk Measures")
        self.button.grid(columnspan=2, row=5, sticky="ew", **App.options)
        self.button["command"] = self._get_risk_measure

        self.grid(padx=10, pady=10)

    def _conditional_input(self):
        if self.port_type.get() == "custom_weight":
            self.weight_label = ttk.Label(self, text="Specify portfolio weights:")
            self.weight_label.grid(row=3, sticky="e", **App.options)
            self.weight = tk.StringVar()
            self.weight_entry = ttk.Entry(self, textvariable=self.weight)
            self.weight_entry.grid(row=3, column=1, **App.options)
        elif self.port_type.get() == "equal_weight" and hasattr(self, "weight_label"):
            self.weight_label.destroy()
            self.weight_entry.destroy()
            delattr(self, "weight_label")
            delattr(self, "weight_entry")

    def _get_portfolio(self):
        try:
            tickers = [tic.strip().upper() for tic in self.tickers.get().split(",")]
            weights = [float(w.strip()) for w in self.weight.get().split(",")] if hasattr(self,
                                                                                          "weight_label") else None
            window = int(self.lookback.get())
            portfolio = Portfolio(tickers=tickers, lookback_window=window, portfolio_weights=weights)
            return portfolio
        except ValueError as err:
            showerror(title="Error", message=err)

    def _get_risk_measure(self):
        try:
            portfolio = self._get_portfolio()
            alpha = float(self.alpha.get())
            risk_measure = RiskMeasures(portfolio=portfolio, confidence_level=alpha)

            self.var_value = tk.Label(self, text=f"{risk_measure.var():.4%}")
            self.var_value.grid(column=1, row=6, sticky="w", **App.options)
            self.var = ttk.Label(self, text="Value a Risk: ")
            self.var.grid(column=0, row=6, sticky="e", **App.options)

            self.es = ttk.Label(self, text="Expected Shortfall: ")
            self.es.grid(column=0, row=7, sticky="e", **App.options)
            self.es_value = tk.Label(self, text=f"{risk_measure.es():.4%}")
            self.es_value.grid(column=1, row=7, sticky="w", **App.options)

            figure = Figure(figsize=(3, 3), dpi=100)
            figure_canvas = FigureCanvasTkAgg(figure, self)

            axes = figure.add_subplot()
            axes.set_title("Portfolio Returns Distribution", size=9, weight="bold")
            axes.tick_params(labelsize=8)
            axes.set_yticks([])
            axes.set_yticklabels("")
            axes.hist(portfolio.ret, density=True, bins=round(int(self.lookback.get()) ** 0.5),
                      edgecolor="k")
            axes.autoscale(tight=True)
            axes.vlines(risk_measure.var(), *axes.get_ylim(), colors="red", label="Var")
            axes.vlines(risk_measure.es(), *axes.get_ylim(), colors="green", label="ES")
            axes.legend(loc=1, fontsize=8)

            figure_canvas.get_tk_widget().grid(columnspan=2, row=8)

        except ValueError as err:
            showerror(title="Error", message=err)


class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Historical Var Calculator")
        self.iconbitmap(default=resource_path("statistics.ico"))
        self.info = ttk.Label(self, text="Historical Var and Es calculator", font=("Helvetica", 12, "bold")).grid()
        self.info = ttk.Label(self, text="A simple historical risk measures framework").grid()

        self.info = ttk.Label(self, text="by", font=("Helvetica", 6)).grid()
        self.info = ttk.Label(self, text="Gianluca Broll", font=("Helvetica", 6)).grid()

        self.geometry("350x635")
        self.resizable(False, False)


app = Root()
App(app)
app.mainloop()
