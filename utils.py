import pandas as pd
import yaml
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import joblib
from fuzzywuzzy import process 

def fetch_data_from_db(sql_query: str) -> pd.DataFrame:
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        con = psycopg2.connect(
            dbname=config['database_config']['dbname'],
            user=config['database_config']['user'],
            password=config['database_config']['password'],
            host=config['database_config']['host'],
        )
        
        cursor = con.cursor()
        cursor.execute(sql_query)
        
        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
    
    return df


def fill_na(df: pd.DataFrame) -> None:
    for col in df.columns:
        if df[col].dtype == 'object':  
            moda = df[col].mode()
            if not moda.empty:  
                moda = moda[0]
            df[col] = df[col].fillna(moda)  
        else:  
            median = df[col].median()
            df[col] = df[col].fillna(median)
            

def fix_categoric_errors(df: pd.DataFrame,coluna: str, lista_valida: list) -> None:
    for i, valor in enumerate(df[coluna]):
        valor_str = str(valor) if pd.notnull(valor) else valor
        
        if valor_str not in lista_valida and pd.notnull(valor_str):
            fix = process.extractOne(valor_str, lista_valida)[0]
            df.at[i,coluna] = fix

def fix_outliers(df: pd.DataFrame,coluna: str, min: float , max: float) -> pd.DataFrame:
    median = df[(df[coluna] >= min) & (df[coluna] <= max)][coluna].median()
    df[coluna] = df[coluna].apply(lambda x: median if x < min or x > max else x)
    return df

def save_scalers(df: pd.DataFrame, name_columns) -> pd.DataFrame:
    for name_column in  name_columns:
        scaler = StandardScaler()
        df[name_column] = scaler.fit_transform(df[[name_column]])
        joblib.dump(scaler, f'./data/silver/scaler_{name_column}.joblib')
    return df

def save_encoders(df: pd.DataFrame, name_columns) -> pd.DataFrame:
    for name_column in  name_columns:
        encoder = LabelEncoder()
        df[name_column] = encoder.fit_transform(df[name_column])
        joblib.dump(encoder, f'./data/silver/encoder_{name_column}.joblib')
    return df