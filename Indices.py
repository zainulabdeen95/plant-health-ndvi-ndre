import rasterio
import numpy as np
from rasterio.enums import Resampling
from rasterio import Affine

def calculate_indices(input_tif, output_ndvi_tif, output_ndre_tif):
    # Open the input TIF file
    with rasterio.open(input_tif) as src:
        # Read the relevant bands: Band 6 (Red), Band 7 (Green), Band 8 (NIR)
        red_band = src.read(6)  # Band 6: Red
        green_band = src.read(7)  # Band 7: Green
        nir_band = src.read(8)  # Band 8: NIR
        
        # Mask the data to handle any nodata values
        nodata = src.nodata
        if nodata is not None:
            red_band = np.ma.masked_equal(red_band, nodata)
            green_band = np.ma.masked_equal(green_band, nodata)
            nir_band = np.ma.masked_equal(nir_band, nodata)
        
        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        ndvi = (nir_band - red_band) / (nir_band + red_band)
        
        # Calculate NDRE: (NIR - Green) / (NIR + Green)
        ndre = (nir_band - green_band) / (nir_band + green_band)
        
        # Copy metadata to create new outputs
        metadata = src.meta
        metadata.update(dtype=rasterio.float32, count=1)
        
        # Write NDVI to output file
        with rasterio.open(output_ndvi_tif, 'w', **metadata) as dst_ndvi:
            dst_ndvi.write(ndvi.filled(nodata).astype(rasterio.float32), 1)
        
        # Write NDRE to output file
        with rasterio.open(output_ndre_tif, 'w', **metadata) as dst_ndre:
            dst_ndre.write(ndre.filled(nodata).astype(rasterio.float32), 1)


