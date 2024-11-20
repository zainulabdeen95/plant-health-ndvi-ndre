import os
import geopandas as gpd
import rasterio
import numpy as np
from rasterio.mask import mask

# Function to calculate min and max for each polygon in the GeoJSON based on 'predicted' attribute
def calculate_min_max(geojson_path, tiff_path):
    # Read the GeoJSON (now it will be treated as a shapefile)
    geojson = gpd.read_file(geojson_path)

    # Open the TIFF file
    with rasterio.open(tiff_path) as src:
        # Initialize a dictionary to store min and max values for each 'predicted' value
        predicted_min_max = {}

        # Loop through each feature in the GeoJSON
        for _, feature in geojson.iterrows():
            predicted_value = feature['predicted']  # Extract the predicted value for the feature
            geometry = feature['geometry']  # Extract the geometry (polygon)
            
            # Mask the TIFF with the current polygon
            out_image, out_transform = mask(src, [geometry], crop=True)
            
            # Remove any NaN values (masked out areas)
            out_image = out_image[out_image != src.nodata]
            
            # If there are valid pixels inside the polygon, calculate min and max
            if out_image.size > 0:
                # Remove any potential 0 values if they are supposed to be NoData (this could be adjusted)
                out_image_no_zeros = out_image[out_image != 0]  # Remove zero values if zero isn't valid
                
                # If there are still valid pixels after removing zeros
                if out_image_no_zeros.size > 0:
                    feature_min = np.min(out_image_no_zeros)
                else:
                    # If only zeros remained, use the minimum from the full array (could be adjusted)
                    feature_min = np.min(out_image)
                
                feature_max = np.max(out_image)

                # Store min and max values for the specific 'predicted' value
                if predicted_value not in predicted_min_max:
                    predicted_min_max[predicted_value] = {'min': feature_min, 'max': feature_max}
                else:
                    # If already exists, compare and store the overall min/max for that predicted value
                    predicted_min_max[predicted_value]['min'] = min(predicted_min_max[predicted_value]['min'], feature_min)
                    predicted_min_max[predicted_value]['max'] = max(predicted_min_max[predicted_value]['max'], feature_max)

        # Now, for each feature in the GeoJSON, we create the 'range' column
        geojson['range'] = geojson['predicted'].map(lambda pred: 
            # Round the min and max to 2 decimal places before creating the range string
            f"{round(predicted_min_max.get(pred, {'min': np.nan})['min'], 2):.2f} - "
            f"{round(predicted_min_max.get(pred, {'max': np.nan})['max'], 2):.2f}"
        )

    return geojson

# Main function to process all the files in the given directories
def process_files_stats(geojson_folder, tiff_folder, output_folder):
    # Check if output folder exists, if not create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all the .geojson files from the geojson folder
    geojson_files = [f for f in os.listdir(geojson_folder) if f.endswith('.geojson')]
    
    # Get all the .tif files from the tif folder
    tiff_files = [f for f in os.listdir(tiff_folder) if f.endswith('.tif')]

    # Sort both lists to ensure matching order
    geojson_files.sort()
    tiff_files.sort()

    # Make sure that the number of GeoJSON files matches the number of TIFF files
    if len(geojson_files) != len(tiff_files):
        print("Warning: The number of GeoJSON files does not match the number of TIFF files.")
        return

    # Process each pair of GeoJSON and TIFF files
    for geojson_file, tiff_file in zip(geojson_files, tiff_files):
        geojson_path = os.path.join(geojson_folder, geojson_file)
        tiff_path = os.path.join(tiff_folder, tiff_file)
        
        # Calculate min and max values and update the GeoJSON with the 'range' column
        updated_geojson = calculate_min_max(geojson_path, tiff_path)
        
        # Save the updated GeoJSON as a shapefile with range values to the output folder
        output_shapefile = os.path.join(output_folder, f"updated_{os.path.splitext(geojson_file)[0]}.shp")
        updated_geojson.to_file(output_shapefile)
        print(f"Processed and saved: {output_shapefile}")

# Example usage
# geojson_folder = 'path_to_geojson_folder'
# tiff_folder = 'path_to_tiff_folder'
# output_folder = 'path_to_output_folder'  # Specify a new folder where updated shapefiles will be saved
# process_files_stats(geojson_folder, tiff_folder, output_folder)
