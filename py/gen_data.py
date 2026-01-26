import csv
import os

def gen_data():
    # define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uni2tipa_dir = os.path.join(base_dir, "uni2tipa")
    
    data = {}
    
    # UNI2TIPA (0-2)
    uni2tipa = []
    for i in range(3):
        path = os.path.join(uni2tipa_dir, f"uni2tipa{i}.tsv")
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONE, delimiter="\t")
            uni2tipa.append({row[0]: row[1] for row in reader if len(row) >= 2})
    data['UNI2TIPA'] = uni2tipa
    
    # UNI2TIPA_TONE
    path_tone = os.path.join(uni2tipa_dir, "uni2tipa-tone.tsv")
    with open(path_tone, encoding="utf-8") as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONE, delimiter="\t")
        data['UNI2TIPA_TONE'] = {row[0]: row[1] for row in reader if len(row) >= 2}
    
    # UNI2TIPA_SUPSUB
    path_supsub = os.path.join(uni2tipa_dir, "uni2tipa-supsub.tsv")
    with open(path_supsub, encoding="utf-8") as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONE, delimiter="\t")
        data['UNI2TIPA_SUPSUB'] = {row[0]: row[1] for row in reader if len(row) >= 2}
    
    # write to py/ipa2tipa/data.py
    output_path = os.path.join(base_dir, "py", "ipa2tipa", "data.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Generated from uni2tipa/*.tsv. Do not edit manually.\n\n")
        f.write(f"UNI2TIPA = {repr(data['UNI2TIPA'])}\n\n")
        f.write(f"UNI2TIPA_TONE = {repr(data['UNI2TIPA_TONE'])}\n\n")
        f.write(f"UNI2TIPA_SUPSUB = {repr(data['UNI2TIPA_SUPSUB'])}\n")
    
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    gen_data()
