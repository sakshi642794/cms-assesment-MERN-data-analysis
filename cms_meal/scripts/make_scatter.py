import math
from pathlib import Path

import pandas as pd


def scale(value, vmin, vmax, out_min, out_max):
    if vmax == vmin:
        return (out_min + out_max) / 2
    return out_min + (value - vmin) * (out_max - out_min) / (vmax - vmin)


def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    base_dir = Path(__file__).resolve().parents[1]
    data_path = base_dir / "data" / "processed" / "fact_country_year_indicator.csv"
    out_path = base_dir / "dashboard" / "scatter_gdp_vs_health_expenditure.svg"

    df = pd.read_csv(data_path)

    ind_map = {
        "NY.GDP.PCAP.CD": "gdp_per_capita",
        "SH.XPD.CHEX.PC.CD": "health_expenditure_pc",
        "SP.POP.TOTL": "population",
    }

    df = df[df["ind_code"].isin(ind_map)].copy()
    df["indicator_short"] = df["ind_code"].map(ind_map)

    wide = (
        df.pivot_table(
            index=["iso3", "country", "year"],
            columns="indicator_short",
            values="value",
            aggfunc="mean",
        )
        .reset_index()
    )

    wide = wide.dropna(subset=["gdp_per_capita", "health_expenditure_pc"])
    if wide.empty:
        raise SystemExit("No rows with both GDP per capita and health expenditure per capita.")

    latest_year = int(wide["year"].max())
    plot_df = wide[wide["year"] == latest_year].copy()

    # Log scale for GDP per capita
    plot_df = plot_df[plot_df["gdp_per_capita"] > 0]
    plot_df["gdp_log"] = plot_df["gdp_per_capita"].apply(lambda v: math.log10(v))

    # Size based on population
    if "population" in plot_df.columns and not plot_df["population"].isna().all():
        pop = plot_df["population"].fillna(plot_df["population"].median())
        r = (pop / pop.max()) * 14 + 4
    else:
        r = pd.Series([8] * len(plot_df), index=plot_df.index)

    width, height = 1000, 600
    margin = dict(left=90, right=40, top=60, bottom=80)
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]

    x_min, x_max = plot_df["gdp_log"].min(), plot_df["gdp_log"].max()
    y_min, y_max = plot_df["health_expenditure_pc"].min(), plot_df["health_expenditure_pc"].max()

    # Add small padding
    x_pad = (x_max - x_min) * 0.05
    y_pad = (y_max - y_min) * 0.05
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad

    def x_to_svg(x):
        return scale(x, x_min, x_max, margin["left"], margin["left"] + plot_w)

    def y_to_svg(y):
        return scale(y, y_min, y_max, margin["top"] + plot_h, margin["top"])

    svg = []
    svg.append(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>")
    svg.append("<rect width='100%' height='100%' fill='white' />")

    # Axes
    x0 = margin["left"]
    y0 = margin["top"] + plot_h
    x1 = margin["left"] + plot_w
    y1 = margin["top"]
    svg.append(f"<line x1='{x0}' y1='{y0}' x2='{x1}' y2='{y0}' stroke='#333' />")
    svg.append(f"<line x1='{x0}' y1='{y0}' x2='{x0}' y2='{y1}' stroke='#333' />")

    # X ticks (log scale)
    tick_start = int(math.floor(x_min))
    tick_end = int(math.ceil(x_max))
    for t in range(tick_start, tick_end + 1):
        val = 10 ** t
        x = x_to_svg(t)
        svg.append(f"<line x1='{x}' y1='{y0}' x2='{x}' y2='{y0 + 6}' stroke='#333' />")
        svg.append(
            f"<text x='{x}' y='{y0 + 24}' font-size='12' text-anchor='middle' fill='#333'>{val:,.0f}</text>"
        )

    # Y ticks
    for i in range(6):
        v = y_min + (y_max - y_min) * i / 5
        y = y_to_svg(v)
        svg.append(f"<line x1='{x0 - 6}' y1='{y}' x2='{x0}' y2='{y}' stroke='#333' />")
        svg.append(
            f"<text x='{x0 - 10}' y='{y + 4}' font-size='12' text-anchor='end' fill='#333'>{v:.0f}</text>"
        )

    # Points
    for idx, row in plot_df.iterrows():
        cx = x_to_svg(row["gdp_log"])
        cy = y_to_svg(row["health_expenditure_pc"])
        radius = r.loc[idx]
        title = xml_escape(row["country"])
        svg.append(
            f"<circle cx='{cx}' cy='{cy}' r='{radius:.2f}' fill='#2a6f97' fill-opacity='0.7' stroke='white' stroke-width='0.6'>"
        )
        svg.append(f"<title>{title}</title></circle>")

    # Titles
    svg.append(
        f"<text x='{width/2}' y='{32}' font-size='18' text-anchor='middle' fill='#111'>GDP per Capita vs Health Expenditure per Capita ({latest_year})</text>"
    )
    svg.append(
        f"<text x='{width/2}' y='{height - 24}' font-size='14' text-anchor='middle' fill='#333'>GDP per Capita (current US$, log scale)</text>"
    )
    svg.append(
        f"<text x='22' y='{height/2}' font-size='14' text-anchor='middle' fill='#333' transform='rotate(-90 22 {height/2})'>Health Expenditure per Capita (current US$)</text>"
    )

    svg.append("</svg>")

    out_path.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
