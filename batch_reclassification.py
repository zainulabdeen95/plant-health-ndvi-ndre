import os
import rasterio
import numpy as np
from math import ceil
# Defining the reclassification function
import numpy as np
import rasterio
from osgeo import gdal

# def reclassify_raster(input_path, output_path, report, threshold=0.2):
#     with rasterio.open(input_path) as src:
#         arr = src.read(1)
        
#         # Masking out zero values (interpreted as null)
#         arr = np.where(arr == 0, np.nan, arr)
        
#         # Apply the threshold: Anything lower than the threshold will have class 1
#         arr = np.where(arr < threshold, 1, arr)
        
#         # Calculating mean and standard deviation, ignoring NaN values
#         mean = np.nanmean(arr)
#         std_dev = np.nanstd(arr)
        
#         # Calculating thresholds
#         sd_half = std_dev / 2
#         val1 = mean - sd_half
#         val2 = mean
#         val3 = mean + sd_half

#         if report == "ndvi":

#             # Reclassifying based on thresholds for NDVI & GCI
#             arr = np.where(arr <= val1, 1, arr)
#             arr = np.where((arr > val1) & (arr <= val2), 2, arr)
#             arr = np.where((arr > val2) & (arr <= val3), 3, arr)
#             arr = np.where((arr > val3) & (arr < 1), 4, arr)

#         elif report == "ndre":
#             # Reclassifying based on thresholds for NDRE
#             arr = np.where(arr <= val1, 1, arr)
#             arr = np.where((arr > val1) & (arr <= val2), 2, arr)
#             arr = np.where((arr > val2) & (arr < 1), 3, arr)
        
#         # Set NaN values back to 0 if desired
#         arr = np.where(np.isnan(arr), 0, arr)

#         # Update metadata
#         out_meta = src.meta.copy()
#         out_meta.update(dtype=rasterio.int32)

#         # Write reclassified raster to output file
#         with rasterio.open(output_path, "w", **out_meta) as dest:
#             dest.write(arr.astype(rasterio.int32), 1)
#     print(f"Reclassified raster saved at: {output_path}")

import numpy as np
from osgeo import gdal

def re_classify(input_path, output_path, key):
    '''
    Function to reclassify indices 
    '''
    methodology = 'standard'
    threshold = 0.125
    gs = gdal.Open(input_path)
    geotrans = gs.GetGeoTransform()
    band = gs.GetRasterBand(1)
    arr = band.ReadAsArray()

    no_data_value = band.GetNoDataValue()
    if no_data_value is None:  # If noData value is not set, assume 0
        no_data_value = 0 

    # Mask the noData values
    arr = np.ma.masked_equal(arr, no_data_value)

    arr[arr <= -1] = np.nan  # Additional masking based on your previous logic

    # Different function for quantile and sd dev 
    if methodology == 'quantile':
        pass
    else:
        reclassify_functions = {
            "ndvi": reclassify_non_ndre,
            "ndmi": reclassify_non_ndre,
            "ndre": reclassify_ndre,
            "gci": reclassify_non_ndre
        }

    try:
        re_arr, values_dict, mean_val = reclassify_functions[key](arr, float(threshold), no_data_value)
        export_raster(output_path, re_arr, gs, no_data_value)  # Ensure we write the noData values back correctly
        return values_dict, mean_val
    except Exception as e:
        print(f'Couldnt reclassify because of exception {e}')
        return None, None


def reclassify_non_ndre(arr, threshold, no_data_value):
    # Ensure that the noData value is preserved
    arr = np.ma.masked_equal(arr, no_data_value)

    flat_arr = arr.flatten()
    elements = np.array(flat_arr)
    elements = elements[~np.isnan(elements)]  # Remove NaNs
    unique_elements = np.unique(elements)
    filtered_array = unique_elements[unique_elements > threshold]

    if len(filtered_array) > 2:
        mean = np.mean(filtered_array, axis=0)
        sd = np.std(filtered_array, axis=0)
        sd_half = sd / 2
        val1 = mean - sd
        val2 = mean - sd_half
        val3 = mean + sd_half

        # Reclassify only the non-masked (valid) pixels
        conditions = [
            (arr <= val1),
            (arr > val1) & (arr <= val2),
            (arr > val2) & (arr <= val3),
            (arr > val3) & (arr < 100)
        ]
        choices = [100, 200, 300, 400]

        # Perform reclassification, maintaining the noData values
        arr = np.select(conditions, choices, default=arr)  # Default leaves noData values untouched

        conditions = [arr == 100, arr == 200, arr == 300, arr == 400]
        choices = [1, 2, 3, 4]
        arr = np.select(conditions, choices, default=arr)  # Default leaves noData values untouched

        minimum = np.min(elements)
        maximum = np.max(elements)
        values_dict = {
            '1': f"{rounding(minimum, 2)} - {rounding(val1, 2)}",
            '2': f"{rounding(val1, 2)} - {rounding(val2, 2)}",
            '3': f"{rounding(val2, 2)} - {rounding(val3, 2)}",
            '4': f"{rounding(val3, 2)} - {rounding(maximum, 2)}"
        }
    else:
        # If there are too few elements above threshold, assign the lowest category
        arr = np.where(arr.mask, arr, 1)  # Only assign 1 to valid pixels
        minimum = np.min(elements)
        maximum = np.max(elements)
        values_dict = {'1': f"{minimum} - {maximum}"}

    mean = rounding(np.mean(elements), 2)

    return arr, values_dict, mean


def reclassify_ndre(arr, threshold, no_data_value):
    # Ensure that the noData value is preserved
    arr = np.ma.masked_equal(arr, no_data_value)

    flat_arr = arr.flatten()
    elements = np.array(flat_arr)
    elements = elements[~np.isnan(elements)]  # Remove NaNs

    unique_elements = np.unique(elements)
    filtered_array = unique_elements[unique_elements > threshold]

    if len(filtered_array) > 2:
        mean = np.mean(filtered_array, axis=0)
        sd = np.std(filtered_array, axis=0)
        sd_half = sd / 2
        val1 = mean - sd_half
        val2 = mean

        # Reclassify only the non-masked (valid) pixels
        arr = np.select(
            [
                arr <= val1,
                (arr > val1) & (arr <= val2),
                (arr > val2) & (arr < 1),
            ], [1, 2, 3], default=arr
        )

        minimum = np.min(elements)
        maximum = np.max(elements)
        values_dict = {
            '1': f"{rounding(minimum, 2)} - {rounding(val1, 2)}",
            '2': f"{rounding(val1, 2)} - {rounding(val2, 2)}",
            '3': f"{rounding(val2, 2)} - {rounding(maximum, 2)}"
        }

    else:
        # If there are too few elements above threshold, assign the lowest category
        arr = np.where(arr.mask, arr, 1)  # Only assign 1 to valid pixels
        minimum = np.min(elements)
        maximum = np.max(elements)
        values_dict = {'1': f"{minimum} - {maximum}"}

    # For attributes mean and range 
    mean = rounding(np.mean(elements), 2)

    return arr, values_dict, mean


def export_raster(output_path, arr, gs, no_data_value):
    # Create output raster from the reclassified array
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_path, gs.RasterXSize, gs.RasterYSize, 1, gdal.GDT_Float32)
    out_ds.SetGeoTransform(gs.GetGeoTransform())
    out_ds.SetProjection(gs.GetProjection())
    out_band = out_ds.GetRasterBand(1)

    # Write the reclassified array to the raster, setting noData values
    out_band.WriteArray(arr)
    out_band.SetNoDataValue(no_data_value)  # Ensure noData value is set
    out_band.FlushCache()

    # Close dataset
    out_ds = None




def rounding(numb, deci):
    '''
    Function to round off values (float)
    '''

    result = ceil(numb * 10 ** deci)/(10 ** deci)
    
    return result

# def export_raster(output_path, reclassified_array, raster_dataset):
#     '''
#     Exports raster to a file
#     Args
#     ---------
    
#     output path: the path to save the raster to
#     reclassified_array: the flattened array of the raster
#     raster_dataset: the dataset itself
    
#     '''
    
#     raster_columns = raster_dataset.RasterXSize
#     raster_rows = raster_dataset.RasterYSize
#     geo_transform = raster_dataset.GetGeoTransform()
#     projection = raster_dataset.GetProjection()
#     raster_driver = raster_dataset.GetDriver()

#     outDs = raster_driver.Create(output_path, raster_columns, raster_rows, 1, gdal.GDT_Float32)
#     outBand = outDs.GetRasterBand(1)
#     outBand.SetNoDataValue(15)  #TODO:CHANGE THIS
#     outBand.WriteArray(reclassified_array)
#     outDs.SetGeoTransform(geo_transform)
#     outDs.SetProjection(projection)
