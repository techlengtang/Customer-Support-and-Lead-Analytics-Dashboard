import pandas as pd

from utils.paths import get_project_root


REQUIRED_COLUMNS = [
    "Objection Status",
    "First Contact Date",
    "Nationality",
    "Main Contact Platform",
    "Lead Quality",
    "Service",
    "Ad Source",
    "Objection Type",
    "Quote_English",
    "Nationality_Category",
]


def clean_dashboard_data(df):

    df = df.copy()

    df.columns = df.columns.str.strip()

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    df["First Contact Date"] = pd.to_datetime(
        df["First Contact Date"],
        errors="coerce"
    )

    df["Objection Type"] = df["Objection Type"].replace(
        "Employme - Out Of Scope",
        "Employment - Out Of Scope"
    )

    return df


def load_data():

    df = pd.read_csv(
        get_project_root() / "data" / "Client_Objection_Cleaned.csv"
    )

    return clean_dashboard_data(df)


def load_uploaded_data(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError("Please upload a CSV or Excel file.")

    return clean_dashboard_data(df)
