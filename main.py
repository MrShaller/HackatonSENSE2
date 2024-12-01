import json
import pandas as pd

from scripts.preprocessing import preprocessing
from scripts.features import features

'''
Для того, чтобы запустить правильно на тестирование -> Поменять в if __name__ == main 
train -> test

'''


#поменять salary#поменять salary#поменять salary#поменять salary#поменять salary#поменять salary#поменять salary#поменять salary#поменять salary#поменять salary

def process_file(file_path, flag):
    """
    Обрабатывает файл, переданный через Flask.
    
    :param file_path: Путь к загруженному файлу
    :return: Результат обработки
    """
    try:
        # Пример обработки: считаем количество строк в файле
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception as e:
        raise Exception(f"Error processing file: {e}")
    

    # Преобразуем в датафрейм
    df = pd.DataFrame(data)

    #1. Обработка начального датафрейма #поменять salary#поменять salary#поменять salary#поменять salary#поменять salary
    df = preprocessing(df, flag)

    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')

    #2. post_processing
    df2 = pd.read_csv('data/postpreprocess_df.csv')
    df = pd.merge(df, df2, left_on='client_name', right_on='short_name', how='left')
    df = df.drop(columns={'Unnamed: 0', 'short_name'})
    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')

    #3. Feature eng
    df = features(df, flag)

    print(df.columns)

    return df.to_csv("data/result.csv", index=False)

    
    
if __name__ == "__main__":
    process_file(file_path='data/client_dataset.json', flag='train')
