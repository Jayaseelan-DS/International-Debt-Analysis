
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# --- CONNECTION SETUP ---
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- LOAD COUNTRIES TABLE ---
country_meta = pd.read_csv("../data/cleaned/country_meta_cleaned.csv")
country_meta.columns = ["country_code", "country_name", "region", "income_group", "lending_category"]
country_meta.to_sql("countries", con=engine, if_exists="append", index=False)
print("Countries loaded:", len(country_meta))

# --- LOAD INDICATORS TABLE ---
# series_meta_cleaned only has Series Code + Topic; we need Indicator Name from debt data
series_meta = pd.read_csv("../data/cleaned/series_meta_cleaned.csv")
debt_data = pd.read_csv("../data/cleaned/All_country_data_cleaned.csv")

# Get unique Series Code -> Series Name mapping from debt_data
indicator_names = debt_data[["Series Code", "Series Name"]].drop_duplicates()
indicator_names.columns = ["series_code", "indicator_name"]

series_meta.columns = ["series_code", "topic"]

indicators = indicator_names.merge(series_meta, on="series_code", how="left")
indicators.to_sql("indicators", con=engine, if_exists="append", index=False)
print("Indicators loaded:", len(indicators))

# --- LOAD DEBT_DATA TABLE ---
debt_data_final = debt_data[["Country Code", "Series Code", "Year", "Value"]].copy()
debt_data_final.columns = ["country_code", "series_code", "year", "value"]
debt_data_final.to_sql("debt_data", con=engine, if_exists="append", index=False, chunksize=5000)
print("Debt data loaded:", len(debt_data_final))