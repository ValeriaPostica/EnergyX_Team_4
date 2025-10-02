from datetime import datetime
import pandas as pd
import copy
import os

# Use relative paths for local development  
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CLOCK_COLMN_NAME = "Clock (8:0-0:1.0.0*255:2)"
METER_MAP_FILE = os.path.join(DATA_DIR, "daniel_data", "meter_to_location.json")
LOCATION_CSV_FILE = os.path.join(DATA_DIR, "daniel_data", "locations.csv")
DATA_JSON_FILE = os.path.join(DATA_DIR, "data.json")

def get_time_obj_from_dict(d):
    return datetime.strptime(d[CLOCK_COLMN_NAME], "%d.%m.%Y %H:%M:%S")


def get_diff(d1: dict, d2: dict):
    dt = get_time_obj_from_dict(d2) - get_time_obj_from_dict(d1)
    dexp = (
        d2["Active Energy Export (3:1-0:2.8.0*255:2)"]
        - d1["Active Energy Export (3:1-0:2.8.0*255:2)"]
    )
    dimp = (
        d2["Active Energy Import (3:1-0:1.8.0*255:2)"]
        - d1["Active Energy Import (3:1-0:1.8.0*255:2)"]
    )
    return {
        "Import Delta": dimp,
        "Export Delta": dexp,
        "Time Delta": str(dt),
        "Date of Second Val": str(get_time_obj_from_dict(d2)),
    }


def get_diffs(d: list[dict]) -> list[dict]:
    return list(map(get_diff, d, d[1:]))


def get_every_diff(data: dict, ids: list[str]):
    df = (
        pd.concat({k: pd.DataFrame(v) for k, v, in data.items()}, names=["Meter"])
        .reset_index(level=0)
        .reset_index(drop=True)
    )

    df = df[df["Meter"].isin(ids)]
    xs = (
        df.groupby("Meter")
        .apply(lambda x: x.drop(columns="Meter").to_dict(orient="records"))
        .to_dict()
    )
    arrs = [v for _, v in xs.items()]
    return [get_diffs(arr) for arr in arrs]


def get_timed_diffs(data: dict, ids: list[str], time: str) -> list[dict]:
    # Getting the ids back in column
    df = (
        pd.concat({k: pd.DataFrame(v) for k, v, in data.items()}, names=["Meter"])
        .reset_index(level=0)
        .reset_index(drop=True)
    )

    df = df[df["Meter"].isin(ids) & (df[CLOCK_COLMN_NAME] == time)]
    df = df[
        [
            "Meter",
            "Active Energy Export (3:1-0:2.8.0*255:2)",
            "Active Energy Import (3:1-0:1.8.0*255:2)",
            CLOCK_COLMN_NAME,
        ]
    ].to_dict(orient="records")

    return {
        row["Meter"]: {
            "Export": row["Active Energy Export (3:1-0:2.8.0*255:2)"],
            "Import": row["Active Energy Import (3:1-0:1.8.0*255:2)"],
            "Clock": row[CLOCK_COLMN_NAME],
        }
        for row in df
    }


def calc_diff_from_two_timed_arrays(d2: dict, d1: dict):
    common_keys = d2.keys() & d1.keys()
    return {
        m_id: {
            "Export Delta": d2[m_id]["Export"] - d1[m_id]["Export"],
            "Import Delta": d2[m_id]["Import"] - d1[m_id]["Import"],
        }
        for m_id in common_keys
    }


def calc_diff_timed(data: dict, ids: list[str], t2: str, t1: str) -> dict:
    d2 = get_timed_diffs(data, ids, t2)
    d1 = get_timed_diffs(data, ids, t1)
    return calc_diff_from_two_timed_arrays(d2, d1)


import json
from diff_data import calc_diff_timed
import os
import pandas as pd



def get_all_region_meters() -> dict:
    if os.path.exists(METER_MAP_FILE):
        with open(METER_MAP_FILE, "r", encoding="utf-8") as f:
            location_to_meters = json.load(f)
        # Convert meter IDs back to int
        location_to_meters = {
            loc: [str(m) for m in meters] for loc, meters in location_to_meters.items()
        }

    return location_to_meters


def get_color_json(data: dict, cloc: str) -> dict:

    t = cloc.split(" ")
    hour = t[1]
    day = t[0]

    # Try to load meter-to-location mapping from file

    # Try to load location-to-meters mapping from file
    if os.path.exists(METER_MAP_FILE):
        with open(METER_MAP_FILE, "r", encoding="utf-8") as f:
            location_to_meters = json.load(f)
        # Convert meter IDs back to int
        location_to_meters = {
            loc: [int(m) for m in meters] for loc, meters in location_to_meters.items()
        }

    all_meter_ids = [
        str(meter) for meters in location_to_meters.values() for meter in meters
    ]

    # Example usage: input day and hour, then call calc_diff_timed for each location

    from datetime import datetime, timedelta

    dt = datetime.strptime(f"{day} {hour}", "%d.%m.%Y %H:%M:%S")
    prev_dt = dt - timedelta(hours=1)
    t2 = dt.strftime("%d.%m.%Y %H:%M:%S")
    t1 = prev_dt.strftime("%d.%m.%Y %H:%M:%S")

    # Call calc_diff_timed once for all meters
    diff = calc_diff_timed(data, all_meter_ids, t2, t1)

    # For one location, print all Import Delta values before summing

    # For one location, print all Import Delta values before summing, warn if missing

    # Print dictionary of location: total_consumption for all locations
    # print(location_to_meters)
    location_consumption = {}
    for location, meters in location_to_meters.items():
        total_consumption = sum(
            diff.get(str(m), {}).get("Import Delta", 0) for m in meters
        )
        location_consumption[location] = total_consumption

    # Function to assign RGB color based on consumption
    def get_color_for_consumption(consumption, min_val, max_val):
        if max_val == min_val:
            # Avoid division by zero, assign green
            return (0, 255, 0)
        percent = (consumption - min_val) / (max_val - min_val) * 100
        if percent <= 25:
            # Green to Yellow
            # 0%: green (0,255,0), 25%: yellow (255,255,0)
            r = int(255 * (percent / 25))
            g = 255
            b = 0
        elif percent <= 75:
            # Yellow to Red
            # 25%: yellow (255,255,0), 75%: red (255,0,0)
            r = 255
            g = int(255 * (1 - (percent - 25) / 50))
            b = 0
        else:
            # 75%-100%: red (255,0,0)
            r = 255
            g = 0
            b = 0
        return (r, g, b)

    # Calculate min, max, avg
    values = list(location_consumption.values())
    # print(values)
    min_val = min(values)
    max_val = max(values)
    avg_val = sum(values) / len(values) if values else 0

    # Load coordinates from locations.csv
    coords_df = pd.read_csv(LOCATION_CSV_FILE)
    coords_map = {
        row["Name"]: (row["Latitude"], row["Longitude"])
        for _, row in coords_df.iterrows()
    }

    # Build new dictionary with color and coordinates
    location_consumption_with_color = {}
    for location, consumption in location_consumption.items():
        color = get_color_for_consumption(consumption, min_val, max_val)
        coord = coords_map.get(location)
        location_consumption_with_color[location] = {
            "consumption": consumption,
            "color": color,
            "coordonates": coord,
        }
    return location_consumption_with_color

def get_region_consumption(data:dict, region:str) -> dict:
    loc_data = get_all_region_meters()
    diffss = get_every_diff(data, loc_data[region])

    result = {
        x["Date of Second Val"]: {
            "Import": x["Import Delta"],
            "Export": x["Export Delta"],
        }
        for x in diffss[0]
    }

    for arr in diffss[1:]:
        for key, _ in result.items():
            for x in arr:
                if x["Date of Second Val"] == key:
                    result[key]["Import"] += x["Import Delta"]
                    result[key]["Export"] += x["Export Delta"]
    return result

def calc_consump(data:dict) -> list[dict]:

    coords_df = pd.read_csv(LOCATION_CSV_FILE)
    coords_maps: list[str] = [row["Name"] for _, row in coords_df.iterrows()]

    every = {}
    all = {}

    for region in coords_maps:
        every[region] = get_region_consumption(data, region)
    
    every_keys = list(every.keys())

    all["moldova"] = copy.deepcopy(every[every_keys[0]])

    for reg in every_keys[1:]:
        for time, vals in every[reg].items():
            if time in all["moldova"]:
                try:
                    all["moldova"][time]["Import"] += vals.get("Import", 0)
                    all["moldova"][time]["Export"] += vals.get("Export", 0)
                except Exception:
                    continue
    return [every, all]


if __name__ == "__main__":

    import json

    data = {}
    # Opening JSON file
    with open(DATA_JSON_FILE) as json_file:
        data: dict = json.load(json_file)

    
    