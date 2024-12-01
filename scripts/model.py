import joblib
import os
import numpy as np
import pandas as pd


# Пути для сохранения модели и векторизатора
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/model_xgboost.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), '../data/tfidf_vectorizer_hack.pkl')


def load_model():
    """Функция для загрузки модели и векторизатора"""
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print("Модель и векторизатор загружены.")
        return model, vectorizer
    else:
        print("Модель или векторизатор не найдены!")
        return None, None
    

def modeltesting(df):

    if 'grade_proof' in df.columns:
        df = df.drop(columns=['grade_proof'])
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    model, vectorizer = load_model()
    if model is None or vectorizer is None:
        print("Ошибка: не удалось загрузить модель или векторизатор.")
        return
    print('1')
    # Преобразуем текстовые данные с помощью того же векторизатора
    X_new_tfidf = vectorizer.transform(df['unique_positions'])
    print('2')
    # Обрабатываем числовые признаки
    numerical_features = df.drop(columns=['unique_positions']).columns
    X_new_num = df[numerical_features].values
    print('3')
    # Объединяем текстовые и числовые признаки
    X_new_combined = np.hstack((X_new_tfidf.toarray(), X_new_num))
    print('4')
    # Прогнозируем с помощью загруженной модели
    y_pred = model.predict(X_new_combined)
    y_pred_proba = model.predict_proba(X_new_combined)[:, 1]
    print('5')
    # Получаем ID (индекс) для каждого человека
    df_predictions = pd.DataFrame({
        'ID': df.index,  # Или замените на нужный столбец с ID, если он есть
        'predict_proba': y_pred_proba
    })
    print('6')
    return df_predictions
    
