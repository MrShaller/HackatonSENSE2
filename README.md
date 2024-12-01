# README.md

## Описание проекта

Проект представляет собой систему обработки и анализа данных о кандидатах, которая включает в себя предобработку данных, извлечение признаков, расчёт различных метрик схожести и использование обученной модели XGBoost для классификации кандидатов. 

Цель — определить, подходит ли кандидат под заданные критерии вакансии.

---

## Основной функционал

1. **Обработка данных:**
   - Нормализация текста.
   - Расчёт сходства между навыками и должностями с использованием TF-IDF и косинусного сходства.
   - Работа с датами опыта работы кандидатов.
   - Определение последней должности, регионов, уникальных позиций и ключевых навыков.
   - Нормализация числовых данных и лемматизация текста.

2. **Классификация:**
   - Используется обученная модель XGBoost, расположенная в папке `models`, для классификации кандидатов.

3. **Веб-интерфейс:**
   - Загрузка данных через пользовательский интерфейс.
   - Отображение прогресса обработки данных.
   - Возможность скачать результат обработки.

---

## Структура проекта

Проект организован следующим образом:

```plaintext
HackatonSENSE2/
├── data/
│   ├── encoder/
│   │   ├── postpreprocess_df.csv
│   │   ├── russia-cities.json
│   │   ├── salaries.txt
│   │   └── unique_salaries.txt
│   └── result.csv
├── models/
│   └── xgboost_model.pkl
├── notebook/
│   └── SENSE2.ipynb
├── results/
│   └── result.csv
├── scripts/
│   ├── __init__.py
│   ├── features.py
│   ├── post_processing_parsed_data.py
│   └── preprocessing.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   │   ├── fic_logo.png
│   │   └── a_logo.png
│   └── js/
│       └── script.js
├── templates/
│   └── index.html
├── uploads/
├── .gitignore
├── app.py
├── demo.mp4
├── HackatonSENSE2.rar
├── main.py
└── requirements.txt
```

---

## Основные папки и файлы

### 1. **data/**
- **encoder/** — включает данные для преобразования категориальных признаков.
  - `postpreprocess_df.csv` — файл для постобработки данных.
  - `russia-cities.json` — сопоставление городов и регионов России.
  - `salaries.txt` и `unique_salaries.txt` — текстовые данные о зарплатах.
- `result.csv` — результирующий файл после обработки данных.

### 2. **models/**
- `xgboost_model.pkl` — обученная модель XGBoost для классификации кандидатов.

### 3. **notebook/**
- `SENSE2.ipynb` — Jupyter Notebook для анализа данных.

### 4. **results/**
- `result.csv` — файл с результатами классификации.

### 5. **scripts/**
- `preprocessing.py` — модуль предобработки данных.
- `features.py` — модуль извлечения признаков.
- `post_processing_parsed_data.py` — модуль постобработки.

### 6. **static/**
- `css/` — стили для веб-интерфейса.
- `images/` — изображения для интерфейса.
- `js/` — JavaScript для интерактивности.

### 7. **templates/**
- `index.html` — главная страница веб-интерфейса.

### 8. **uploads/**
- Папка для загрузки файлов пользователями.

### 9. **app.py**
- Основной файл для запуска Flask-приложения.

### 10. **main.py**
- Скрипт для обработки данных.

---

Требуемая структура входного файла и формат выходного файла:

Входной файл должен быть в формате JSON и содержать данные о кандидатах. Основные требования к структуре файла:
Наличие полей, присутствующих в train-файле


---

Выходной файл сохраняется в формате CSV и содержит следующие столбцы:

id: Уникальный идентификатор кандидата (соответствует полю id во входном файле).

predict_proba: Вероятность того, что кандидат подходит для заданной вакансии.

Тип: float (значение от 0.0 до 1.0).

Пример выходного файла (CSV):
csv
id,predict_proba
1,0.87
2,0.45

---
## Запуск проекта

1. Установите необходимые библиотеки:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите сервер:
   ```bash
   python app.py
   ```

3. Перейдите в браузер и откройте страницу:
   ```plaintext
   http://127.0.0.1:5000/
   ```

---

## Использование

1. Загрузите файл с данными кандидатов через веб-интерфейс.
2. Дождитесь завершения обработки.
3. Скачайте обработанный файл с результатами.

---

## Примечания

- Обработанные данные и результаты классификации сохраняются в папке `results/`.

---

## Авторы

Проект был реализован командой *Василеостровская община* для хакатона.
