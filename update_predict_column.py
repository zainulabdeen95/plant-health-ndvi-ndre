import geopandas as gpd

def update_shapefile_values(shapefile_path, report):
    # Read the shapefile into a GeoDataFrame
    gdf = gpd.read_file(shapefile_path)
    
    # Check if 'predict' column exists in the shapefile
    if 'predicted' not in gdf.columns:
        raise ValueError("The shapefile does not have a 'predict' column.")

    # Define the mapping based on the 'report' parameter
    if report == 'ndvi':
        value_map = {'1': '73', '2': '74', '3': '75', '4': '76'}
    elif report == 'ndre':
        value_map = {'1': '103', '2': '104', '3': '105'}
    else:
        raise ValueError("Invalid report type. Choose either 'ndvi' or 'ndre'.")
    
    # Replace the values in the 'predict' column
    gdf['predicted'] = gdf['predicted'].astype(str).replace(value_map)
    
    # Save the modified GeoDataFrame back to a shapefile
    updated_shapefile_path = shapefile_path.replace('.shp', f'_{report}.shp')
    gdf.to_file(updated_shapefile_path)
    
    print(f"Shapefile updated and saved as: {updated_shapefile_path}")

# Example usage:
# update_shapefile_values('path/to/your/shapefile.shp', 'ndvi')
