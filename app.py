from flask import Flask, render_template, request, jsonify
import os
import time  # Для имитации прогресса
from main import process_file  # Импортируем функцию обработки

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Файл не выбран"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Пустое имя файла"})

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Имитируем прогресс обработки
        for i in range(5):
            print(f"Обработка: {i * 20}%")
            time.sleep(1)

        # Вызываем обработку файла
        result = process_file(file_path)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
