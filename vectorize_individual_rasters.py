import os
import rasterio
import geopandas as gpd
import numpy as np
from rasterio.features import shapes
from shapely.geometry import shape

# Function to vectorize a TIFF image and save it as a GeoJSON
def vectorize_image(image_path, output_path):
    # Open the raster file using Rasterio
    with rasterio.open(image_path) as src:
        # Read the raster data and its CRS
        image_data = src.read(1)  # Read the first band (assuming single-band image)
        crs = src.crs  # Get CRS from the raster
        
        # Mask the image (remove any NoData values)
        mask = image_data != src.nodata
        
        # Use rasterio.features.shapes to extract vector shapes from the raster
        # It returns a generator of (geom, value) tuples
        results = shapes(image_data, mask=mask, transform=src.transform)
        
        # Create a list to hold the geometries and values
        geometries = []
        values = []

        # Convert each shape to a GeoJSON-compatible format
        for geom, value in results:
            geometries.append(shape(geom))  # Convert geometry to shapely object
            values.append(value)
        
        # Create a GeoDataFrame with the geometries and their associated values
        gdf = gpd.GeoDataFrame({
            'geometry': geometries,
            'predicted': values
        }, crs=crs)  # Set CRS to the raster's CRS

        # Save the GeoDataFrame as GeoJSON
        gdf.to_file(output_path, driver='GeoJSON')

    print(f"Vectorized image and saved as {output_path}")

# Function to process all TIFF files in a folder
def process_vector_folder(input_folder, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all TIFF files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.tif') or file_name.lower().endswith('.tiff'):
            image_path = os.path.join(input_folder, file_name)
            
            # Define the output GeoJSON path
            output_file = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.geojson")
            
            # Vectorize and save as GeoJSON
            vectorize_image(image_path, output_file)

# Example usage:
# input_folder = 'path/to/your/tiff/folder'
# output_folder = 'path/to/save/geojson/folder'
# process_vector_folder(input_folder, output_folder)
