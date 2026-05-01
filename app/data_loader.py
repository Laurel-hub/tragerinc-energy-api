from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_customer_info():
    return pd.read_csv(DATA_DIR / "tragerinc_customer_info.csv")


def load_energy_usage():
    df = pd.read_csv(DATA_DIR / "tragerinc_energy_usage.csv")

    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if "Energy_Type" in df.columns:
        df[["Renewable_%", "Non_Renewable_%"]] = df["Energy_Type"].str.extract(
            r"(\d+)%\s*renewable,\s*(\d+)%\s*non-renewable"
        )

        df["Renewable_%"] = pd.to_numeric(df["Renewable_%"], errors="coerce")
        df["Non_Renewable_%"] = pd.to_numeric(df["Non_Renewable_%"], errors="coerce")

    df = df.sort_values(by=["Customer_ID", "Date"])

    return df


def load_support_tickets():
    df = pd.read_csv(DATA_DIR / "tragerinc_support_tickets.csv")

    df.columns = df.columns.str.strip()
    df["Date_Opened"] = pd.to_datetime(df["Date_Opened"], errors="coerce")
    df["Date_Closed"] = pd.to_datetime(df["Date_Closed"], errors="coerce")

    return df


def load_chatbot_interactions():
    return pd.read_csv(DATA_DIR / "tragerinc_chatbot_interactions.csv")