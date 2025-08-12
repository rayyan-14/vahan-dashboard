import pandas as pd

def calculate_growth(df):
    df = df.copy()
    df["Year"] = df["Month"].str[:4].astype(int)
    df["Quarter"] = df["Month"].str[-2:]

    df.sort_values(by=["Category", "Manufacturer", "Year", "Quarter"], inplace=True)

    df["Prev_Qtr"] = df.groupby(["Category", "Manufacturer"])["Registrations"].shift(1)
    df["QoQ_Growth"] = ((df["Registrations"] - df["Prev_Qtr"]) / df["Prev_Qtr"]) * 100

    df["Prev_Year"] = df.groupby(["Category", "Manufacturer"])["Registrations"].shift(4)
    df["YoY_Growth"] = ((df["Registrations"] - df["Prev_Year"]) / df["Prev_Year"]) * 100

    return df
