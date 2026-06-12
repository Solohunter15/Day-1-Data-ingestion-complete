import os
import json

def extract_notebook(nb_path, out_path):
    if not os.path.exists(nb_path):
        print(f"Notebook {nb_path} does not exist.")
        return
    
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
        
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"# EXTRACTED FROM {os.path.basename(nb_path)}\n")
        out.write(f"# =========================================================\n\n")
        
        for i, cell in enumerate(nb.get("cells", [])):
            cell_type = cell.get("cell_type")
            source = "".join(cell.get("source", []))
            
            out.write(f"# --- CELL {i} ({cell_type.upper()}) ---\n")
            if cell_type == "markdown":
                # Comment out markdown to make it clean python/text comments
                commented = "\n".join([f"# {line}" for line in source.split("\n")])
                out.write(commented + "\n\n")
            else:
                out.write(source + "\n\n")

os.makedirs("scratch", exist_ok=True)
extract_notebook("day 3/EDA_Analysis.ipynb", "scratch/eda_extracted.py")
extract_notebook("day 4/Performance_Analytics.ipynb", "scratch/performance_extracted.py")
extract_notebook("day 6/Advanced_Analytics.ipynb", "scratch/advanced_extracted.py")
print("Notebooks extracted successfully!")
