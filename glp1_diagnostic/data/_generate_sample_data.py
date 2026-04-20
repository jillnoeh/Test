"""One-shot generator for sample GLP-1 data CSVs.

Run from the data/ directory:  python _generate_sample_data.py

Produces realistic dummy data so the app runs out-of-the-box. Re-running is
deterministic (fixed seed). Replace these CSVs with proprietary data when
available; the schemas are stable.
"""
from __future__ import annotations

import csv
import math
import random
from pathlib import Path

SEED = 7
random.seed(SEED)

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Anchor metros: (DMA name, DMA code, state, lat, lon, base_adoption)
# Adoption is a hand-tuned base rate (share of adults on GLP-1) per metro,
# loosely informed by published payer/pharmacy data: higher in the Sun Belt
# and affluent coastal metros, lower in rural/lower-income markets.
# ---------------------------------------------------------------------------
METROS = [
    ("New York",           501, "NY", 40.7128,  -74.0060, 0.082),
    ("Los Angeles",        803, "CA", 34.0522, -118.2437, 0.071),
    ("Chicago",            602, "IL", 41.8781,  -87.6298, 0.068),
    ("Philadelphia",       504, "PA", 39.9526,  -75.1652, 0.074),
    ("Dallas-Ft. Worth",   623, "TX", 32.7767,  -96.7970, 0.091),
    ("San Francisco",      807, "CA", 37.7749, -122.4194, 0.078),
    ("Boston",             506, "MA", 42.3601,  -71.0589, 0.069),
    ("Atlanta",            524, "GA", 33.7490,  -84.3880, 0.094),
    ("Houston",            618, "TX", 29.7604,  -95.3698, 0.088),
    ("Washington DC",      511, "DC", 38.9072,  -77.0369, 0.083),
    ("Phoenix",            753, "AZ", 33.4484, -112.0740, 0.089),
    ("Tampa",              539, "FL", 27.9506,  -82.4572, 0.097),
    ("Seattle",            819, "WA", 47.6062, -122.3321, 0.064),
    ("Detroit",            505, "MI", 42.3314,  -83.0458, 0.073),
    ("Minneapolis",        613, "MN", 44.9778,  -93.2650, 0.062),
    ("Miami",              528, "FL", 25.7617,  -80.1918, 0.101),
    ("Denver",              751, "CO", 39.7392, -104.9903, 0.067),
    ("Orlando",            534, "FL", 28.5383,  -81.3792, 0.092),
    ("Cleveland",          510, "OH", 41.4993,  -81.6944, 0.072),
    ("Sacramento",         862, "CA", 38.5816, -121.4944, 0.066),
    ("St. Louis",          609, "MO", 38.6270,  -90.1994, 0.075),
    ("Portland OR",        820, "OR", 45.5152, -122.6784, 0.061),
    ("Pittsburgh",         508, "PA", 40.4406,  -79.9959, 0.069),
    ("Charlotte",          517, "NC", 35.2271,  -80.8431, 0.086),
    ("Raleigh-Durham",     560, "NC", 35.7796,  -78.6382, 0.081),
    ("Indianapolis",       527, "IN", 39.7684,  -86.1581, 0.078),
    ("Baltimore",          512, "MD", 39.2904,  -76.6122, 0.077),
    ("San Diego",          825, "CA", 32.7157, -117.1611, 0.069),
    ("Nashville",          659, "TN", 36.1627,  -86.7816, 0.084),
    ("Hartford",           533, "CT", 41.7658,  -72.6734, 0.071),
    ("Kansas City",        616, "MO", 39.0997,  -94.5786, 0.074),
    ("Columbus OH",        535, "OH", 39.9612,  -82.9988, 0.076),
    ("Salt Lake City",     770, "UT", 40.7608, -111.8910, 0.058),
    ("Cincinnati",         515, "OH", 39.1031,  -84.5120, 0.073),
    ("Milwaukee",          617, "WI", 43.0389,  -87.9065, 0.066),
    ("San Antonio",        641, "TX", 29.4241,  -98.4936, 0.083),
    ("West Palm Beach",    548, "FL", 26.7153,  -80.0534, 0.099),
    ("Las Vegas",          839, "NV", 36.1699, -115.1398, 0.087),
    ("Austin",             635, "TX", 30.2672,  -97.7431, 0.079),
    ("Jacksonville",       561, "FL", 30.3322,  -81.6557, 0.090),
    ("Birmingham AL",      630, "AL", 33.5186,  -86.8104, 0.088),
    ("Memphis",            640, "TN", 35.1495,  -90.0490, 0.082),
    ("Oklahoma City",      650, "OK", 35.4676,  -97.5164, 0.080),
    ("Greenville SC",      567, "SC", 34.8526,  -82.3940, 0.083),
    ("Louisville",         529, "KY", 38.2527,  -85.7585, 0.079),
    ("New Orleans",        622, "LA", 29.9511,  -90.0715, 0.085),
    ("Buffalo",            514, "NY", 42.8864,  -78.8784, 0.067),
    ("Albuquerque",        790, "NM", 35.0844, -106.6504, 0.063),
    ("Tucson",             789, "AZ", 32.2226, -110.9747, 0.078),
    ("Richmond",           556, "VA", 37.5407,  -77.4360, 0.078),
]


def jitter(value: float, pct: float) -> float:
    return max(0.0, value * (1.0 + random.uniform(-pct, pct)))


def write_dma_csv() -> None:
    path = HERE / "glp1_adoption_by_dma.csv"
    rows = []
    for name, code, state, lat, lon, base in METROS:
        households = random.randint(180_000, 4_500_000)
        rows.append({
            "dma_code": code,
            "dma_name": name,
            "state": state,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "adoption_rate": round(jitter(base, 0.05), 4),
            "household_count": households,
        })
    # Pad with smaller mid-tier markets to reach ~210 DMAs.
    fillers = [
        ("Spokane",         881, "WA"), ("Boise",           757, "ID"),
        ("Des Moines",      679, "IA"), ("Omaha",           652, "NE"),
        ("Tulsa",           671, "OK"), ("Wichita",         678, "KS"),
        ("Little Rock",     693, "AR"), ("Madison",         669, "WI"),
        ("Knoxville",       557, "TN"), ("Lexington",       541, "KY"),
        ("Roanoke",         573, "VA"), ("Mobile",          686, "AL"),
        ("Shreveport",      612, "LA"), ("El Paso",         765, "TX"),
        ("Honolulu",        744, "HI"), ("Anchorage",       743, "AK"),
        ("Burlington VT",   523, "VT"), ("Portland ME",     500, "ME"),
        ("Charleston SC",   519, "SC"), ("Savannah",        507, "GA"),
        ("Jackson MS",      718, "MS"), ("Fargo",           724, "ND"),
        ("Sioux Falls",     725, "SD"), ("Cheyenne",        759, "WY"),
        ("Bangor",          537, "ME"), ("Lincoln NE",      722, "NE"),
        ("Springfield MO",  619, "MO"), ("Toledo",          547, "OH"),
        ("Dayton",          542, "OH"), ("Grand Rapids",    563, "MI"),
        ("Lansing",         551, "MI"), ("Green Bay",       658, "WI"),
        ("Rochester NY",    538, "NY"), ("Syracuse",        555, "NY"),
        ("Albany NY",       532, "NY"), ("Providence",      521, "RI"),
        ("Norfolk",         544, "VA"), ("Greensboro",      518, "NC"),
        ("Wilmington NC",   550, "NC"), ("Columbia SC",     546, "SC"),
        ("Augusta GA",      520, "GA"), ("Macon",           503, "GA"),
        ("Tallahassee",     530, "FL"), ("Ft. Myers",       571, "FL"),
        ("Pensacola",       686, "FL"), ("Lubbock",         651, "TX"),
        ("Amarillo",        634, "TX"), ("Corpus Christi",  600, "TX"),
        ("Reno",            811, "NV"), ("Eugene",          801, "OR"),
        ("Yakima",          810, "WA"), ("Billings",        756, "MT"),
        ("Missoula",        762, "MT"), ("Idaho Falls",     758, "ID"),
        ("Casper",           767, "WY"), ("Grand Junction", 773, "CO"),
        ("Colorado Springs", 752, "CO"), ("Topeka",         605, "KS"),
        ("Fayetteville NC", 545, "NC"), ("Chattanooga",     575, "TN"),
        ("Tri-Cities TN",   531, "TN"), ("Columbus GA",     522, "GA"),
        ("Montgomery",      698, "AL"), ("Huntsville",      691, "AL"),
        ("Lafayette LA",    642, "LA"), ("Baton Rouge",     716, "LA"),
        ("Beaumont",        692, "TX"), ("Waco",            625, "TX"),
        ("Tyler",           709, "TX"), ("McAllen",         636, "TX"),
        ("Bakersfield",     800, "CA"), ("Fresno",          866, "CA"),
        ("Monterey",        828, "CA"), ("Santa Barbara",   855, "CA"),
        ("Chico-Redding",   868, "CA"), ("Medford",         813, "OR"),
        ("Quad Cities",     682, "IA"), ("Cedar Rapids",    637, "IA"),
        ("Davenport",       682, "IA"), ("Peoria",          675, "IL"),
        ("Rockford",        610, "IL"), ("Champaign",       648, "IL"),
        ("Springfield IL",  648, "IL"), ("Evansville",      649, "IN"),
        ("Ft. Wayne",       509, "IN"), ("South Bend",      588, "IN"),
        ("Lafayette IN",    582, "IN"), ("Terre Haute",     581, "IN"),
        ("Bloomington IL",  675, "IL"),
        ("Joplin",          603, "MO"), ("Columbia MO",     604, "MO"),
        ("Springfield MA",  543, "MA"), ("Worcester",       552, "MA"),
        ("Manchester NH",   500, "NH"), ("Bangor ME",       537, "ME"),
        ("Erie PA",         516, "PA"), ("Wilkes Barre",    577, "PA"),
        ("Harrisburg",      566, "PA"), ("Johnstown",       574, "PA"),
        ("Charleston WV",   564, "WV"), ("Wheeling",        554, "WV"),
        ("Clarksburg",      598, "WV"), ("Parkersburg WV",  597, "WV"),
        ("Beckley WV",      559, "WV"),
        ("Lima OH",         558, "OH"), ("Mansfield",       569, "OH"),
        ("Zanesville",      596, "OH"), ("Steubenville",    554, "OH"),
        ("Bend OR",         821, "OR"), ("Eureka",          802, "CA"),
        ("Palm Springs",    804, "CA"), ("Yuma",            771, "AZ"),
        ("Flagstaff",       753, "AZ"), ("Twin Falls",      760, "ID"),
        ("Pocatello",       761, "ID"), ("Helena",          766, "MT"),
        ("Great Falls",     755, "MT"), ("Butte",           754, "MT"),
        ("Glendive",        798, "MT"), ("Rapid City",      764, "SD"),
        ("Mitchell SD",     687, "SD"), ("Aberdeen SD",     688, "SD"),
        ("Minot ND",        687, "ND"), ("Bismarck",        687, "ND"),
        ("Grand Forks",     724, "ND"), ("Williston",       687, "ND"),
        ("Anchorage 2",     743, "AK"), ("Fairbanks",       745, "AK"),
        ("Juneau",          747, "AK"), ("North Slope",     746, "AK"),
        ("Hilo",            744, "HI"), ("Kahului",         744, "HI"),
        ("Lihue",           744, "HI"),
    ]
    # Approximate centroid for filler markets near anchor metros.
    used_codes = {r["dma_code"] for r in rows}
    for fname, code, state in fillers:
        if code in used_codes:
            code = code + random.randint(1000, 9999)
        used_codes.add(code)
        base_rate = random.uniform(0.045, 0.075)  # smaller markets, lower mean
        rows.append({
            "dma_code": code,
            "dma_name": fname,
            "state": state,
            "lat": round(random.uniform(28.0, 47.5), 4),
            "lon": round(random.uniform(-122.0, -75.0), 4),
            "adoption_rate": round(base_rate, 4),
            "household_count": random.randint(45_000, 380_000),
        })
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.name}: {len(rows)} rows")


def write_zip_csv() -> None:
    """~3000 ZIPs scattered around anchor metros with adoption inherited
    from the metro plus a small neighborhood-level jitter."""
    path = HERE / "glp1_adoption_by_zip.csv"
    rows = []
    used_zips = set()
    for name, code, state, lat, lon, base in METROS:
        n_zips = random.randint(50, 80)
        for _ in range(n_zips):
            # Generate a plausible 5-digit ZIP unique across the file.
            for _attempt in range(5):
                z = f"{random.randint(1001, 99950):05d}"
                if z not in used_zips:
                    used_zips.add(z)
                    break
            d_lat = lat + random.uniform(-0.45, 0.45)
            d_lon = lon + random.uniform(-0.45, 0.45)
            rate = max(0.005, jitter(base, 0.30))
            rows.append({
                "zip": z,
                "city": name,
                "state": state,
                "lat": round(d_lat, 5),
                "lon": round(d_lon, 5),
                "dma_code": code,
                "adoption_rate": round(rate, 4),
                "population": random.randint(2_500, 78_000),
            })
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.name}: {len(rows)} rows")


# ---------------------------------------------------------------------------
# Consumer panel: each panelist had a "pre" size and a "post" size after
# starting GLP-1 therapy. Migration is biased downward (smaller).
# ---------------------------------------------------------------------------
SIZES = ["XS", "S", "M", "L", "XL", "1X", "2X", "3X+"]
SIZE_INDEX = {s: i for i, s in enumerate(SIZES)}

# Pre-GLP-1 distribution skews to L/XL/1X/2X (the segment most likely to
# initiate therapy).
PRE_DIST = {"XS": 0.02, "S": 0.06, "M": 0.12, "L": 0.21,
            "XL": 0.22, "1X": 0.18, "2X": 0.13, "3X+": 0.06}


def sample_pre_size() -> str:
    r = random.random()
    cum = 0.0
    for size, p in PRE_DIST.items():
        cum += p
        if r <= cum:
            return size
    return "XL"


def sample_post_size(pre: str, months: int) -> str:
    """After 6+ months on GLP-1, panelists shift down 1-3 sizes on average."""
    idx = SIZE_INDEX[pre]
    # Expected drop scales with months (capped).
    expected_drop = min(3.5, 0.45 * math.log1p(months))
    drop = max(0, int(round(random.gauss(expected_drop, 0.9))))
    new_idx = max(0, idx - drop)
    return SIZES[new_idx]


def write_panel_csv() -> None:
    path = HERE / "glp1_consumer_panel.csv"
    categories = ["womens_tops", "womens_bottoms", "womens_dresses",
                  "mens_tops", "mens_bottoms"]
    age_bands = ["25-34", "35-44", "45-54", "55-64", "65+"]
    regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
    rows = []
    for i in range(5000):
        pre = sample_pre_size()
        months = random.randint(3, 24)
        post = sample_post_size(pre, months)
        rows.append({
            "panelist_id": f"P{i:05d}",
            "age_band": random.choice(age_bands),
            "region": random.choice(regions),
            "category": random.choice(categories),
            "months_on_glp1": months,
            "pre_glp1_size": pre,
            "post_glp1_size": post,
        })
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.name}: {len(rows)} rows")


def write_demand_curve_csv() -> None:
    """Derive projected size demand share from the panel.

    Baseline = pre-GLP-1 mix across the panel (a proxy for today's demand).
    Projected = blend baseline with post-GLP-1 mix, weighted by an assumed
    GLP-1 adoption ramp (15% of the relevant apparel-buying population is on
    GLP-1 within 24 months — a midpoint of published forecasts).
    """
    path = HERE / "size_demand_curve.csv"
    panel_path = HERE / "glp1_consumer_panel.csv"
    pre_counts = {s: 0 for s in SIZES}
    post_counts = {s: 0 for s in SIZES}
    with panel_path.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            pre_counts[r["pre_glp1_size"]] += 1
            post_counts[r["post_glp1_size"]] += 1
    pre_total = sum(pre_counts.values())
    post_total = sum(post_counts.values())
    adoption_share = 0.15
    rows = []
    for s in SIZES:
        baseline = pre_counts[s] / pre_total
        post = post_counts[s] / post_total
        projected = (1 - adoption_share) * baseline + adoption_share * post
        rows.append({
            "size": s,
            "baseline_share": round(baseline, 4),
            "projected_share": round(projected, 4),
            "delta": round(projected - baseline, 4),
        })
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.name}: {len(rows)} rows")


if __name__ == "__main__":
    write_dma_csv()
    write_zip_csv()
    write_panel_csv()
    write_demand_curve_csv()
