# Plant Health NDVI & NDRE Report:

from Indices import calculate_indices
import os
from clipping import clip_raster_by_polygon
from batch_reclassification import reclassify_raster
from vectorize import process_rasters_in_directory
from merge_into_final import merge_shapefiles

report = 'ndre'

# Indices:
# Example usage
input_tif = 'input/SKYWATCH_PLSD_PS_20240325T0502_ALL_Tile_0_0_0e9c.tif'
output_ndvi_tif = 'NDVI/ndvi_output.tif'  # Output NDVI TIFF file path
output_ndre_tif = 'NDRE/ndre_output.tif'  # Output NDRE TIFF file path

calculate_indices(input_tif, output_ndvi_tif, output_ndre_tif)

# Clipping:
if report == 'ndvi':
    input_raster_path = 'NDVI/ndvi_output.tif'
if report == 'ndre':
    input_raster_path = 'NDRE/ndre_output.tif'
output_folder = 'output_clipped'
clip_vector_file = 'agro_farms_updated.geojson'  
os.makedirs(output_folder, exist_ok=True)
clip_raster_by_polygon(input_raster_path, clip_vector_file, output_folder)

# Batch Reclassification:
input_folder = r'output_clipped'
output_folder = r'output_reclassified'

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith('.tif'):
        input_path = os.path.join(input_folder, filename)
        output_filename = f"{os.path.splitext(filename)[0]}_reclassified.tif"
        output_path = os.path.join(output_folder, output_filename)
        # Reclassify the raster and save it
        reclassify_raster(input_path, output_path, report)

# Polygonize:
# Usage example
input_directory = 'output_reclassified'  # Folder containing raster files
output_folder = 'final_vectors'  # Folder to save polygonized shapefiles

# Process all rasters in the directory and polygonize with predicted values
process_rasters_in_directory(input_directory, output_folder, report)

# Merge:
# Set your folder path and output file name
input_folder = 'final_vectors'  # Replace with the path to your folder
if report == 'ndre':
    output_file = 'FINAL/merged_NDRE.shp'      # Replace with the desired output file name
if report == 'ndvi':
    output_file = 'FINAL/merged_NDVI.shp' 

# Run the merge function
merge_shapefiles(input_folder, output_file)

