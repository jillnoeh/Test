"""Demo fixtures used when live scraping is blocked or returns nothing.

Three named fixtures cover different risk profiles so demos stay interesting.
DEFAULT_RETAILER is what the scraper returns on a generic fallback.
"""
from __future__ import annotations

from typing import Dict, List


def _fixture(
    sizes_offered: Dict[str, int],
    stock_by_size: Dict[str, Dict[str, int]],
    clearance_items: List[Dict[str, str]],
    stores: List[Dict[str, str]],
) -> Dict:
    return {
        "sizes_offered": sizes_offered,
        "stock_by_size": stock_by_size,
        "clearance_items": clearance_items,
        "stores": stores,
        "is_demo": True,
    }


# Mid-market specialty apparel chain — heavy mall + Sun Belt footprint, broad
# size run, classic plus-size emphasis. Designed to score "High".
DEFAULT_RETAILER = _fixture(
    sizes_offered={"XS": 18, "S": 42, "M": 58, "L": 67, "XL": 71,
                   "1X": 44, "2X": 39, "3X+": 22},
    stock_by_size={
        "XS": {"in_stock": 6,  "low_stock": 4, "out_of_stock": 8},
        "S":  {"in_stock": 18, "low_stock": 9, "out_of_stock": 15},
        "M":  {"in_stock": 32, "low_stock": 11, "out_of_stock": 15},
        "L":  {"in_stock": 51, "low_stock": 9, "out_of_stock": 7},
        "XL": {"in_stock": 60, "low_stock": 7, "out_of_stock": 4},
        "1X": {"in_stock": 38, "low_stock": 4, "out_of_stock": 2},
        "2X": {"in_stock": 33, "low_stock": 4, "out_of_stock": 2},
        "3X+": {"in_stock": 18, "low_stock": 3, "out_of_stock": 1},
    },
    clearance_items=(
        [{"sku": f"CL-{i:04d}", "size": "XL"}  for i in range(28)] +
        [{"sku": f"CL-{i:04d}", "size": "1X"}  for i in range(28, 52)] +
        [{"sku": f"CL-{i:04d}", "size": "2X"}  for i in range(52, 76)] +
        [{"sku": f"CL-{i:04d}", "size": "3X+"} for i in range(76, 92)] +
        [{"sku": f"CL-{i:04d}", "size": "L"}   for i in range(92, 108)] +
        [{"sku": f"CL-{i:04d}", "size": "M"}   for i in range(108, 116)] +
        [{"sku": f"CL-{i:04d}", "size": "S"}   for i in range(116, 120)]
    ),
    stores=[
        # Stores concentrated in high-adoption Sun Belt + FL/TX metros.
        {"name": "Tampa Galleria",       "city": "Tampa",          "state": "FL", "zip": "33602"},
        {"name": "Orlando Millenia",     "city": "Orlando",        "state": "FL", "zip": "32839"},
        {"name": "Miami Aventura",       "city": "Miami",          "state": "FL", "zip": "33180"},
        {"name": "West Palm Gardens",    "city": "West Palm Beach","state": "FL", "zip": "33410"},
        {"name": "Jacksonville Town",    "city": "Jacksonville",   "state": "FL", "zip": "32256"},
        {"name": "Atlanta Lenox",        "city": "Atlanta",        "state": "GA", "zip": "30326"},
        {"name": "Atlanta Perimeter",    "city": "Atlanta",        "state": "GA", "zip": "30346"},
        {"name": "Charlotte SouthPark",  "city": "Charlotte",      "state": "NC", "zip": "28211"},
        {"name": "Raleigh Crabtree",     "city": "Raleigh-Durham", "state": "NC", "zip": "27612"},
        {"name": "Nashville Green Hills","city": "Nashville",      "state": "TN", "zip": "37215"},
        {"name": "Memphis Wolfchase",    "city": "Memphis",        "state": "TN", "zip": "38133"},
        {"name": "Birmingham Galleria",  "city": "Birmingham AL",  "state": "AL", "zip": "35244"},
        {"name": "New Orleans Lakeside", "city": "New Orleans",    "state": "LA", "zip": "70002"},
        {"name": "Houston Galleria",     "city": "Houston",        "state": "TX", "zip": "77056"},
        {"name": "Houston Memorial",     "city": "Houston",        "state": "TX", "zip": "77024"},
        {"name": "Dallas NorthPark",     "city": "Dallas-Ft. Worth","state":"TX", "zip": "75225"},
        {"name": "Dallas Galleria",      "city": "Dallas-Ft. Worth","state":"TX", "zip": "75240"},
        {"name": "Austin Domain",        "city": "Austin",         "state": "TX", "zip": "78758"},
        {"name": "San Antonio La Cantera","city":"San Antonio",    "state": "TX", "zip": "78256"},
        {"name": "Phoenix Scottsdale",   "city": "Phoenix",        "state": "AZ", "zip": "85251"},
        {"name": "Phoenix Biltmore",     "city": "Phoenix",        "state": "AZ", "zip": "85016"},
        {"name": "Las Vegas Fashion",    "city": "Las Vegas",      "state": "NV", "zip": "89109"},
        {"name": "Denver Cherry Creek",  "city": "Denver",         "state": "CO", "zip": "80206"},
        {"name": "Kansas City Plaza",    "city": "Kansas City",    "state": "MO", "zip": "64112"},
        {"name": "St. Louis Galleria",   "city": "St. Louis",      "state": "MO", "zip": "63117"},
        {"name": "Indianapolis Fashion", "city": "Indianapolis",   "state": "IN", "zip": "46240"},
        {"name": "Columbus Easton",      "city": "Columbus OH",    "state": "OH", "zip": "43219"},
        {"name": "Cincinnati Kenwood",   "city": "Cincinnati",     "state": "OH", "zip": "45236"},
        {"name": "Pittsburgh Ross Park", "city": "Pittsburgh",     "state": "PA", "zip": "15237"},
        {"name": "Philadelphia King Prussia","city":"Philadelphia","state":"PA", "zip": "19406"},
        {"name": "Washington Tysons",    "city": "Washington DC",  "state": "VA", "zip": "22102"},
        {"name": "Richmond Short Pump",  "city": "Richmond",       "state": "VA", "zip": "23233"},
        {"name": "Baltimore Towson",     "city": "Baltimore",      "state": "MD", "zip": "21204"},
        {"name": "Boston Natick",        "city": "Boston",         "state": "MA", "zip": "01760"},
        {"name": "NYC Roosevelt Field",  "city": "New York",       "state": "NY", "zip": "11530"},
        {"name": "NYC Westchester",      "city": "New York",       "state": "NY", "zip": "10605"},
        {"name": "Chicago Oakbrook",     "city": "Chicago",        "state": "IL", "zip": "60523"},
        {"name": "Chicago Old Orchard",  "city": "Chicago",        "state": "IL", "zip": "60077"},
        {"name": "Detroit Somerset",     "city": "Detroit",        "state": "MI", "zip": "48084"},
        {"name": "Minneapolis Mall of America","city":"Minneapolis","state":"MN","zip": "55425"},
    ],
)


# Coastal premium denim brand — narrow size run, urban affluent footprint,
# small clearance, smaller-size stockouts. Designed to score "Critical".
COASTAL_PREMIUM = _fixture(
    sizes_offered={"XS": 22, "S": 38, "M": 41, "L": 26, "XL": 11,
                   "1X": 0, "2X": 0, "3X+": 0},
    stock_by_size={
        "XS": {"in_stock": 4,  "low_stock": 6, "out_of_stock": 12},
        "S":  {"in_stock": 11, "low_stock": 9, "out_of_stock": 18},
        "M":  {"in_stock": 22, "low_stock": 7, "out_of_stock": 12},
        "L":  {"in_stock": 21, "low_stock": 3, "out_of_stock": 2},
        "XL": {"in_stock": 10, "low_stock": 1, "out_of_stock": 0},
        "1X": {"in_stock": 0,  "low_stock": 0, "out_of_stock": 0},
        "2X": {"in_stock": 0,  "low_stock": 0, "out_of_stock": 0},
        "3X+": {"in_stock": 0, "low_stock": 0, "out_of_stock": 0},
    },
    clearance_items=(
        [{"sku": f"PR-{i:04d}", "size": "XL"} for i in range(8)] +
        [{"sku": f"PR-{i:04d}", "size": "L"}  for i in range(8, 14)] +
        [{"sku": f"PR-{i:04d}", "size": "M"}  for i in range(14, 18)]
    ),
    stores=[
        {"name": "SoHo",        "city": "New York",       "state": "NY", "zip": "10012"},
        {"name": "Madison Ave", "city": "New York",       "state": "NY", "zip": "10075"},
        {"name": "Brooklyn",    "city": "New York",       "state": "NY", "zip": "11201"},
        {"name": "Boston Newbury","city":"Boston",        "state": "MA", "zip": "02116"},
        {"name": "DC Georgetown","city": "Washington DC", "state": "DC", "zip": "20007"},
        {"name": "SF Union Sq", "city": "San Francisco",  "state": "CA", "zip": "94108"},
        {"name": "SF Hayes",    "city": "San Francisco",  "state": "CA", "zip": "94102"},
        {"name": "LA Melrose",  "city": "Los Angeles",    "state": "CA", "zip": "90046"},
        {"name": "LA Abbot Kinney","city":"Los Angeles",  "state": "CA", "zip": "90291"},
        {"name": "Miami Design District","city":"Miami",  "state": "FL", "zip": "33137"},
        {"name": "Chicago Bucktown","city":"Chicago",     "state": "IL", "zip": "60622"},
        {"name": "Seattle Capitol Hill","city":"Seattle", "state": "WA", "zip": "98122"},
    ],
)


# Mass-market basics retailer — broad size run, balanced clearance, modest
# adoption metros. Designed to score "Moderate".
MASS_BASICS = _fixture(
    sizes_offered={"XS": 60, "S": 120, "M": 145, "L": 150, "XL": 140,
                   "1X": 95, "2X": 75, "3X+": 50},
    stock_by_size={
        "XS": {"in_stock": 45, "low_stock": 8, "out_of_stock": 7},
        "S":  {"in_stock": 95, "low_stock": 14,"out_of_stock": 11},
        "M":  {"in_stock": 120,"low_stock": 15,"out_of_stock": 10},
        "L":  {"in_stock": 130,"low_stock": 12,"out_of_stock": 8},
        "XL": {"in_stock": 122,"low_stock": 11,"out_of_stock": 7},
        "1X": {"in_stock": 80, "low_stock": 9, "out_of_stock": 6},
        "2X": {"in_stock": 64, "low_stock": 7, "out_of_stock": 4},
        "3X+": {"in_stock": 42,"low_stock": 5, "out_of_stock": 3},
    },
    clearance_items=(
        [{"sku": f"MB-{i:04d}", "size": "XS"}  for i in range(15)] +
        [{"sku": f"MB-{i:04d}", "size": "S"}   for i in range(15, 35)] +
        [{"sku": f"MB-{i:04d}", "size": "M"}   for i in range(35, 60)] +
        [{"sku": f"MB-{i:04d}", "size": "L"}   for i in range(60, 85)] +
        [{"sku": f"MB-{i:04d}", "size": "XL"}  for i in range(85, 110)] +
        [{"sku": f"MB-{i:04d}", "size": "1X"}  for i in range(110, 130)] +
        [{"sku": f"MB-{i:04d}", "size": "2X"}  for i in range(130, 145)] +
        [{"sku": f"MB-{i:04d}", "size": "3X+"} for i in range(145, 155)]
    ),
    stores=[
        {"name": "Spokane Valley", "city": "Spokane",      "state": "WA", "zip": "99206"},
        {"name": "Boise Towne",    "city": "Boise",        "state": "ID", "zip": "83704"},
        {"name": "Salt Lake City Cottonwood","city":"Salt Lake City","state":"UT","zip":"84121"},
        {"name": "Des Moines Jordan","city":"Des Moines",  "state": "IA", "zip": "50266"},
        {"name": "Omaha Westroads","city":"Omaha",         "state": "NE", "zip": "68114"},
        {"name": "Wichita Towne East","city":"Wichita",    "state": "KS", "zip": "67207"},
        {"name": "Tulsa Woodland","city":"Tulsa",          "state": "OK", "zip": "74133"},
        {"name": "Little Rock Park", "city":"Little Rock", "state": "AR", "zip": "72211"},
        {"name": "Knoxville West","city":"Knoxville",      "state": "TN", "zip": "37919"},
        {"name": "Lexington Fayette","city":"Lexington",   "state": "KY", "zip": "40503"},
        {"name": "Madison East","city":"Madison",          "state": "WI", "zip": "53704"},
        {"name": "Green Bay Bay Park","city":"Green Bay",  "state": "WI", "zip": "54303"},
        {"name": "Grand Rapids Woodland","city":"Grand Rapids","state":"MI","zip":"49546"},
        {"name": "Toledo Franklin","city":"Toledo",        "state": "OH", "zip": "43623"},
        {"name": "Dayton Fairfield","city":"Dayton",       "state": "OH", "zip": "45459"},
        {"name": "Erie Millcreek","city":"Erie PA",        "state": "PA", "zip": "16509"},
        {"name": "Rochester Marketplace","city":"Rochester NY","state":"NY","zip":"14623"},
        {"name": "Syracuse Destiny","city":"Syracuse",     "state": "NY", "zip": "13204"},
        {"name": "Buffalo Walden","city":"Buffalo",        "state": "NY", "zip": "14225"},
    ],
)


FIXTURES = {
    "default": DEFAULT_RETAILER,
    "coastal_premium": COASTAL_PREMIUM,
    "mass_basics": MASS_BASICS,
}
