FILES = [
    {
        "day": 2,
        "hour": 0,
    },
    {
        "day": 2,
        "hour": 6,
    },
    {
        "day": 2,
        "hour": 12,
    },
    {
        "day": 2,
        "hour": 18,
    },
    {
        "day": 3,
        "hour": 0,
    },
    {
        "day": 3,
        "hour": 12,
    },
    {
        "day": 4,
        "hour": 0,
    },
    {
        "day": 4,
        "hour": 12,
    },
    {
        "day": 4,
        "hour": 18,
    },
    {
        "day": 5,
        "hour": 0,
    },
    {
        "day": 5,
        "hour": 6,
    },
    {
        "day": 5,
        "hour": 12,
    },
    {
        "day": 5,
        "hour": 18,
    },
    {
        "day": 6,
        "hour": 0,
    },
    {
        "day": 6,
        "hour": 6,
    },
    {
        "day": 6,
        "hour": 12,
    },
    {
        "day": 6,
        "hour": 18,
    },
    {
        "day": 7,
        "hour": 0,
    },
    {
        "day": 7,
        "hour": 6,
    },
    {
        "day": 7,
        "hour": 12,
    },
    {
        "day": 7,
        "hour": 18,
    },
    {
        "day": 8,
        "hour": 0,
    },
    {
        "day": 8,
        "hour": 6,
    },
    {
        "day": 8,
        "hour": 12,
    },
    {
        "day": 8,
        "hour": 18,
    }
]

class file_name_class:
    day: int
    hour:int
    minute:int

    def __init__(self, day:int, hour:int):
        self.day = day
        self.hour = hour

    @staticmethod
    def from_dict(d: dict):
        return file_name_class(d["day"], d["hour"])

def get_file_name(fc: file_name_class):
    return f"{fc.day:02d}.06.2025 {fc.hour:02d}_00_All measuring points_ExportFile.csv"

def get_all_file_names():
    return [get_file_name(file_name_class.from_dict(f)) for f in FILES]
    