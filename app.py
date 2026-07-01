from pathlib import Path
from uuid import uuid4

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from utils import extract_text
from analyzer import analyze_resume

app = Flask(__name__)
app.secret_key = "resume-reviewer-local-secret"
app.config["UPLOAD_FOLDER"] = Path("uploads")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def is_allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    upload_folder = app.config["UPLOAD_FOLDER"]
    upload_folder.mkdir(exist_ok=True)

    original_name = secure_filename(file.filename)
    suffix = Path(original_name).suffix.lower()
    saved_name = f"{Path(original_name).stem}-{uuid4().hex[:8]}{suffix}"
    saved_path = upload_folder / saved_name
    file.save(saved_path)
    return saved_path, original_name

@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        file = request.files.get("resume")

        if not file or file.filename == "":
            error = "Please choose a resume file before analyzing."
        elif not is_allowed_file(file.filename):
            error = "Unsupported file type. Please upload a PDF, DOCX, or TXT resume."
        else:
            try:
                saved_path, uploaded_file = save_upload(file)
                text = extract_text(saved_path)
                if not text.strip():
                    error = "No readable text was found in this file. Please upload a text-based PDF, DOCX, or TXT resume."
                else:
                    session["result"] = analyze_resume(text)
                    session["uploaded_file"] = uploaded_file
                    return redirect(url_for("result"))
            except Exception as exc:
                error = str(exc)

    return render_template("index.html", error=error)


@app.route("/result")
def result():
    result_data = session.get("result")
    if not result_data:
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        result=result_data,
        uploaded_file=session.get("uploaded_file"),
    )


if __name__ == "__main__":
    app.run(debug=True)
