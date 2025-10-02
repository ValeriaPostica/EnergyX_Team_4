import pandas as pd
import filename

def read_one_file(file:str) -> dict:
    df = pd.read_csv(file)
    print(df.columns)
    return df.groupby("Meter").apply(lambda x: x.drop(columns="Meter").to_dict(orient="records")).to_dict()

    

def read_all_files() -> list[dict]:
    # return read_one_file(f"../data/{filename.get_all_file_names()[0]}")
    return [read_one_file(f"../data/{f}") for f in filename.get_all_file_names()]

def merge(to: dict, d2:dict):
    for key, value in d2.items():
        if key in to:
            to[key] += value  # concatenate lists
        else:
            to[key] = value

def merge_all(dicts: list[dict]) -> dict:
    merged = {}
    for d in dicts:
        merge(merged, d)
    return merged

def main():
    ds = read_all_files()
    return merge_all(ds)

if __name__ == "__main__" :
    main()