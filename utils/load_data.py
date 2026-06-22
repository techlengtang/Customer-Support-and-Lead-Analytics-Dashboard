import pandas as pd

from utils.paths import get_project_root


def load_data():

    df = pd.read_csv(
        get_project_root() / "data" / "Client_Objection_Cleaned.csv"
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