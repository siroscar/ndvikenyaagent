import ee
ee.Initialize()

counties = ee.FeatureCollection("FAO/GAUL/2015/level2") \
    .filter(ee.Filter.eq("ADM0_NAME", "Kenya"))

names = counties.aggregate_array("ADM2_NAME").getInfo()
print(sorted(set(names)))
print(f"Total: {len(set(names))}")
