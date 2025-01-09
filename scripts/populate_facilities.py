"""
Rough script to load MEI facilities data into the API web server.

Data is read from a CSV set at MEI_FACILITIES_CSV_URI. The server URL should be set at SERVER_URL.

If the format of the CSV or API server internals change, this script will also likely need to change. The web API, this script, and the CSV are tightly coupled here.
"""


import datetime
import json

import pandas as pd  # v2.2.3
import requests


MEI_FACILITIES_CSV_URI = "data/mei_facilities.csv"
SERVER_URL = "http://localhost:8080"


def main():
    df_raw = pd.read_csv(MEI_FACILITIES_CSV_URI, skiprows=6)

    # We'll need to rename all the columns we want.
    rename_map = {
        "unique_id": "uid",
        "Segment": "segment",
        "Company": "company",
        "Technology": "technology",
        "Subcategory": "subcategory",
        "Investment_Status": "investment_status",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Investment_Estimated": "estimated_investment",
        "Announcement_Date": "announcement_date",
    }
    # Get only the columns we need.
    df = df_raw[list(rename_map.keys())].rename(columns=rename_map)
    # Pandas has trouble parsing date format unless we do it this way.
    df["announcement_date"] = pd.to_datetime(df["announcement_date"]).dt.date
    # Make money an int so we don't have float errors. Using Int64 so has NaNs.
    df["estimated_investment"] = df["estimated_investment"].round().astype("Int64")

    # Get pandas to encode it as a json str but then loading it as a json obj so we can pass it to requests when we had it to the server below.
    json_payload = json.loads(df.to_json(orient="records", date_format="iso"))

    for idx, facility in enumerate(json_payload):
        print(f"Processing {idx}: {facility}")

        # Parse the ISO format datetime and "NaT"s down into
        # ISO format dates. Skip facilities with "NaT"s.
        original_datetime = facility["announcement_date"]
        if original_datetime is None:
            print("Found bad date field - skipping facility")
            continue
        try:
            tmp_datetime = datetime.datetime.fromisoformat(original_datetime)
        except ValueError:
            print("Found bad date field - skipping facility")
            continue
        date_str = str(tmp_datetime.date())
        facility["announcement_date"] = date_str

        r = requests.post(
            f"{SERVER_URL}/facilities/",
            json=facility,
            headers={
                "Content-Type": "application/json",
                "user-agent": "populate_facilities.py/0.0.1",  # It's rude to to exclude a user-agent.
            },
        )
        r.raise_for_status()


if __name__ == "__main__":
    main()
