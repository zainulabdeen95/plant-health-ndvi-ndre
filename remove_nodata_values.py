import rasterio
import numpy as np

def replace_nodata_with_zero(input_tiff, output_tiff):
    # Open the input TIFF file
    with rasterio.open(input_tiff) as src:
        # Read the raster data
        data = src.read(1)  # Assuming we're working with a single-band raster
        nodata_value = src.nodata  # Get the NoData value from the raster
        
        # Check if there is a NoData value
        if nodata_value is not None:
            # Replace the NoData values with 0
            data[data == nodata_value] = 0
            
        # Prepare the metadata for the output file
        metadata = src.meta
        metadata.update(dtype=rasterio.uint8, nodata=0)  # Set the output NoData value to 0
    
    # Write the modified data to a new output file
    with rasterio.open(output_tiff, 'w', **metadata) as dst:
        dst.write(data, 1)  # Write the modified data to the first band

# Example usage
input_tiff = 'NDRE/ndre_output.tif'
output_tiff = 'NDRE/nodata_removed.tif'
replace_nodata_with_zero(input_tiff, output_tiff)
