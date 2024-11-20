import os
import glob
import numpy as np
import rasterio
from rasterio.merge import merge

def mosaic_rasters(input_folder, output_tif, output_dtype='float64'):
    """
    Takes input folder containing TIFF files, mosaics them, and saves as a single output TIFF file.
    
    Args:
        input_folder (str): Path to the folder containing the input TIFF files.
        output_tif (str): Path to save the mosaicked output TIFF file.
        output_dtype (str): Desired output data type, e.g., 'float64', 'int16', etc.
    """
    # Get list of all TIFF files in the input folder
    tif_files = glob.glob(os.path.join(input_folder, '*.tif'))
    
    if not tif_files:
        raise ValueError(f"No TIFF files found in the folder: {input_folder}")
    
    # List to hold the opened raster datasets
    datasets = []
    
    # Open each TIFF file and append to the list
    for tif_file in tif_files:
        dataset = rasterio.open(tif_file)
        datasets.append(dataset)
    
    # Merge all the datasets
    mosaic, out_transform = merge(datasets)
    
    # Convert the mosaic to the desired data type (float64 in this case)
    mosaic = mosaic.astype(output_dtype)
    
    # Get metadata of the first file (assuming all files have the same metadata)
    out_meta = datasets[0].meta.copy()
    
    # Set a consistent NoData value (e.g., None or a specific value)
    nodata_value = datasets[0].nodata if datasets[0].nodata is not None else -9999
    
    # Update metadata to reflect the new size, transform, NoData value, and data type
    out_meta.update({
        'driver': 'GTiff',
        'count': 1,  # Single-band (if multi-band, use the count from the datasets)
        'crs': datasets[0].crs,
        'transform': out_transform,
        'width': mosaic.shape[2],
        'height': mosaic.shape[1],
        'nodata': nodata_value,  # Set NoData value
        'dtype': output_dtype  # Update the data type to float64
    })
    
    # Save the mosaicked raster to output file
    with rasterio.open(output_tif, 'w', **out_meta) as out_raster:
        out_raster.write(mosaic[0], 1)  # Write first band of the mosaicked raster

    print(f"Mosaic saved as {output_tif}")

# Example usage:
# input_folder = "path/to/your/tif/folder"
# output_tif = "path/to/save/mosaicked_output.tif"
# mosaic_rasters(input_folder, output_tif)
