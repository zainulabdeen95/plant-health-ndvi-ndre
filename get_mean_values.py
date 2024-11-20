import os
import rasterio
import numpy as np
import geopandas as gpd

def get_mean_values_from_tifs(folder_path):
    mean_values = {}

    # Loop through each file in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".tif"):
            # Extract the number from the file name
            try:
                # Assuming the filename format is like "ndre_output_clip_0.tif"
                key = int(file_name.split('_')[-1].split('.')[0])
                
                # Open the .tif file and read the data
                with rasterio.open(os.path.join(folder_path, file_name)) as src:
                    # Read the data into a numpy array
                    data = src.read(1)  # Read the first band
                    mean_value = np.mean(data)  # Calculate mean value
                    mean_values[key] = round(float(mean_value), 2)  # Convert to Python float, round to 2 decimals
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
    
    return mean_values

def add_mean_column(shapefile_path, mean_dict):
    # Load the shapefile into a GeoDataFrame
    gdf = gpd.read_file(shapefile_path)
    
    # Ensure the 'predicted' column exists in the GeoDataFrame
    if 'predicted' not in gdf.columns:
        raise ValueError("The shapefile must contain a 'predicted' column.")
    
    # Add the 'mean' column based on the 'predicted' column using the provided dictionary
    gdf['mean'] = gdf['predicted'].map(mean_dict)
    
    # Check if there are any unmatched values (NaN values for 'mean')
    if gdf['mean'].isna().any():
        print("Warning: Some values in 'predicted' do not have a corresponding entry in the dictionary.")
    
    # Return the updated GeoDataFrame
    return gdf

# Example usage
