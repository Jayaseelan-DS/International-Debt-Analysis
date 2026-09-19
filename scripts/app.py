
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# --- CONNECTION ---
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- QUESTIONS + QUERIES DICTIONARY ---
queries = {
    "1. Retrieve all distinct country names": """
        SELECT DISTINCT country_name FROM countries;
    """,
    "2. Count the total number of countries": """
        SELECT COUNT(DISTINCT country_name) AS country FROM countries;
    """,
    "3. Find the total number of indicators": """
        SELECT COUNT(DISTINCT series_code) AS Total_Indicator FROM indicators;
    """,
    "4. Display the first 10 records of the dataset": """
        SELECT * FROM debt_data LIMIT 10;
    """,
    "5. Calculate the total global debt (2024)": """
        SELECT SUM(value) AS Total_Global_Debt_2024
        FROM debt_data
        WHERE series_code = 'DT.DOD.DECT.CD' AND year = 2024;
    """,
    "6. List all unique indicator names": """
        SELECT DISTINCT indicator_name FROM indicators;
    """,
    "7. Find the number of records for each country": """
        SELECT country_code, COUNT(*) AS record_count
        FROM debt_data
        GROUP BY country_code
        ORDER BY record_count DESC;
    """,
    "8. Display all records where debt is greater than 1 billion USD": """
        SELECT * FROM debt_data
        WHERE value > 1000000000
        ORDER BY value DESC;
    """,
    "9. Find the minimum, maximum, and average debt values": """
        SELECT MIN(value) AS Min_Global_Debt,
               MAX(value) AS Max_Global_Debt,
               AVG(value) AS Avg_Global_Debt
        FROM debt_data;
    """,
    "10. Count total number of records in the dataset": """
        SELECT COUNT(*) AS Total_number_of_records FROM debt_data;
    """,
    "11. Find the total debt for each country": """
        SELECT c.country_name, SUM(dd.value) AS Total_value
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        ORDER BY Total_value DESC;
    """,
    "12. Top 10 countries with the highest total debt (2024)": """
        SELECT c.country_name, dd.value AS debt_2024
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        WHERE dd.series_code = 'DT.DOD.DECT.CD' AND dd.year = 2024
        ORDER BY dd.value DESC
        LIMIT 10;
    """,
    "13. Find the average debt per country": """
        SELECT c.country_name, AVG(dd.value) AS Avg_value
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        ORDER BY Avg_value DESC;
    """,
    "14. Calculate total debt for each indicator": """
        SELECT i.indicator_name, SUM(dd.value) AS Total_Debt
        FROM debt_data dd
        JOIN indicators i ON dd.series_code = i.series_code
        GROUP BY i.series_code
        ORDER BY Total_Debt DESC;
    """,
    "15. Indicator contributing the highest total debt": """
        SELECT i.indicator_name, SUM(dd.value) AS Total_Debt
        FROM debt_data dd
        JOIN indicators i ON dd.series_code = i.series_code
        GROUP BY i.series_code
        ORDER BY Total_Debt DESC
        LIMIT 1;
    """,
    "16. Country with the lowest total debt": """
        SELECT c.country_name, SUM(dd.value) AS Total_Debt
        FROM debt_data dd
        JOIN countries c ON dd.country_code = c.country_code
        GROUP BY c.country_name
        ORDER BY Total_Debt ASC
        LIMIT 1;
    """,
    "17. Total debt for each country and indicator combination": """
        SELECT c.country_name, i.indicator_name, SUM(dd.value) AS Total_value
        FROM debt_data dd
        JOIN indicators i ON dd.series_code = i.series_code
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name, i.series_code
        ORDER BY Total_value DESC
        LIMIT 5000;
    """,
    "18. Count how many indicators each country has": """
        SELECT c.country_name, COUNT(DISTINCT i.series_code) AS Indicator_count
        FROM debt_data dd
        JOIN indicators i ON dd.series_code = i.series_code
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        ORDER BY Indicator_count DESC;
    """,
    "19. Countries whose total debt is above the global average": """
        SELECT c.country_name, SUM(dd.value) AS Total_debt
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        HAVING SUM(dd.value) > (
            SELECT AVG(total) FROM (
                SELECT SUM(value) AS total
                FROM debt_data
                GROUP BY country_code
            ) AS country_totals
        )
        ORDER BY Total_debt DESC;
    """,
    "20. Rank countries based on total debt": """
        SELECT country_name, Total_value,
               RANK() OVER (ORDER BY Total_value DESC) AS ranking
        FROM (
            SELECT c.country_name, SUM(dd.value) AS Total_value
            FROM debt_data dd
            JOIN countries c ON c.country_code = dd.country_code
            GROUP BY c.country_name
        ) AS country_total;
    """,
    "21. Top 5 indicators contributing most to global debt": """
        SELECT i.indicator_name, SUM(dd.value) AS Total_Debt
        FROM debt_data dd
        JOIN indicators i ON dd.series_code = i.series_code
        GROUP BY i.series_code
        ORDER BY Total_Debt DESC
        LIMIT 5;
    """,
    "22. Percentage contribution of each country to total global debt": """
        SELECT c.country_name, SUM(dd.value) AS country_total,
               (SUM(dd.value) / (SELECT SUM(value) FROM debt_data)) * 100 AS percentage_contribution
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        ORDER BY percentage_contribution DESC;
    """,
    "23. Top 3 countries for each indicator (2024)": """
        SELECT indicator_name, country_name, value, rnk
        FROM (
            SELECT i.indicator_name, c.country_name, dd.value,
                   RANK() OVER (PARTITION BY dd.series_code ORDER BY dd.value DESC) AS rnk
            FROM debt_data dd
            JOIN countries c ON c.country_code = dd.country_code
            JOIN indicators i ON i.series_code = dd.series_code
            WHERE dd.year = 2024
        ) AS ranked
        WHERE rnk <= 3
        ORDER BY indicator_name, rnk;
    """,
    "24. Difference between max and min debt for each country": """
        SELECT c.country_name,
               MAX(dd.value) AS max_debt,
               MIN(dd.value) AS min_debt,
               MAX(dd.value) - MIN(dd.value) AS debt_difference
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        ORDER BY debt_difference DESC;
    """,
    "25. Top 10 countries with highest debt (view)": """
        SELECT * FROM top_10_countries_debt;
    """,
    "26. Categorize countries into High/Medium/Low Debt": """
        SELECT c.country_name, SUM(dd.value) AS total_debt,
               CASE
                   WHEN SUM(dd.value) >= 5000000000000 THEN 'High Debt'
                   WHEN SUM(dd.value) >= 1000000000000 THEN 'Medium Debt'
                   ELSE 'Low Debt'
               END AS debt_category
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        ORDER BY total_debt DESC;
    """,
    "27. Cumulative debt per country (window function)": """
        SELECT c.country_name, dd.year, dd.value,
               SUM(dd.value) OVER (PARTITION BY c.country_name ORDER BY dd.year) AS cumulative_debt
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        WHERE dd.series_code = 'DT.DOD.DECT.CD'
        ORDER BY c.country_name, dd.year;
    """,
    "28. Indicators where average debt is higher than overall average": """
        SELECT i.indicator_name, AVG(dd.value) AS avg_indicator_debt
        FROM debt_data dd
        JOIN indicators i ON i.series_code = dd.series_code
        GROUP BY i.indicator_name
        HAVING AVG(dd.value) > (SELECT AVG(value) FROM debt_data)
        ORDER BY avg_indicator_debt DESC;
    """,
    "29. Countries contributing more than 5% of global debt": """
        SELECT c.country_name, SUM(dd.value) AS country_total,
               (SUM(dd.value) / (SELECT SUM(value) FROM debt_data)) * 100 AS percentage_contribution
        FROM debt_data dd
        JOIN countries c ON c.country_code = dd.country_code
        GROUP BY c.country_name
        HAVING percentage_contribution > 5
        ORDER BY percentage_contribution DESC;
    """,
    "30. Most dominant indicator for each country": """
        SELECT country_name, indicator_name, total_value, rnk
        FROM (
            SELECT c.country_name, i.indicator_name, SUM(dd.value) AS total_value,
                   RANK() OVER (PARTITION BY c.country_name ORDER BY SUM(dd.value) DESC) AS rnk
            FROM debt_data dd
            JOIN countries c ON c.country_code = dd.country_code
            JOIN indicators i ON i.series_code = dd.series_code
            GROUP BY c.country_name, i.indicator_name
        ) AS ranked
        WHERE rnk = 1
        ORDER BY country_name;
    """,
}

# --- STREAMLIT UI ---
st.set_page_config(page_title="International Debt Analysis", layout="wide")
st.title("🌍 International Debt Analysis — SQL Query Explorer")
st.write("Select a question below to run its corresponding SQL query and view the result.")

selected_question = st.selectbox("Choose a question:", list(queries.keys()))

if st.button("Run Query"):
    query = queries[selected_question]
    with st.spinner("Running query..."):
        result = pd.read_sql(query, con=engine)
    st.subheader("SQL Query")
    st.code(query, language="sql")
    st.subheader(f"Result ({len(result)} rows)")
    st.dataframe(result, use_container_width=True)