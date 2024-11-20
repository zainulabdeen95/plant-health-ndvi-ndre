import os
import geopandas as gpd
import rasterio
import numpy as np

def calculate_mean_ndre(shapefile_folder, tiff_folder):
    # List all Shapefile and TIFF files in the given folders
    shapefile_files = sorted([f for f in os.listdir(shapefile_folder) if f.endswith('.shp')])
    tiff_files = sorted([f for f in os.listdir(tiff_folder) if f.endswith('.tif')])
    
    # Iterate over each pair of Shapefile and TIFF files
    for shapefile_file, tiff_file in zip(shapefile_files, tiff_files):
        shapefile_path = os.path.join(shapefile_folder, shapefile_file)
        tiff_path = os.path.join(tiff_folder, tiff_file)
        
        # Read the Shapefile into a GeoDataFrame
        gdf = gpd.read_file(shapefile_path)
        
        # Open the corresponding TIFF file
        with rasterio.open(tiff_path) as src:
            # Read the entire image (NDRE values)
            ndre_image = src.read(1)  # Assuming NDRE is in the first band (if single band)

            # Mask out NoData values in the NDRE image
            nodata_value = src.nodata
            if nodata_value is not None:
                ndre_image = np.ma.masked_equal(ndre_image, nodata_value)

            # Calculate the mean NDRE for the entire image
            mean_ndre = np.mean(ndre_image)

            # Round the mean to 2 decimal places
            mean_ndre_rounded = round(mean_ndre, 2)

        # Add the mean NDRE value to all features in the GeoDataFrame (column name: 'mean')
        gdf['mean'] = mean_ndre_rounded

        # Ensure the 'mean' column is rounded to 2 decimal places for all rows
        gdf['mean'] = gdf['mean'].apply(lambda x: round(x, 2))

        # Save the updated Shapefile with the new 'mean' column
        gdf.to_file(shapefile_path)  # Saves as .shp since the input is a Shapefile
        
        # Explicitly format the print statement to show two decimal places
        print(f"Processed {shapefile_file} and updated with mean NDRE value: {mean_ndre_rounded:.2f}")

# Example usage:
# calculate_mean_ndre('path/to/shapefile_folder', 'path/to/tiff_folder')
