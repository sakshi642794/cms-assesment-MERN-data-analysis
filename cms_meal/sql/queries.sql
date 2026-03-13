-- Example analytical queries

-- 1) Trend for a selected country and indicator
SELECT
  f.year,
  f.value
FROM fact_country_year_indicator f
WHERE f.iso3 = 'IND'
  AND f.ind_code = 'WHOSIS_000001'
ORDER BY f.year;

-- 2) Compare GDP per capita vs life expectancy for a given year
SELECT
  g.iso3,
  g.value AS gdp_per_capita,
  l.value AS life_expectancy
FROM fact_country_year_indicator g
JOIN fact_country_year_indicator l
  ON g.iso3 = l.iso3
 AND g.year = l.year
WHERE g.ind_code = 'NY.GDP.PCAP.CD'
  AND l.ind_code = 'WHOSIS_000001'
  AND g.year = 2020;

-- 3) Top countries by population (example)
SELECT
  f.iso3,
  f.value AS population
FROM fact_country_year_indicator f
WHERE f.ind_code = 'SP.POP.TOTL'
  AND f.year = 2020
ORDER BY population DESC
LIMIT 10;
