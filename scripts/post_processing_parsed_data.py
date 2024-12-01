import numpy as np
import pandas as pd
import re
from sklearn.preprocessing import LabelEncoder

def process_dataframe(df):
    # Function to convert the profit values
    def convert_profit(value):
        if value == 'Не найдено':
            return np.nan
        
        number_part = value.split()[0]
        
        try:
            number = float(number_part)
        except ValueError:
            return np.nan
        
        if number == 0:
            return np.nan
        
        if 'млн' in value:
            number *= 1_000_000
        elif 'млрд' in value:
            number *= 1_000_000_000
        elif 'тыс' in value:
            number *= 1_000
        else:
            return np.nan
        
        return number

    # Function to convert the workers.count values
    def convert_workers_count(value):
        if value == 'Не найдено':
            return np.nan
        
        match = re.search(r'\d+(?:\s*\d+)*', value)
        if match:
            number = match.group().replace(' ', '')
            return int(number)
        else:
            return np.nan

    # Apply the conversion functions
    df['employers_cnt'] = df['workers_count'].apply(convert_workers_count)
    df['Net_profit'] = df['profit'].apply(convert_profit)
    df['Benefit'] = df['benefit'].apply(convert_profit)
    df['org_form'] = df['next_word_after_full_report']
    df['amount'] = df['Benefit'] - df['Net_profit']

    # Label encode the 'next_word_after_full_report' feature
    label_encoder = LabelEncoder()
    df['org_form'] = label_encoder.fit_transform(df['org_form'].astype(str))

    # Select the desired features
    final_df = df[['short_name', 'amount', 'org_form']]

    return final_df