import geopandas as gpd

def filter_shapefile(input_shapefile, output_shapefile):
    # Step 1: Read the shapefile
    gdf = gpd.read_file(input_shapefile)
    
    # Step 2: Filter the rows where the 'DN' column values are 1, 2, 3, or 4
    valid_values = [1, 2, 3, 4]
    filtered_gdf = gdf[gdf['predicted'].isin(valid_values)]
    
    # Step 3: Write the filtered GeoDataFrame to a new shapefile
    filtered_gdf.to_file(output_shapefile)

    print(f"Filtered shapefile saved as: {output_shapefile}")
