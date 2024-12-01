import os
import logging
import shutil
from flask import Flask, request, jsonify, send_file, render_template
from flask_socketio import SocketIO
from main import process_file  # Импорт функции обработки из main.py

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

# Создание папок для загрузки и сохранения результатов
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    """Отображает главную страницу."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """Обрабатывает загрузку файла и запускает его обработку."""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Файл не найден в запросе."})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Файл не выбран."})

    # Сохраняем загруженный файл
    input_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_file_path)
    logger.info(f"Файл загружен: {input_file_path}")

    # Обрабатываем файл через main.py
    try:
        result_file_path = os.path.join(RESULT_FOLDER, "result.csv")
        process_file(input_file_path, "test", emit_progress=lambda msg: logger.info(f"Прогресс: {msg}"))

        logger.info(f"Результирующий файл должен находиться по пути: {result_file_path}")
        
        return jsonify({"status": "success", "filename": os.path.basename(result_file_path)})
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/download/<filename>")
def download_file(filename):
    """Отправляет обработанный файл пользователю."""
    result_path = os.path.join(RESULT_FOLDER, filename)
    if os.path.exists(result_path):
        return send_file(result_path, as_attachment=True)
    return jsonify({"status": "error", "message": "Файл не найден."})


if __name__ == "__main__":
    logger.info("Запуск приложения Flask...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
