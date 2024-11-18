import os
import geopandas as gpd
import pandas as pd

# Function to merge all .shp files in a directory
def merge_shapefiles(input_folder, output_file):
    # List all .shp files in the input folder
    shp_files = [f for f in os.listdir(input_folder) if f.endswith('.shp')]
    
    # Initialize an empty list to store GeoDataFrames
    gdfs = []
    
    # Iterate through all shapefiles and append them to the list
    for shp_file in shp_files:
        shp_path = os.path.join(input_folder, shp_file)
        print(f"Reading {shp_path}")
        
        # Read the current shapefile
        gdf = gpd.read_file(shp_path)
        
        # Append GeoDataFrame to the list
        gdfs.append(gdf)
    
    # Use pandas.concat() to combine all GeoDataFrames into one
    if gdfs:
        print("Merging shapefiles...")
        merged_gdf = pd.concat(gdfs, ignore_index=True)
        
        # Save the merged shapefile
        print(f"Merging complete, saving to {output_file}")
        merged_gdf.to_file(output_file)
    else:
        print("No shapefiles found to merge.")


