from flask import Flask, render_template, request, send_file
import os
from converter import process_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Get form inputs
    use_manual = request.form.get("manual") == "yes"
    use_gender = request.form.get("gender_filter") == "yes"
    gender = request.form.get("gender")

    mapping_inputs = {
        request.form.get("name_col"): "Name",
        request.form.get("mobile_col"): "Mobile",
        request.form.get("city_col"): "City"
    } if use_manual else {}

    output = process_file(filepath, use_manual, mapping_inputs, use_gender, gender)

    return send_file(output, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
