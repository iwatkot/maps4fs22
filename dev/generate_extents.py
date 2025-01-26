""" Generate a shapefile with the extents of the regions for all providers."""

import pandas
import shapely
import geopandas

# prepare state and country files for uniform reading
states = geopandas.read_file(
    (
        "https://github.com/nvkelso/natural-earth-vector/raw/refs/heads/"
        "master/10m_cultural/ne_10m_admin_1_states_provinces.shp"
    )
)
countries = geopandas.read_file(
    (
        "https://github.com/nvkelso/natural-earth-vector/raw/refs/heads/master/"
        "50m_cultural/ne_50m_admin_0_countries.shp"
    )
)
countries.rename(columns={"NAME": "name"}, inplace=True)

combined = pandas.concat([states, countries])
print("combined", combined["geometry"].head())

# handling by name (for most of them)
names = [
    "Baden-Württemberg",
    "Bayern",
    "Canada",
    "Czechia",
    "Denmark",
    "Finland",
    "France",
    "Hessen",
    "Italy",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Norway",
    "Nordrhein-Westfalen",
    "Sachsen-Anhalt",
    "Spain",
    "Switzerland",
    "United States of America",
    "Antarctica",
]
names_set = combined[combined["name"].isin(names)]

# handling by state/province
england_set = combined[combined["geonunit"] == "England"]
union = shapely.union_all(england_set["geometry"])
england_union = geopandas.GeoDataFrame(columns=["name", "geometry"], data=[["England", union]])

scotland_set = combined[combined["geonunit"] == "Scotland"]
union = shapely.union_all(scotland_set["geometry"])
scotland_union = geopandas.GeoDataFrame(columns=["name", "geometry"], data=[["Scotland", union]])

flanders_set = combined[combined["region"] == "Flemish"]
union = shapely.union_all(flanders_set["geometry"])
flanders_union = geopandas.GeoDataFrame(columns=["name", "geometry"], data=[["Flanders", union]])

# manual bounds that don't correspond to a specific country
srtm = geopandas.GeoDataFrame({"name": ["SRTM"], "geometry": [shapely.box(-180, -90, 180, 90)]})

# Arctic is a special case
arctic_names = [
    "Canada",
    "Sweden",
    "Finland",
    "Iceland",
    "Norway",
    "Russia",
    "United States of America",
    "Greenland",
]
arctic_set = combined[combined["name"].isin(arctic_names)]
union = shapely.union_all(arctic_set["geometry"])
arctic_clipped = shapely.clip_by_rect(
    union, -180, 60.7492704708152, 179.99698443265999, 83.98823036056658
)
arctic = geopandas.GeoDataFrame(columns=["name", "geometry"], data=[["Arctic", arctic_clipped]])

# combine all
result = pandas.concat([names_set, england_union, scotland_union, flanders_union, arctic, srtm])[
    ["name", "geometry"]
]

result.to_file(
    "../maps4fs/generator/dtm/extents.shz",
    driver="ESRI Shapefile",
)
