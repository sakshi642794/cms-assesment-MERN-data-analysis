-- Analytical model (star schema)
-- Dimensions
CREATE TABLE dim_country (
  iso3 TEXT PRIMARY KEY,
  country TEXT
);

CREATE TABLE dim_indicator (
  ind_code TEXT PRIMARY KEY,
  indicator TEXT,
  source TEXT,
  unit TEXT
);

-- Fact table
CREATE TABLE fact_country_year_indicator (
  iso3 TEXT,
  year INTEGER,
  ind_code TEXT,
  value REAL,
  country TEXT,
  indicator TEXT,
  source TEXT,
  unit TEXT
);

CREATE INDEX idx_fact_country_year ON fact_country_year_indicator(iso3, year);
CREATE INDEX idx_fact_indicator ON fact_country_year_indicator(ind_code);
