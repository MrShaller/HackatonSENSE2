import re
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Определяем базовый путь
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Путь к текущему файлу
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')  # Путь к папке data

# Пути к файлам векторизаторов
VECT1_PATH = os.path.join(DATA_DIR, 'vect1.pkl')
VECT2_PATH = os.path.join(DATA_DIR, 'vect2.pkl')

# Функция для нормализации текста
def normalize_text_to_set(text):
    if not isinstance(text, str):
        return set()  # Если текст отсутствует, возвращаем пустое множество
    # Приведение к нижнему регистру, удаление лишних символов и разделение на слова
    text = re.sub(r'[^а-яёa-z0-9\s]', '', text.lower())
    return set(text.split())

# Функция для расчёта сходства на основе пересечения множеств
def calculate_euler_similarity(df):
    if 'key_skills' not in df.columns or 'last_position' not in df.columns:
        print("Отсутствуют столбцы 'key_skills' или 'last_position'.")
        return df

    # Преобразуем текст в множества слов
    df['key_skills_set'] = df['key_skills'].apply(normalize_text_to_set)
    df['last_position_set'] = df['last_position'].apply(normalize_text_to_set)

    # Вычисляем долю пересечения (intersection/last_position)
    def compute_similarity(row):
        if not row['last_position_set']:
            return 0  # Если last_position пусто, возвращаем 0
        intersection = row['key_skills_set'] & row['last_position_set']
        return len(intersection) / len(row['last_position_set'])

    df['key_skills-last_pos_euler_similarity'] = df.apply(compute_similarity, axis=1)

    return df


def calculate_years_delta(row):
    try:
        # Приводим к числовому типу для расчёта
        age = float(row['age'])
        full_years = float(row['full_years'])
        return age - full_years
    except (ValueError, TypeError):
        return None  # Если значения не подходят, возвращаем None


# Функция для лемматизации текста
def lemmatize_text(text):

    # Инициализация стеммера для лемматизации
    stemmer = SnowballStemmer("russian")

    if not isinstance(text, str):
        return ""
    # Удаляем лишние символы и приводим текст к нижнему регистру
    text = re.sub(r'[^а-яёa-z\s]', '', text.lower())
    # Применяем лемматизацию
    return ' '.join([stemmer.stem(word) for word in text.split()])


# Вычисление TF-IDF и косинусного сходства
def calculate_tfidf_similarity(row, flag, **kwargs):
    texts = [row['position_lemmatized'], row['last_position_lemmatized']]
    
    if flag == 'train':
        vectorizer1 = TfidfVectorizer()
        tfidf_matrix = vectorizer1.fit_transform(texts)
        # Сохраняем векторизатор
        with open(VECT1_PATH, 'wb') as f:
            pickle.dump(vectorizer1, f)
    elif flag == 'test':
        # Загружаем векторизатор
        if os.path.exists(VECT1_PATH):
            with open(VECT1_PATH, 'rb') as f:
                vectorizer1 = pickle.load(f)
            tfidf_matrix = vectorizer1.transform(texts)
        else:
            raise FileNotFoundError(f"Векторизатор {VECT1_PATH} не найден.")
    else:
        raise ValueError("Неверное значение флага. Используйте 'train' или 'test'.")
    
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0, 0]

# Функция для вычисления косинусного сходства между навыками и последней позицией
# Вычисление TF-IDF и косинусного сходства для навыков
def calculate_skills_last_pos_similarity(row, flag, **kwargs):
    texts = [row['key_skills_lemmatized'], row['last_position_lemmatized']]
    
    if flag == 'train':
        vectorizer2 = TfidfVectorizer()
        tfidf_matrix = vectorizer2.fit_transform(texts)
        # Сохраняем векторизатор
        with open(VECT2_PATH, 'wb') as f:
            pickle.dump(vectorizer2, f)
    elif flag == 'test':
        # Загружаем векторизатор
        if os.path.exists(VECT2_PATH):
            with open(VECT2_PATH, 'rb') as f:
                vectorizer2 = pickle.load(f)
            tfidf_matrix = vectorizer2.transform(texts)
        else:
            raise FileNotFoundError(f"Векторизатор {VECT2_PATH} не найден.")
    else:
        raise ValueError("Неверное значение флага. Используйте 'train' или 'test'.")
    
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0, 0]


# Нормализация столбца 'work_exp'
def normalize_column(column):
    max_value = column.max()
    min_value = column.min()
    if max_value - min_value == 0:
        return column  # Возвращаем без изменений, если все значения одинаковы
    return (column - min_value) / (max_value - min_value)


def encoding(df, flag):

    # Путь к папке для хранения энкодеров
    ENCODER_DIR = os.path.join(os.path.dirname(__file__), '../data/encoder')

    # Убедимся, что папка существует
    os.makedirs(ENCODER_DIR, exist_ok=True)

    encoder_path = os.path.join(ENCODER_DIR, 'label_encoders.pkl')

    # Категориальные столбцы
    if flag == 'train':
        categorical_columns = ['grade_proof', 'position', 'age', 'country', 'city', 
                                'key_skills', 'client_name', 'last_position', 'region', 'years']
    else:
        categorical_columns = ['position', 'age', 'country', 'city', 
                               'key_skills', 'client_name', 'last_position', 'region', 'years']

    if flag == 'train':
        # Обучаем энкодеры и сохраняем их
        label_encoders = {}
        for column in categorical_columns:
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column])
            label_encoders[column] = le

        # Сохраняем энкодеры
        with open(encoder_path, 'wb') as file:
            pickle.dump(label_encoders, file)

        print("Энкодеры сохранены.")
        return df

    elif flag == 'test':

        # Загружаем энкодеры
        if not os.path.exists(encoder_path):
            raise FileNotFoundError(f"Файл с энкодерами не найден: {encoder_path}. Сначала обучите модель (flag='train').")

        # Загружаем энкодеры
        with open(encoder_path, 'rb') as file:
            label_encoders = pickle.load(file)

        # Преобразуем тестовый набор
        for column in categorical_columns:
            if column in df.columns:
                le = label_encoders[column]
                # Обработка неизвестных категорий
                df[column] = df[column].apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )

        print("Данные тестового набора обработаны.")
        return df
    else:
        raise ValueError("flag должен быть 'train' или 'test'.")


def features(df, flag):

    # Пример словаря с оценкой престижности
    prestige_scores = {
    "ТОП Финтех": 1, "ТОП IT (сервисы, интеграторы)": 2, "ТОП Телеком": 3, "X5 Group": 4,
    "Черкизово": 15, "BIOCAD": 5, "Hoff": 20, "Яндекс Райдтех": 6, "Крок": 7,
    "Nebius": 8, "Click2Money": 30, "Pay365": 35, "OZON": 9, "РСХБ": 10, "Хеликон": 25,
    "Cloud.ru": 22, "Самолёт": 18, "Яндекс Маркет": 11, "Яндекс.Cloud": 12,
    "ТОП eCOM": 13, "IVI": 14, "Banki.ru": 16, "585 RPO": 40, "Сбер Еаптека": 21,
    "Информзащита": 17, "Казино NDA": 50, "Onpoint": 45, "Food Rocket": 32, "Hawex": 48,
    "Loymax": 28, "EggHeads": 27, "Брусника": 31, "Amdocs": 29, "ЮЛаки": 42, "Fun&Sun": 46,
    "nil.foundation": 36, "Brand Analytics": 23, "М.Видео – Эльдорадо": 24,
    "Equifax": 33, "Mercury": 34, "Прочее": 55, "МТС Банк (Аутсорс)": 26,
    "МТС (Аутсорс)": 26, "Хантфлоу": 41, "Papa John's": 43, "Национальная Лотерея": 47,
    "ЛитРес": 38, "InDrive": 37, "Просвещение": 19, "Совкомбанк": 39,
    "Национальная Медиа Группа (МСБ)": 44, "ЦБ РФ": 8, "SRG Group": 49, "Этнамед": 51,
    "Usetech": 52, "Яндекс. Такси": 10, "АО Азот-Взрыв": 53, "Glue up": 54,
    "PIM Solutions": 56, "Metaship": 57, "Sitronics": 58, "4 Лапы": 59, "Ингосстрах": 60,
    "Nestle": 6, "Auxo": 61, "Айтуби": 62, "Sunlight": 63, "Air Liquide": 64, "Т2": 65,
    "Яндекс Академия": 66
    }

    # Добавляем новый столбец prestige на основе client_name
    df['prestige'] = df['client_name'].map(prestige_scores)

    #1. Применяем функцию эйлерак DataFrame
    df = calculate_euler_similarity(df)

    #2. Считаем фичу years-delta
    df['years_delta'] = df.apply(calculate_years_delta, axis=1)

    #3. Считаем косинусные сходства

    # Применяем лемматизацию к столбцам 'position' и 'last_position'
    df['position_lemmatized'] = df['position'].apply(lemmatize_text)
    df['last_position_lemmatized'] = df['last_position'].apply(lemmatize_text)

    # Применяем вычисление косинусного сходства
    df['pos-last_pos'] = df.apply(calculate_tfidf_similarity, axis=1, flag=flag)


    # Применяем лемматизацию к столбцам 'key_skills' и 'last_position'
    df['key_skills_lemmatized'] = df['key_skills'].apply(lemmatize_text)
    df['last_position_lemmatized'] = df['last_position'].apply(lemmatize_text)

    # Применяем функцию для расчета косинусного сходства
    df['skills-last_pos'] = df.apply(calculate_skills_last_pos_similarity, axis=1, flag=flag)

    # Удаляем временные столбцы, если они больше не нужны
    df = df.drop(columns=['key_skills_lemmatized', 'last_position_lemmatized'])


    #4. # Замена значений в столбце 'work_exp' на длину текста

    def calculate_text_length(text):
        if isinstance(text, str):
            return len(text)
        return 0  # Возвращаем 0 для пустых или некорректных значений

    # Применяем функцию к столбцу 'work_exp'
    df['work_exp'] = df['work_exp'].apply(calculate_text_length)

    #5. Применяем нормализацию
    df['work_exp'] = normalize_column(df['work_exp'])

    #6. Удаляем ненужные столбцы
    df = df.drop(columns=[
        'position_lemmatized',
        'key_skills_set',
        'last_position_set',
        'is_duplicate',
        'work_experience',
    ])

    #7. label-encoder
    # Преобразование категориальных признаков в численные
    df = encoding(df, flag)


    return df