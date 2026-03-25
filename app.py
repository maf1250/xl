from flask import Flask, request, send_file, render_template
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file:
        return "لم يتم رفع ملف", 400

    filename = file.filename
    base_name = os.path.splitext(filename)[0]

    # Save file
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # Read Excel
    try:
        df = pd.read_excel(input_path, engine='openpyxl')
    except Exception as e:
        return f"خطأ في قراءة الملف: {e}", 400

    # Clean columns
    df.columns = df.columns.str.strip()

    # =========================
    # Column Mapping
    # =========================
    manual = request.form.get("manual", "no")

    if manual == "yes":
        name_col = request.form.get("name_col", "")
        mobile_col = request.form.get("mobile_col", "")
        city_col = request.form.get("city_col", "")

        column_mapping = {}
        if name_col:
            column_mapping[name_col] = "Name"
        if mobile_col:
            column_mapping[mobile_col] = "Mobile"
        if city_col:
            column_mapping[city_col] = "City"
    else:
        column_mapping = {
            "اسم الحاج": "Name",
            "رقم الجوال": "Mobile",
            "المدينة": "City"
        }

    df = df.rename(columns=column_mapping)

    # =========================
    # Gender Filter
    # =========================
    gender_filter = request.form.get("gender_filter", "no")

    if gender_filter == "yes":
        gender = request.form.get("gender", "").lower()

        if "الجنس" in df.columns:
            if gender in ["male", "m"]:
                df = df[df["الجنس"] == "ذكر"]
            elif gender in ["female", "f"]:
                df = df[df["الجنس"] == "أنثى"]

    # =========================
    # Format Mobile
    # =========================
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

    # Remove invalid
    df = df[df["Mobile"].notna()]
    df = df.drop_duplicates(subset=["Mobile"])

    # =========================
    # Split Names
    # =========================
    def split_name(name):
        if pd.isna(name):
            return "", ""

        parts = str(name).strip().split()

        if len(parts) == 0:
            return "", ""
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], " ".join(parts[1:])

    df[["FirstName", "LastName"]] = df["Name"].apply(
        lambda x: pd.Series(split_name(x))
    )

    df["FullName"] = (df["FirstName"] + " " + df["LastName"]).str.strip()

    # Sort
    df = df.sort_values(by="FullName", ascending=True)

    # =========================
    # Create VCF
    # =========================
    output_path = os.path.join(UPLOAD_FOLDER, base_name + ".vcf")

    with open(output_path, "w", encoding="utf-8") as vcf:
        for _, row in df.iterrows():
            First_Name = row["FirstName"]
            Last_Name = row["LastName"]
            Full_Name = row["FullName"]
            Mobile = row["Mobile"]
            Company = str(row.get("City", "")).strip()

            vcf.write("BEGIN:VCARD\n")
            vcf.write("VERSION:3.0\n")
            vcf.write(f"N:{Last_Name};{First_Name};;;\n")
            vcf.write(f"FN:{Full_Name}\n")
            vcf.write(f"ORG:{Company}\n")
            vcf.write(f"TEL;TYPE=CELL:{Mobile}\n")
            vcf.write("END:VCARD\n")

    # =========================
    # RETURN FILE (Safari Preview Mode)
    # =========================
    return send_file(
        output_path,
        as_attachment=False,   # 🔥 This enables preview instead of forced download
        mimetype="text/x-vcard"
    )


if __name__ == "__main__":
    app.run(debug=True)
