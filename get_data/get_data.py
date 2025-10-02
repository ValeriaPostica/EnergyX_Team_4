#import numpy
import api.diff_data as diff_data
import json

def stretch_array(arr, target_len):
    """Resize arr to target_len by repeating elements (simple interpolation)."""
    n = len(arr)
    if n == 0:
        return []  # skip empty arrays
    if n == target_len:
        return arr
    stretched = []
    for i in range(target_len):
        # map each new index to original index
        orig_idx = int(i * n / target_len)
        stretched.append(arr[orig_idx])
    return stretched

data = {}
# Opening JSON file
with open("data.json") as json_file:
    data: dict = json.load(json_file)

data_list = []
for key in data.keys():
    data_list.append(data[key])

# print(data_list[0][1]["Active Energy Import (3:1-0:1.8.0*255:2)"])

data = list(map(lambda d: list(map(lambda l: l["Import Delta"],diff_data.get_diffs(d))),data_list))
print(len(data))

data = [arr for arr in data if any(v != 0 for v in arr)]

# 2. Find the maximum length
max_len = max(len(arr) for arr in data)
print(max_len)

# 3. Stretch all arrays to max_len
data = [stretch_array(arr, max_len) for arr in data]
print(len(data))

with open("processed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)