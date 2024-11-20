import os
import geopandas as gpd

def merge_shapefiles(input_folder, output_folder, output_filename):
    # Check if the input folder exists
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"The folder {input_folder} does not exist.")
    
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all shapefile paths in the input folder
    shapefiles = [f for f in os.listdir(input_folder) if f.endswith('.shp')]
    
    # Check if there are any shapefiles in the folder
    if not shapefiles:
        raise ValueError(f"No shapefiles found in the folder {input_folder}.")
    
    # Read the first shapefile into a GeoDataFrame
    gdf_merged = gpd.read_file(os.path.join(input_folder, shapefiles[0]))
    
    # Iterate through the rest of the shapefiles and append them to the merged GeoDataFrame
    for shapefile in shapefiles[1:]:
        gdf_temp = gpd.read_file(os.path.join(input_folder, shapefile))
        gdf_merged = gdf_merged.append(gdf_temp, ignore_index=True)
    
    # Define the output shapefile path
    output_path = os.path.join(output_folder, output_filename)
    
    # Save the merged GeoDataFrame to a new shapefile
    gdf_merged.to_file(output_path)
    
    print(f"Merged shapefiles saved to {output_path}")

# Example usage:
# merge_shapefiles('/path/to/input/folder', '/path/to/output/folder', 'merged_shapefile.shp')
