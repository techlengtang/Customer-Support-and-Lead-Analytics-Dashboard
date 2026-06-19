import pandas as pd

def load_data():

    df = pd.read_csv(
        "data/Client_Objection_Cleaned.csv"
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