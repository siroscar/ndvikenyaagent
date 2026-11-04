"""Compute NDVI for a Kenyan county from Sentinel-2 Harmonized for a given year."""
import ee
import geemap
from config import OUTPUT_MAP


def initialize_gee() -> None:
    """Initialize Earth Engine — call once per session."""
    ee.Initialize()
    print("✅ Earth Engine initialized")


def get_county_geometry(county_name: str) -> ee.Feature:
    """Get a Kenyan county boundary from the FAO GAUL dataset (2015)."""
    counties = ee.FeatureCollection("FAO/GAUL/2015/level2")
    county = counties.filter(ee.Filter.eq("ADM0_NAME", "Kenya")) \
                     .filter(ee.Filter.eq("ADM2_NAME", county_name))
    if county.size().getInfo() == 0:
        raise ValueError(f"County '{county_name}' not found in GAUL dataset.")
    return ee.Feature(county.first())


def mask_s2_clouds(image: ee.Image) -> ee.Image:
    """Mask clouds and cirrus using the SCL (Scene Classification Layer) band."""
    scl = image.select("SCL")
    # Keep: vegetation(4), bare soil(5), water(6), unclassified(7),
    #       snow/ice(11), probably clear(8/9) → drop clouds 8,9,10 wait,
    # SCL classes: 0 no data, 1 saturated, 2 dark, 3 cloud shadow,
    # 4 vegetation, 5 bare, 6 water, 7 unclassified, 8 cloud med, 9 cloud hi, 10 cirrus, 11 snow
    keep = [4, 5, 6, 7, 11]
    mask = scl.eq(keep[0])
    for k in keep[1:]:
        mask = mask.Or(scl.eq(k))
    return image.updateMask(mask)


def compute_ndvi(county_name: str, year: int) -> ee.Image:
    """Return a median-composite NDVI image for a county and year."""
    geometry = get_county_geometry(county_name).geometry()
    start, end = f"{year}-01-01", f"{year+1}-01-01"

    collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                  .filterBounds(geometry)
                  .filterDate(start, end)
                  .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
                  .map(mask_s2_clouds))

    n = collection.size().getInfo()
    print(f"📡 {n} scenes after filtering for {county_name}, {year}")

    if n == 0:
        raise ValueError("No usable scenes — try another year or loosen the cloud filter.")

    return collection.median().normalizedDifference(["B8", "B4"]).clip(geometry).rename("NDVI")


def plot_ndvi(county_name: str, year: int, output_path: str = OUTPUT_MAP) -> None:
    """Render NDVI on an interactive geemap and also save a static figure."""
    ndvi = compute_ndvi(county_name, year)
    geometry = get_county_geometry(county_name).geometry()

    m = geemap.Map(center=[-0.2, 36.8], zoom=7)
    m.addLayer(ndvi, {"min": 0, "max": 1, "palette": ["red", "yellow", "green"]}, "NDVI")
    m.addLayer(ee.Image().byte().paint(featureCollection=ee.FeatureCollection(geometry), width=2), {}, f"{county_name} boundary")
    m.add_colorbar(vis_params={"min": 0, "max": 1, "palette": ["red", "yellow", "green"]}, label="NDVI")
    m.addLayerControl()
    m.centerObject(geometry, zoom=8)

    # Save static figure (works in plain Python scripts too)
    geemap.ee_export_image(ndvi, filename=output_path.replace(".png", "_raw.tif"), scale=30, region=geometry)
    m.save(f"assets/{county_name}_{year}_map.html")
    print(f"🗺️  Interactive map saved → assets/{county_name}_{year}_map.html")

if __name__ == "__main__":
    initialize_gee()
    plot_ndvi("Nairobi", 2023)