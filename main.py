import json
import pandas as pd
import logging
from scripts.preprocessing import preprocessing
from scripts.features import features
from scripts.salary import salaries
from scripts.model import modeltesting

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def process_file(file_path, flag, emit_progress):
    """
    Обрабатывает файл, переданный через Flask.

    :param file_path: Путь к загруженному файлу
    :param flag: Режим обработки ('train' или 'test')
    :param emit_progress: Функция для отправки прогресса на фронтенд
    :return: Путь к результату обработки
    """
    emit_progress("Начало обработки файла...")
    logger.info(f"Начало обработки файла: {file_path}")

    # Загрузка файла
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            emit_progress("Файл успешно загружен.")
            logger.info("Файл успешно загружен.")
    except Exception as e:
        emit_progress(f"Ошибка чтения файла: {e}")
        logger.error(f"Ошибка чтения файла: {e}")
        raise

    # Преобразование в DataFrame
    emit_progress("Превращение файла в DataFrame...")
    logger.info("Превращение файла в DataFrame.")
    df = pd.DataFrame(data)

    # Предобработка
    emit_progress("Выполняется предобработка...")
    logger.info("Начало предобработки.")
    try:
        df = preprocessing(df, flag)
        emit_progress("Предобработка завершена.")
        logger.info("Предобработка завершена.")
    except Exception as e:
        emit_progress(f"Ошибка предобработки: {e}")
        logger.error(f"Ошибка предобработки: {e}")
        raise

    # Постобработка
    emit_progress("Выполняется постобработка...")
    logger.info("Начало постобработки.")
    try:
        df2 = pd.read_csv('data/postpreprocess_df.csv')
        df = pd.merge(df, df2, left_on='client_name', right_on='short_name', how='left')
        df = df.drop(columns={'Unnamed: 0', 'short_name'})
        emit_progress("Постобработка завершена.")
        logger.info("Постобработка завершена.")
    except Exception as e:
        emit_progress(f"Ошибка постобработки: {e}")
        logger.error(f"Ошибка постобработки: {e}")
        raise

    # Обработка зарплат
    emit_progress("Выполняется обработка зарплат...")
    logger.info("Начало обработки зарплат.")
    try:
        df = salaries(df)
        emit_progress("Обработка зарплат завершена.")
        logger.info("Обработка зарплат завершена.")
    except Exception as e:
        emit_progress(f"Ошибка Обработка зарплати: {e}")
        logger.error(f"Ошибка Обработка зарплат: {e}")
        raise

    # Генерация фич
    emit_progress("Генерация фич...")
    logger.info("Начало генерации фич.")
    try:
        df = features(df, flag)
        emit_progress("Генерация фич завершена.")
        logger.info("Генерация фич завершена.")
    except Exception as e:
        emit_progress(f"Ошибка генерации фич: {e}")
        logger.error(f"Ошибка генерации фич: {e}")
        raise
    # Тестируем модель
    df_result = modeltesting(df)

    # Сохранение результата
    emit_progress("Сохранение результата...")
    logger.info("Сохранение результата.")
    output_path = "results/result.csv"
    try:
        df_result.to_csv(output_path, index=False)
        emit_progress("Результат успешно сохранён.")
        logger.info(f"Результат успешно сохранён в {output_path}.")
    except Exception as e:
        emit_progress(f"Ошибка сохранения результата: {e}")
        logger.error(f"Ошибка сохранения результата: {e}")
        raise

    emit_progress("Обработка завершена.")
    logger.info("Обработка файла завершена.")
    return output_path


if __name__ == "__main__":
    logger.info("Запуск скрипта main.py напрямую.")
    # Тестовый запуск
    try:
        process_file(file_path='data/client_dataset.json', flag='test', emit_progress=print)
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
