from flask import Flask, request, send_file
import pandas as pd
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename
    base_name = os.path.splitext(filename)[0]

    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    df = pd.read_excel(filepath, engine='openpyxl')

    # --- Your processing logic ---
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"اسم الحاج":"Name","رقم الجوال":"Mobile","المدينة":"City"})
    df["Mobile"] = df["Mobile"].apply(lambda x: "+966" + str(x).replace("05","") if str(x).startswith("05") else x)
    df[["FirstName","LastName"]] = df["Name"].apply(lambda n: pd.Series(str(n).split(' ',1) if ' ' in str(n) else [str(n),'']))
    df["FullName"] = (df["FirstName"] + " " + df["LastName"]).str.strip()
    df = df.drop_duplicates(subset=["Mobile"])

    output_path = os.path.join("uploads", base_name + ".vcf")
    with open(output_path,"w",encoding="utf-8") as vcf:
        for _, row in df.iterrows():
            vcf.write("BEGIN:VCARD\n")
            vcf.write("VERSION:3.0\n")
            vcf.write(f"N:{row['LastName']};{row['FirstName']};;;\n")
            vcf.write(f"FN:{row['FullName']}\n")
            vcf.write(f"ORG:{row.get('City','')}\n")
            vcf.write(f"TEL;TYPE=CELL:{row['Mobile']}\n")
            vcf.write("END:VCARD\n")

    return send_file(output_path, as_attachment=True, download_name=base_name+".vcf", mimetype="text/vcard")
