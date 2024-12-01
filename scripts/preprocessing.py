import re
from datetime import datetime
import json

# Функция для извлечения чисел из строки
def extract_last_number(salary):
    if not isinstance(salary, str):
        return 0  # Если значение пустое, возвращаем 0

    # Находим все числа в строке
    numbers = re.findall(r'\d+', salary)

    # Если числа найдены, возвращаем последнее из них
    if numbers:
        return int(numbers[-1])

    return 0  # Если чисел нет, возвращаем 0


# Функция для заполнения пропущенных конечных дат ближайшими значениями
def fill_missing_end_dates_with_nearest(work_experience):

    # Получаем сегодняшнюю дату в формате YYYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Ищем все даты в формате "YYYY-MM-DD"
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', str(work_experience))
    if not dates:
        return work_experience  # Если дат нет, возвращаем как есть

    # Сортируем даты
    dates = sorted(set(dates))

    # Формируем список диапазонов дат
    ranges = []
    for i in range(len(dates) - 1):
        ranges.append(f"{dates[i]} - {dates[i+1]}")

    # Добавляем последний диапазон с сегодняшней датой
    if dates:
        ranges.append(f"{dates[-1]} - {today_date}")

    # Объединяем диапазоны
    return ', '.join(ranges)

def extract_years_with_nearest_dates(work_experience):
    # Заполняем пропущенные конечные даты
    processed_experience = fill_missing_end_dates_with_nearest(work_experience)
    # Возвращаем обработанные диапазоны
    return processed_experience


# Функция для подсчёта количества лет в диапазонах
def calculate_full_years(years):
    total_years = 0.0
    if not years:
        return total_years  # Если данных нет, возвращаем 0.0

    # Разбиваем диапазоны
    ranges = years.split(', ')
    for date_range in ranges:
        try:
            # Извлекаем начальную и конечную даты
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Вычисляем разницу в днях и переводим в годы
            days_diff = (end_date - start_date).days
            total_years += days_diff / 365.25  # Учитываем високосные года
        except ValueError:
            # Если формат данных некорректный, пропускаем
            continue

    return round(total_years, 2)  # Округляем до двух знаков


# Функция для очистки дублирующихся данных между одинаковыми датами
def clean_work_experience(work_experience):
    # Ищем диапазоны дат в формате YYYY-MM-DD - YYYY-MM-DD или YYYY-MM-DD -
    date_ranges = re.findall(r'\d{4}-\d{2}-\d{2} - \d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2} -', str(work_experience))

    # Уникальные диапазоны для сохранения
    unique_ranges = []
    last_date_range = None
    cleaned_text = []

    for date_range in date_ranges:
        if date_range != last_date_range:
            # Добавляем уникальный диапазон
            unique_ranges.append(date_range)
            last_date_range = date_range

    # Для каждого уникального диапазона оставляем текст только один раз
    for unique_range in unique_ranges:
        # Ищем первую часть текста, которая соответствует этому диапазону
        pattern = re.escape(unique_range) + r'(.*?)(?=\d{4}-\d{2}-\d{2} -|\Z)'
        match = re.search(pattern, work_experience, re.DOTALL)
        if match:
            # Добавляем очищенный текст для текущего диапазона
            cleaned_text.append(unique_range + match.group(1).strip())

    # Объединяем очищенные части
    return ' '.join(cleaned_text)


# Функция для извлечения уникальных дат и текста после них
def extract_unique_positions(work_exp):
    if not isinstance(work_exp, str):
        return None  # Если значение не строка, возвращаем None

    # Паттерн для поиска дат в формате YYYY-MM-DD
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    matches = re.findall(date_pattern, work_exp)

    if not matches:
        return None  # Если дат нет, возвращаем None

    # Сортируем найденные даты по убыванию
    sorted_dates = sorted(set(matches), key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse=True)

    unique_entries = []
    last_date = None
    last_text = None

    for date in sorted_dates:
        # Формируем паттерн для извлечения текста после каждой даты
        pattern = rf'{re.escape(date)}.*?:\s*(.*?)(?=\d{{4}}-\d{{2}}-\d{{2}}|$)'
        match = re.search(pattern, work_exp, re.DOTALL)

        if match:
            # Получаем текст после даты
            current_text = match.group(1).strip()

            # Проверяем, если этот блок текста уникален (не повторяется)
            if current_text != last_text:
                unique_entries.append(f'{date}: {current_text}')
                last_text = current_text  # Обновляем последний текст

    # Возвращаем только уникальные записи
    return ' '.join(unique_entries)


# Функция для извлечения последней должности по самой поздней дате
def extract_last_position(work_exp):
    if not isinstance(work_exp, str):
        return None  # Если значение не строка, возвращаем None

    # Паттерн для поиска дат в формате YYYY-MM-DD
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    matches = re.findall(date_pattern, work_exp)

    if not matches:
        return None  # Если дат нет, возвращаем None

    # Сортируем найденные даты по убыванию
    sorted_dates = sorted(matches, key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse=True)
    last_date = sorted_dates[0]  # Берём самую позднюю дату

    # Находим блок текста, связанный с последней датой
    # Учёт форматов с ":" или текстов после самой последней даты
    pattern = rf'{re.escape(last_date)}.*?:\s*(.*?)(?=\d{{4}}-\d{{2}}-\d{{2}}|$)'
    match = re.search(pattern, work_exp, re.DOTALL)

    if match:
        return match.group(1).strip()  # Возвращаем текст, связанный с последней датой

    return None  # Если текст не найден



def preprocessing(df, flag):

    if flag=='train':
        df = df.drop_duplicates() #удаляем дубликаты в записях 

    #1. Применяем функцию к столбцу 'salary' <----------------------------------------------------------ПОМЕНЯТЬ
    df['salary_2.0'] = df['salary'].apply(extract_last_number)

    #2. Применяем функцию к столбцу 'work_experience'
    if 'work_experience' in df.columns:
        # Обновляем столбец 'years' с учётом ближайших дат
        df['years'] = df['work_experience'].apply(extract_years_with_nearest_dates)

        # Проверка на дубликаты в 'years'
        def check_duplicates(years):
            dates = years.split(', ')
            return len(dates) != len(set(dates))

        # Добавляем столбец 'is_duplicate'
        df['is_duplicate'] = df['years'].apply(check_duplicates)
    else:
        print("Столбец 'work_experience' отсутствует в данных.")
    
    #3. Применяем функцию к столбцу 'years'
    if 'years' in df.columns:
        # Добавляем столбец 'full_years'
        df['full_years'] = df['years'].apply(calculate_full_years)
    else:
        print("Столбец 'years' отсутствует в данных.")

    #4. Применяем функцию к столбцу 'work_experience'
    if 'work_experience' in df.columns:
        # Создаем новый столбец 'work_exp' с очищенными данными
        df['work_exp'] = df['work_experience'].apply(clean_work_experience)
    else:
        print("Столбец 'work_experience' отсутствует в данных.")

    #5. Регионы
    # Загружаем файл russia-cities.json
    with open('data/russia-cities.json', 'r', encoding='utf-8') as file:
        cities_data = json.load(file)
    
    # Создаём словарь сопоставления городов с регионами
    city_to_region = {entry['name']: entry['region']['name'] for entry in cities_data}

    # Функция для сопоставления города с регионом
    def map_city_to_region(city):
        return city_to_region.get(city, "Неизвестный регион")

    # Добавляем столбец 'region' в DataFrame
    if 'city' in df.columns:
        df['region'] = df['city'].apply(map_city_to_region)
    else:
        print("Столбец 'city' отсутствует в данных.")

    #6. Применяем функцию к столбцу 'work_exp' и создаём новый столбец 'unique_positions' -> Удаляем дубликаты в опыте работы
    if 'work_exp' in df.columns:
        df['unique_positions'] = df['work_exp'].apply(extract_unique_positions)
    else:
        print("Столбец 'work_exp' отсутствует в данных.")

    #7. преобразуем grade_proof в цифры
    if 'grade_proof' in df.columns:
        df['grade_proof'] = df['grade_proof'].map({'не подтверждён': 0, 'подтверждён': 1})

    #8. Применяем функцию к столбцу 'work_exp' и создаём новый столбец 'last_position'
    if 'work_exp' in df.columns:
        df['last_position'] = df['work_exp'].apply(extract_last_position)
    else:
        print("Столбец 'work_exp' отсутствует в данных.")

    return df