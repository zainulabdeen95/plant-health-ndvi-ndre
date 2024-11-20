import os
from osgeo import gdal

def merge_tiff_files(input_folder, output_raster):
    # Get all .tiff files in the folder
    tiff_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.tif') or f.endswith('.tiff')]
    
    if not tiff_files:
        print("No TIFF files found in the folder.")
        return
    
    # Open the first TIFF to get the reference (projection, geotransform)
    first_tiff = gdal.Open(tiff_files[0])
    if not first_tiff:
        print("Unable to open the first TIFF file.")
        return
    
    # Prepare the options for merging (this can include resampling, no data value, etc.)
    merge_options = gdal.WarpOptions(
        format='GTiff',  # Output format
        resampleAlg=gdal.GRA_NearestNeighbour,  # Resampling method (could be changed)
        multithread=True  # Use multiple threads for faster processing
    )
    
    # Perform the merge operation
    gdal.Warp(output_raster, tiff_files, options=merge_options)

    print(f"Merge completed successfully. Output file: {output_raster}")

# Example Usage
# input_folder = "/path/to/your/tiff/folder"  # Replace with the path to your folder
# output_raster = "/path/to/output/merged_raster.tif"  # Replace with desired output file path
# merge_tiff_files(input_folder, output_raster)
