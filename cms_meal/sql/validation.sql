-- Basic data validation checks

-- Null checks
SELECT COUNT(*) AS null_iso3
FROM fact_country_year_indicator
WHERE iso3 IS NULL;

SELECT COUNT(*) AS null_year
FROM fact_country_year_indicator
WHERE year IS NULL;

SELECT COUNT(*) AS null_value
FROM fact_country_year_indicator
WHERE value IS NULL;

-- Duplicate check
SELECT iso3, year, ind_code, COUNT(*) AS cnt
FROM fact_country_year_indicator
GROUP BY iso3, year, ind_code
HAVING COUNT(*) > 1;

-- Range check: GDP per capita should be non-negative
SELECT COUNT(*) AS negative_gdp
FROM fact_country_year_indicator
WHERE ind_code = 'NY.GDP.PCAP.CD'
  AND value < 0;
