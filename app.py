from flask import Flask, render_template, request
import fitz
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "Please select a PDF file."

    file = request.files["file"]

    if file.filename == "":
        return "No file selected."

    if not allowed_file(file.filename):
        return "Please upload a PDF file only."

    filename = secure_filename(file.filename)

    if not filename:
        return "Invalid filename."

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        with fitz.open(filepath) as pdf:
            text = "\n".join(page.get_text() for page in pdf)

        if not text.strip():
            return "No readable text found. The PDF may contain scanned images."

        return render_template(
            "result.html",
            filename=filename,
            extracted_text=text
        )

    except Exception:
        return "Unable to read this PDF. Please try another file."


if __name__ == "__main__":
    app.run(debug=True)