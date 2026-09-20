
CREATE DATABASE international_debt_analysis;
USE international_debt_analysis;

CREATE TABLE countries (
    country_code VARCHAR(10) PRIMARY KEY,
    country_name VARCHAR(150) NOT NULL,
    region VARCHAR(100),
    income_group VARCHAR(50),
    lending_category VARCHAR(50)
);

CREATE TABLE indicators (
    series_code VARCHAR(30) PRIMARY KEY,
    indicator_name VARCHAR(255),
    topic VARCHAR(255)
);

CREATE TABLE debt_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(10),
    series_code VARCHAR(30),
    year INT,
    value DOUBLE,
    FOREIGN KEY (country_code) REFERENCES countries(country_code),
    FOREIGN KEY (series_code) REFERENCES indicators(series_code)
);

CREATE INDEX idx_country_code ON debt_data(country_code);
CREATE INDEX idx_series_code ON debt_data(series_code);

SHOW INDEX FROM debt_data;

SET GLOBAL net_read_timeout = 300;
SET GLOBAL net_write_timeout = 300;
SET SESSION net_read_timeout = 300;
SET SESSION net_write_timeout = 300;

DELETE FROM debt_data;
DELETE FROM indicators;
DELETE FROM countries;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM countries;

SELECT COUNT(*) FROM countries;
SELECT COUNT(*) FROM indicators;

SELECT * FROM countries;
SELECT * FROM indicators;
SELECT * FROM countries;
SELECT * FROM debt_data;

# 1) Retrieve all distinct country names from the dataset.

SELECT DISTINCT country_name
FROM countries;

# 2) Count the total number of countries available

SELECT COUNT(DISTINCT country_name) AS country
FROM countries;

# 3) Find the total number of indicators present.

SELECT COUNT(DISTINCT series_code) AS Total_Indicator
FROM indicators;

# 4) Display the first 10 records of the dataset.

SELECT * FROM debt_data LIMIT 10; 

# 5) Calculate the total global debt.

SELECT SUM(value) AS Total_Global_Debt_2024
FROM debt_data
WHERE series_code = 'DT.DOD.DECT.CD' AND year = 2024;

# 6) List all unique indicator names.

SELECT DISTINCT indicator_name
FROM indicators;

# 7) Find the number of records for each country.

SELECT country_code, COUNT(*) AS record_count
FROM debt_data
GROUP BY country_code
ORDER BY record_count DESC;

# 8) Display all records where debt is greater than 1 billion USD.

SELECT * FROM debt_data
where value > 1000000000
ORDER BY value DESC;

# 9) Find the minimum, maximum, and average debt values.

SELECT min(value) AS Min_Global_Debt, 
max(value) AS Max_Global_Debt,
avg (value) AS Avg_Global_Debt
FROM debt_data;

#WHERE series_code = 'DT.DOD.DECT.CD' AND year = 2024;

# 10) Count total number of records in the dataset.

SELECT Count(*) AS Total_number_of_records
FROM debt_data;

SELECT * FROM indicators;
SELECT * FROM countries;
SELECT * FROM debt_data;

#Intermediate Level
# 11) Find the total debt for each country.

SELECT c.country_name, SUM(dd.value) AS Total_value
FROM debt_data dd
JOIN countries c
on c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY Total_value DESC;

# 12) Display the top 10 countries with the highest total debt.

SELECT c.country_name, dd.value AS debt_2024
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
WHERE dd.series_code = 'DT.DOD.DECT.CD'
  AND dd.year = 2024
ORDER BY dd.value DESC
LIMIT 10;

# 13) Find the average debt per country.

SELECT c.country_name, avg(dd.value) AS Avg_value
FROM debt_data dd
JOIN countries c
on c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY Avg_value DESC;

# 14) Calculate total debt for each indicator.

SELECT i.indicator_name, sum(dd.value) AS Total_Debt
FROM debt_data dd
JOIN indicators i
on dd.series_code = i.series_code
GROUP BY i.series_code
ORDER BY Total_debt DESC;

# 15) Identify the indicator contributing the highest total debt.

SELECT i.indicator_name, sum(dd.value) AS Total_Debt
FROM debt_data dd
JOIN indicators i
on dd.series_code = i.series_code
GROUP BY i.series_code
ORDER BY Total_debt DESC
LIMIT 1;

#16) Find the country with the lowest total debt.

SELECT c.country_name, sum(dd.value) AS Total_Debt
FROM debt_data dd
JOIN countries c
on dd.country_code = c.country_code
GROUP BY c.country_name
ORDER BY Total_debt ASC
LIMIT 1;

# 17) Calculate total debt for each country and indicator combination.

SELECT c.country_name, i.indicator_name, SUM(dd.value) AS Total_value
FROM debt_data dd
JOIN indicators i ON dd.series_code = i.series_code
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name, i.series_code
ORDER BY Total_value DESC;

SELECT c.country_name, i.indicator_name, SUM(dd.value) AS Total_value
FROM debt_data dd
JOIN indicators i ON dd.series_code = i.series_code
JOIN countries c ON c.country_code = dd.country_code
WHERE c.country_name = 'Afghanistan'
GROUP BY c.country_name, i.series_code
ORDER BY Total_value DESC;

#18) Count how many indicators each country has.

SELECT c.country_name, COUNT(DISTINCT i.series_code) AS Indicator_count
FROM debt_data dd
JOIN indicators i ON dd.series_code = i.series_code
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY Indicator_count DESC;

#19) Display countries whose total debt is above the global average.

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

# 20) Rank countries based on total debt (highest to lowest).

SELECT country_name, 
       Total_value, 
       RANK() OVER (ORDER BY Total_value DESC) AS ranking
FROM (
    SELECT
        c.country_name,
        SUM(dd.value) AS Total_value
    FROM debt_data dd
    JOIN countries c ON c.country_code = dd.country_code
    GROUP BY c.country_name
) AS country_total;

# 21) Find the top 5 indicators contributing most to global debt.

SELECT i.indicator_name, sum(dd.value) AS Total_Debt
FROM debt_data dd
JOIN indicators i
on dd.series_code = i.series_code
GROUP BY i.series_code
ORDER BY Total_debt DESC
LIMIT 5;

# 22) Calculate percentage contribution of each country to total global debt.

SELECT 
    c.country_name, 
    SUM(dd.value) AS country_total,
    (SUM(dd.value) / (SELECT SUM(value) FROM debt_data)) * 100 AS percentage_contribution
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY percentage_contribution DESC;

# 23) Identify the top 3 countries for each indicator based on debt.

SELECT indicator_name, country_name, value, rnk
FROM (
    SELECT 
        i.indicator_name,
        c.country_name,
        dd.value,
        RANK() OVER (PARTITION BY dd.series_code ORDER BY dd.value DESC) AS rnk
    FROM debt_data dd
    JOIN countries c ON c.country_code = dd.country_code
    JOIN indicators i ON i.series_code = dd.series_code
    WHERE dd.year = 2024
) AS ranked
WHERE rnk <= 3
ORDER BY indicator_name, rnk;

# 24) Find the difference between maximum and minimum debt for each country.

SELECT 
    c.country_name,
    MAX(dd.value) AS max_debt,
    MIN(dd.value) AS min_debt,
    MAX(dd.value) - MIN(dd.value) AS debt_difference
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY debt_difference DESC;

# 25) Create a view for the top 10 countries with highest debt.

CREATE VIEW top_10_countries_debt AS
SELECT c.country_name, SUM(dd.value) AS total_debt
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY total_debt DESC
LIMIT 10;


# 26) Categorize countries into:
#High Debt
#Medium Debt
#Low Debt (based on thresholds)

SELECT 
    c.country_name,
    SUM(dd.value) AS total_debt,
    CASE 
        WHEN SUM(dd.value) >= 5000000000000 THEN 'High Debt'
        WHEN SUM(dd.value) >= 1000000000000 THEN 'Medium Debt'
        ELSE 'Low Debt'
    END AS debt_category
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name
ORDER BY total_debt DESC;

# 27) Use window functions to calculate cumulative debt per country.

SELECT 
    c.country_name,
    dd.year,
    dd.value,
    SUM(dd.value) OVER (PARTITION BY c.country_name ORDER BY dd.year) AS cumulative_debt
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
WHERE dd.series_code = 'DT.DOD.DECT.CD'
ORDER BY c.country_name, dd.year;

# 28) Find indicators where average debt is higher than overall average debt.

SELECT 
    i.indicator_name,
    AVG(dd.value) AS avg_indicator_debt
FROM debt_data dd
JOIN indicators i ON i.series_code = dd.series_code
GROUP BY i.indicator_name
HAVING AVG(dd.value) > (
    SELECT AVG(value) FROM debt_data
)
ORDER BY avg_indicator_debt DESC;

# 29) Identify countries contributing more than 5% of global debt.

SELECT 
    c.country_name, 
    SUM(dd.value) AS country_total,
    (SUM(dd.value) / (SELECT SUM(value) FROM debt_data)) * 100 AS percentage_contribution
FROM debt_data dd
JOIN countries c ON c.country_code = dd.country_code
GROUP BY c.country_name
HAVING percentage_contribution > 5
ORDER BY percentage_contribution DESC;

# 30) Find the most dominant indicator (highest contribution) for each country.

SELECT country_name, indicator_name, total_value, rnk
FROM (
    SELECT 
        c.country_name,
        i.indicator_name,
        SUM(dd.value) AS total_value,
        RANK() OVER (PARTITION BY c.country_name ORDER BY SUM(dd.value) DESC) AS rnk
    FROM debt_data dd
    JOIN countries c ON c.country_code = dd.country_code
    JOIN indicators i ON i.series_code = dd.series_code
    GROUP BY c.country_name, i.indicator_name
) AS ranked
WHERE rnk = 1
ORDER BY country_name;






























