import os

root_dir = r"C:\Users\Nikita\Desktop\merge\EnergyX_Team_4\frontend\src"
replacements = {
    "http://localhost:5000": "",
    "http://localhost:4000": ""
}

for subdir, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".jsx") or file.endswith(".js"):
            filepath = os.path.join(subdir, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                changed = False
                for target, replacement in replacements.items():
                    if target in new_content:
                        new_content = new_content.replace(target, replacement)
                        changed = True
                
                if changed:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
