import os
import rasterio
import numpy as np

# Defining the reclassification function
import numpy as np
import rasterio

def reclassify_raster(input_path, output_path, report, threshold=0.2):
    with rasterio.open(input_path) as src:
        arr = src.read(1)
        
        # Masking out zero values (interpreted as null)
        arr = np.where(arr == 0, np.nan, arr)
        
        # Apply the threshold: Anything lower than the threshold will have class 1
        arr = np.where(arr < threshold, 1, arr)
        
        # Calculating mean and standard deviation, ignoring NaN values
        mean = np.nanmean(arr)
        std_dev = np.nanstd(arr)
        
        # Calculating thresholds
        sd_half = std_dev / 2
        val1 = mean - sd_half
        val2 = mean
        val3 = mean + sd_half

        if report == "ndvi":

            # Reclassifying based on thresholds for NDVI & GCI
            arr = np.where((arr > val1) & (arr <= val2), 2, arr)
            arr = np.where((arr > val2) & (arr <= val3), 3, arr)
            arr = np.where((arr > val3) & (arr < 1), 4, arr)

        elif report == "ndre":
            # Reclassifying based on thresholds for NDRE
            arr = np.where((arr > val1) & (arr <= val2), 2, arr)
            arr = np.where((arr > val2) & (arr < 1), 3, arr)
        
        # Set NaN values back to 0 if desired
        arr = np.where(np.isnan(arr), 0, arr)

        # Update metadata
        out_meta = src.meta.copy()
        out_meta.update(dtype=rasterio.int32)

        # Write reclassified raster to output file
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(arr.astype(rasterio.int32), 1)
    print(f"Reclassified raster saved at: {output_path}")




