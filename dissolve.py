import geopandas as gpd
import os

def dissolve_geojson_by_predicted(input_folder, output_folder):
    """
    Loops through all GeoJSON files in a specified input folder,
    dissolves them based on the 'predicted' column, and saves the output
    in a specified output folder with the same filenames.

    Parameters:
    - input_folder (str): The path to the folder containing the original GeoJSON files.
    - output_folder (str): The path to the folder where the dissolved GeoJSON files will be saved.
    """
    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.geojson'):
            input_file_path = os.path.join(input_folder, filename)
            
            # Read the GeoJSON file using geopandas
            gdf = gpd.read_file(input_file_path)
            
            # Check if 'predicted' column exists
            if 'predicted' in gdf.columns:
                # Dissolve the GeoDataFrame based on the 'predicted' column
                dissolved_gdf = gdf.dissolve(by='predicted')
                
                # Save the dissolved GeoDataFrame to the output folder with the same filename
                output_file_path = os.path.join(output_folder, filename)
                dissolved_gdf.to_file(output_file_path, driver="GeoJSON")
                print(f"Dissolved GeoJSON saved: {output_file_path}")
            else:
                print(f"Warning: 'predicted' column not found in {filename}")
