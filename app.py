from flask import Flask, request, send_file, render_template
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

def convert_excel_to_vcf(file_path, manual_mapping=None, gender_filter=None):
    df = pd.read_excel(file_path, engine='openpyxl')
    df.columns = df.columns.str.strip()

    # Default mapping if none provided
    default_mapping = {"اسم الحاج":"Name", "رقم الجوال":"Mobile", "المدينة":"City"}
    mapping = manual_mapping or default_mapping
    df = df.rename(columns=mapping)

    # Filter by gender if requested
    if gender_filter in ["male", "female"] and "الجنس" in df.columns:
        sorted_gender = "ذكر" if gender_filter=="male" else "أنثى"
        df = df[df["الجنس"] == sorted_gender]

    df["Mobile"] = df["Mobile"].apply(format_mobile)
    df = df[df["Mobile"].notna()]
    df = df.drop_duplicates(subset=["Mobile"])

    df[["FirstName", "LastName"]] = df["Name"].apply(lambda x: pd.Series(split_name(x)))
    df["FullName"] = (df["FirstName"] + " " + df["LastName"]).str.strip()
    df = df.sort_values(by="FullName", ascending=True)

    vcf_file = os.path.splitext(file_path)[0] + ".vcf"
    with open(vcf_file, "w", encoding="utf-8") as vcf:
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
    return vcf_file

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return "لم يتم رفع الملف", 400

    upload_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    uploaded_file.save(upload_path)

    # Optional: handle manual mapping & gender
    gender_filter = request.form.get("gender") if request.form.get("gender_filter")=="yes" else None
    vcf_path = convert_excel_to_vcf(upload_path, gender_filter=gender_filter)

    # Send the file for Safari's "view/download" popup
    return send_file(
        vcf_path,
        as_attachment=False,  # important for iPhone native popup
        mimetype="text/x-vcard"
    )

if __name__ == "__main__":
    app.run(debug=True)
