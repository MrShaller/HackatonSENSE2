import pandas as pd
import re
import numpy as np

# Функция для извлечения чисел из строки
import re

# Функция для извлечения чисел из строки
def extract_last_number(salary, days=20):
    if not isinstance(salary, str):
        return 0  # Если значение пустое, возвращаем 0

    # Приводим строку к нижнему регистру, чтобы обработка не зависела от регистра
    salary = salary.lower()

    # Проверка на наличие слова "ставка" и числа рядом с ним
    rate_match = re.search(r'rate\s*per\s*day\s*(\d{1,6})', salary)  # Изменено на английский
    if rate_match:
        rate_value = int(rate_match.group(1))
        if rate_value <= 100000:  # Если ставка меньше 100000, умножаем на 20 дней
            total_salary = rate_value * days
            return total_salary

    # Проверка на наличие ставки в день, чтобы умножить на количество дней
    daily_match = re.search(r'(\d{1,3}(?:[\s,.]?\d{3})*)\s*(per\s*day|/day|/ per day)', salary)
    if daily_match:
        daily_rate = daily_match.group(1).replace(' ', '').replace(',', '').replace('.', '')
        try:
            daily_rate = int(daily_rate)
            total_salary = daily_rate * days
            return total_salary
        except ValueError:
            return 0

    # Проверка на число с точкой, например, "30.000 ставка"
    dot_match = re.search(r'(\d{1,3}(?:[\.,]?\d{3})*)\s*rate', salary)  # Переписано на английский
    if dot_match:
        rate_value = dot_match.group(1).replace(' ', '').replace(',', '').replace('.', '')
        try:
            rate_value = int(rate_value)
            total_salary = rate_value * days
            return total_salary
        except ValueError:
            return 0

    # Регулярное выражение для поиска чисел
    numbers = re.findall(r'\d{1,3}(?:[\s,.]?\d{3})*(?:\s*(?:net|on\s*hands)?)?', salary)

    # Преобразуем числа в стандартный вид (удаляем запятые и точки, если это необходимо)
    cleaned_numbers = []
    for number in numbers:
        cleaned_number = re.sub(r'(net|on\s*hands)', '', number).replace(' ', '').replace(',', '').replace('.', '')
        try:
            cleaned_numbers.append(int(cleaned_number))
        except ValueError:
            pass

    # Проверка на слияние чисел: если длина числа больше 6 цифр, обрезаем до 6
    if cleaned_numbers:
        for i in range(len(cleaned_numbers)):
            if len(str(cleaned_numbers[i])) > 6:
                cleaned_numbers[i] = int(str(cleaned_numbers[i])[:6])

    # Если найдено несколько чисел, возвращаем наибольшее из них
    if cleaned_numbers:
        return max(cleaned_numbers)
    return 0  # Если чисел нет, возвращаем 0


def process_salaries(df):
    """
    Обрабатывает столбцы salary и salary_2.0 в датафрейме, преобразуя их в соответствии с условиями.

    :param df: pandas DataFrame с колонками salary и salary_2.0
    :return: pandas DataFrame с обновленными значениями в колонках
    """

    def transform_salary(row):
        salary = row['salary'].lower()  # Преобразуем в нижний регистр
        salary_2_0 = row['salary_2.0']


        # Условие 1: salary_2.0 > 60 и < 100
        if 60 < salary_2_0 < 100:
            return salary_2_0 * 1000

        # Условие 2: salary_2.0 < 60 и в salary есть слова "ставка" или "день"
        if salary_2_0 < 60 and ('ставка' in salary or 'день' in salary):
            return salary_2_0 * 1000 * 20

        # Условие 3: salary_2.0 больше 100, но меньше 1000
        if 100 <= salary_2_0 < 1000:
            return salary_2_0 * 1000
        if salary_2_0 < 60:
          return 0
        
        if 10000 < salary_2_0 < 60000 and ('ставка' in salary or 'день' in salary or 'ставку' in salary):
            return salary_2_0 * 20

        if 1000 < salary_2_0 <= 10000:
            return salary_2_0 * 100

        # Если ни одно из условий не выполнено, возвращаем исходное значение salary_2.0
        return salary_2_0

        

    # Применяем функцию transform_salary к каждому ряду датафрейма
    df['salary_2.0'] = df.apply(transform_salary, axis=1)

    return df



# Функция для замены 0.0 медианами
def replace_zeros_with_median(dataframe, column):
    # Фильтруем данные, исключая строки с 0.0
    non_zero_df = dataframe[dataframe[column] != 0.0]

    # Считаем медиану по группировке (по client_name и position)
    median_values = non_zero_df.groupby(['client_name', 'position'])[column].median()

    # Преобразуем медианы в словарь для быстрого доступа
    median_dict = median_values.to_dict()

    # Функция для замены 0.0 на медианные значения
    def fill_median(row):
        if np.isclose(row[column], 0.0):  # Если значение близко к 0.0
            key = (row['client_name'], row['position'])  # Группа: (client_name, position)
            return median_dict.get(key, row[column])  # Возвращаем медиану или оставляем оригинальное значение
        return row[column]  # Если значение не 0.0, оставляем как есть

    # Применяем функцию к DataFrame
    dataframe[column] = dataframe.apply(fill_median, axis=1)
    return dataframe




# Функция для замены 0.0 медианами
def replace_zeros_with_median2(dataframe, column):
    # Фильтруем данные, исключая строки с 0.0
    non_zero_df = dataframe[dataframe[column] != 0.0]

    # Считаем медиану по группировке (по client_name и position)
    median_values = non_zero_df.groupby(['client_name', 'country'])[column].median()

    # Преобразуем медианы в словарь для быстрого доступа
    median_dict = median_values.to_dict()

    # Функция для замены 0.0 на медианные значения
    def fill_median(row):
        if np.isclose(row[column], 0.0):  # Если значение близко к 0.0
            key = (row['client_name'], row['country'])  # Группа: (client_name, position)
            return median_dict.get(key, row[column])  # Возвращаем медиану или оставляем оригинальное значение
        return row[column]  # Если значение не 0.0, оставляем как есть

    # Применяем функцию к DataFrame
    dataframe[column] = dataframe.apply(fill_median, axis=1)
    return dataframe


# Функция для замены 0.0 медианами
def replace_zeros_with_median3(dataframe, column):
    # Фильтруем данные, исключая строки с 0.0
    non_zero_df = dataframe[dataframe[column] != 0.0]

    # Считаем медиану по группировке (по client_name и position)
    median_values = non_zero_df.groupby(['client_name'])[column].median()

    # Преобразуем медианы в словарь для быстрого доступа
    median_dict = median_values.to_dict()

    # Функция для замены 0.0 на медианные значения
    def fill_median(row):
        if np.isclose(row[column], 0.0):  # Если значение близко к 0.0
            key = (row['client_name'])  # Группа: (client_name, position)
            return median_dict.get(key, row[column])  # Возвращаем медиану или оставляем оригинальное значение
        return row[column]  # Если значение не 0.0, оставляем как есть

    # Применяем функцию к DataFrame
    dataframe[column] = dataframe.apply(fill_median, axis=1)
    return dataframe



# Функция для замены 0.0 медианами
def replace_zeros_with_median4(dataframe, column):
    # Фильтруем данные, исключая строки с 0.0
    non_zero_df = dataframe[dataframe[column] != 0.0]

    # Считаем медиану по группировке (по client_name и position)
    median_values = non_zero_df.groupby(['country'])[column].median()

    # Преобразуем медианы в словарь для быстрого доступа
    median_dict = median_values.to_dict()

    # Функция для замены 0.0 на медианные значения
    def fill_median(row):
        if np.isclose(row[column], 0.0):  # Если значение близко к 0.0
            key = (row['country'])  # Группа: (client_name, position)
            return median_dict.get(key, row[column])  # Возвращаем медиану или оставляем оригинальное значение
        return row[column]  # Если значение не 0.0, оставляем как есть

    # Применяем функцию к DataFrame
    dataframe[column] = dataframe.apply(fill_median, axis=1)
    return dataframe





def salaries(df):
    # Применяем функцию к столбцу 'salary' 
    df['salary_2.0'] = df['salary'].apply(extract_last_number)

    df = process_salaries(df)

    # Применяем функцию к DataFrame
    df = replace_zeros_with_median(df, 'salary_2.0')

    # Применяем функцию к DataFrame
    df = replace_zeros_with_median2(df, 'salary_2.0')

    # Применяем функцию к DataFrame
    df = replace_zeros_with_median3(df, 'salary_2.0')

    # Применяем функцию к DataFrame
    df = replace_zeros_with_median4(df, 'salary_2.0')

    return df
