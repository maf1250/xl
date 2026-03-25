import pandas as pd
import os

def process_file(file_path, use_manual_mapping, mapping_inputs, use_gender, gender_choice):
    filename, ext = os.path.splitext(file_path)

    df = pd.read_excel(file_path, engine='openpyxl')

    # Clean column names
    df.columns = df.columns.str.strip()

    # Fixed mapping
    fixed_mapping = {
        "اسم الحاج": "Name",
        "رقم الجوال": "Mobile",
        "المدينة": "City"
    }

    if use_manual_mapping:
        column_mapping = mapping_inputs
    else:
        column_mapping = fixed_mapping

    df = df.rename(columns=column_mapping)

    # Gender filter
    if use_gender:
        if gender_choice.lower() in ['male', 'm']:
            sorted_gender = "ذكر"
        else:
            sorted_gender = "أنثى"

        df = df[df['الجنس'] == sorted_gender]

    # Format mobile numbers
    def format_mobile(mobile):
        if pd.isna(mobile):
            return None

        mobile = str(mobile).replace(" ", "").replace("-", "")

        if mobile.startswith("+966"):
            return mobile
        elif mobile.startswith("966"):
            return "+" + mobile
        elif mobile.startswith("05"):
            return "+966" + mobile[1:]
        else:
            return "+966" + mobile

    df["Mobile"] = df["Mobile"].apply(format_mobile)

    df = df[df["Mobile"].notna()]
    df = df.drop_duplicates(subset=["Mobile"])

    # Split name
    def split_name(name):
        if pd.isna(name):
            return "", ""

        parts = str(name).strip().split()

        if len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], " ".join(parts[1:])

    df[["FirstName", "LastName"]] = df["Name"].apply(
        lambda x: pd.Series(split_name(x))
    )

    df["FullName"] = (df["FirstName"] + " " + df["LastName"]).str.strip()

    df = df.sort_values(by="FullName", ascending=True)

    # Create VCF
    vcf_file = filename + ".vcf"

    with open(vcf_file, "w", encoding="utf-8") as vcf:
        for _, row in df.iterrows():
            vcf.write("BEGIN:VCARD\n")
            vcf.write("VERSION:3.0\n")
            vcf.write(f"N:{row['LastName']};{row['FirstName']};;;\n")
            vcf.write(f"FN:{row['FullName']}\n")
            vcf.write(f"ORG:{str(row.get('City','')).strip()}\n")
            vcf.write(f"TEL;TYPE=CELL:{row['Mobile']}\n")
            vcf.write("END:VCARD\n")

    return vcf_file
