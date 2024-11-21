# Plant Health NDVI & NDRE Report:

from Indices import calculate_indices
import os
from clipping import clip_raster_by_polygon
from batch_reclassification import re_classify
from merge_into_final import merge_shapefiles
# from clipping import clip_raster
# from clipping import clip_raster_by_shapefile
from mosaic import mosaic_rasters
from clipping import process_rasters
from remove_nodata_values import replace_nodata_with_zero
from merge_rasters import merge_tiff_files
from vectorize import vectorize_tif
from remove_other_values import filter_shapefile
from get_mean_values import get_mean_values_from_tifs, add_mean_column
from vectorize_individual_rasters import process_vector_folder
from dissolve import dissolve_geojson_by_predicted
from calculate_stats import process_files_stats
from add_mean_values import calculate_mean_ndre
# from merge_vectors import merge_shapefiles
from update_predict_column import update_shapefile_values


# Define the possible reports
reports = ['ndvi']

# Loop through each report type
for report in reports:
    if report == 'ndvi':
        input_raster_path = 'NDVI/ndvi_output.tif'
    elif report == 'ndre':
        input_raster_path = 'NDRE/ndre_output.tif'

    output_folder_name = f'clipped_index_{report}'
    output_folder_path = os.path.join('outputs', output_folder_name)
    aoi_name = 'kasurifarm_A_full'

    clip_vector_file = f'input/aois/processed/{aoi_name}.geojson'  
    os.makedirs(output_folder_path, exist_ok=True)
    clip_raster_by_polygon(input_raster_path, clip_vector_file, output_folder_path)

    # Batch Reclassification:
    input_folder = output_folder_path
    output_folder_name = f'reclassified_rasters_{report}'
    output_folder_path = os.path.join("outputs", output_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.endswith('.tif'):
            input_path = os.path.join(input_folder, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_reclassified.tif"
            output_path = os.path.join(output_folder_path, output_filename)
            re_classify(input_path, output_path, report)


    # Second clip:
    tiff_folder_name = f'reclassified_rasters_{report}'
    tiff_folder_path = os.path.join("outputs", tiff_folder_name)

    output_folder_name = f'{report}_second_clip'
    output_folder_path = os.path.join("outputs", output_folder_name)

    process_rasters(tiff_folder_path, clip_vector_file, output_folder_path)

    # Vectorizing individual shapefiles:
    process_vector_folder(output_folder_path, 'outputs/new_vectors')

    # Dissolve using 'predicted'
    dissolve_geojson_by_predicted('outputs/new_vectors', 'outputs/dissolved')

    # Calculating stats:
    process_files_stats('outputs/dissolved', f'outputs/clipped_index_{report}', 'outputs/range_added')

    # Add Mean:
    calculate_mean_ndre('outputs/range_added', f'outputs/clipped_index_{report}')



    # Define the folder paths
    folder_paths = ['outputs/merged', 'outputs/cleaned_final']

    # Loop through each folder path and create the folder if it doesn't exist
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder created: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")


    # Merge all shapefile:
    output_path = f"outputs/merged/{report}_{aoi_name}_cleaned.shp"
    merge_shapefiles('outputs/range_added', output_path)

    # Remove Null Values:
    input_path = output_path
    output_path = f"outputs/cleaned_final/{report}_{aoi_name}_cleaned.shp"
    filter_shapefile(input_path, output_path)

    update_shapefile_values(output_path, report)







    # Mosaicking TIFSS: TODO: SKIP THIS PART
    # input_folder_name = f'{report}_second_clip'
    # input_folder_path = os.path.join("outputs", input_folder_name)

    # output_folder_name = f'{report}_output.tif'
    # output_folder_path = os.path.join("outputs", output_folder_name)
    # merge_tiff_files(input_folder_path, output_folder_path)

    # Vectorization:
    # dir_path = 'outputs/vectorized'
    # # Check if the directory exists, and create it if not
    # if not os.path.exists(dir_path):
    #     os.mkdir(dir_path)
    #     print(f"Directory '{dir_path}' has been created.")
    # else:
    #     print(f"Directory '{dir_path}' already exists.")

    # input_file_name = f'{report}_output.tif'
    # input_folder_path = os.path.join("outputs", input_file_name)

    # output_file_name = f'{report}_vectorized.shp'
    # output_folder_path = os.path.join("outputs/vectorized/", output_file_name)

    

    # vectorize_tif(input_folder_path, output_folder_path, values_dict)

    # # Remove values other than 1,2,3,4
    # dir_path = 'outputs/cleaned'
    # # Check if the directory exists, and create it if not
    # if not os.path.exists(dir_path):
    #     os.mkdir(dir_path)
    #     print(f"Directory '{dir_path}' has been created.")
    # else:
    #     print(f"Directory '{dir_path}' already exists.")

    # input_shapefile = output_folder_path
    # output_file_name = f'{report}_{aoi_name}_cleaned.shp'
    # output_folder_path = os.path.join("outputs/cleaned/", output_file_name)
    # filter_shapefile(input_shapefile, output_folder_path)

    # # Adding Mean values:
    # meanvalues = get_mean_values_from_tifs('outputs/clipped_index_ndre')
    # print(meanvalues)

    # add_mean_column(output_folder_path, meanvalues)
    





























































# report = 'ndre'

# Indices: TODO: Need to write this function later for NDVI & NDRE
# Example usage
# input_tif = 'input/SkyFi_2447V4GS-1_2024-11-18_0513Z_MULTISPECTRAL_MEDIUM_Punjab-Pakistan.tif'
# output_ndvi_tif = 'NDVI/ndvi_output.tif'  # Output NDVI TIFF file path
# output_ndre_tif = 'NDRE/ndre_output.tif'  # Output NDRE TIFF file path
# calculate_indices(input_tif, output_ndvi_tif, output_ndre_tif)

# Clipping:
# if report == 'ndvi':
#     input_raster_path = 'NDVI/ndvi_output.tif'
# if report == 'ndre':
#     input_raster_path = 'NDRE/ndre_output.tif'
# output_folder = 'output_clipped'
# clip_vector_file = 'dr_sarwar_32643.geojson'  
# os.makedirs(output_folder, exist_ok=True)
# clip_raster_by_polygon(input_raster_path, clip_vector_file, output_folder)

# # Batch Reclassification:
# input_folder = r'output_clipped'
# output_folder = r'output_reclassified'

# os.makedirs(output_folder, exist_ok=True)

# for filename in os.listdir(input_folder):
#     if filename.endswith('.tif'):
#         input_path = os.path.join(input_folder, filename)

#         output_filename = f"{os.path.splitext(filename)[0]}_reclassified.tif"
#         output_path = os.path.join(output_folder, output_filename)
#         # Reclassify the raster and save it
#         re_classify(input_path, output_path, report)

# # Second clip:
# tiff_folder = r'output_reclassified'

# process_rasters(tiff_folder, clip_vector_file, f'{report}_second_clip' )

# Mosaic TIFFS:
# mosaic_rasters(f'{report}_second_clip', f'{report}_output.tif')

# Polygonize:
# # Usage example
# input_directory = 'output_reclassified'  # Folder containing raster files
# output_folder = 'final_vectors'  # Folder to save polygonized shapefiles

# # Process all rasters in the directory and polygonize with predicted values
# process_rasters_in_directory(input_directory, output_folder, report)

# # Merge:
# # Set your folder path and output file name
# input_folder = 'final_vectors'  # Replace with the path to your folder
# if report == 'ndre':
#     output_file = 'FINAL/merged_NDRE.shp'      # Replace with the desired output file name
# if report == 'ndvi':
#     output_file = 'FINAL/merged_NDVI.shp' 

# # Run the merge function
# merge_shapefiles(input_folder, output_file)

