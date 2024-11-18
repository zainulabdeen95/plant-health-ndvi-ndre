import os
import glob
import numpy as np
import rasterio
from rasterio import features
from shapely.geometry import shape
import fiona
from fiona.crs import from_epsg
from collections import defaultdict

def polygonize_raster_with_predicted(raster_path, output_folder, report):
    # Load the raster data
    with rasterio.open(raster_path) as src:
        if src is None:
            print(f"Skipping invalid raster file: {raster_path}")
            return

        print(f"Processing raster file: {raster_path}")

        if report == 'ndvi':
            # Define the DN to predicted mapping for NDVI
            dn_to_predicted = {1: 220, 2: 221, 3: 222, 4: 223}

        elif report == 'ndre':
            # Define the DN to predicted mapping for NDRE
            dn_to_predicted = {1: 228, 2: 229, 3: 230}
        
        # Read the raster's first band (assuming single band raster)
        band = src.read(1)
        
        # Mask out values that are zero (they are usually no-data values)
        mask = band != 0

        # Use rasterio's features.polygonize to convert raster to polygons
        results = list(features.shapes(band, mask=mask, transform=src.transform))

        # Prepare the output shapefile path
        output_path = os.path.join(output_folder, os.path.basename(raster_path).replace('.tif', '.shp'))

        # Define schema for the shapefile: we need 'DN' and 'predicted' fields
        schema = {
            'geometry': 'Polygon',
            'properties': {'predicted': 'int'}
        }

        # Open the output shapefile for writing
        with fiona.open(output_path, 'w', driver='ESRI Shapefile', crs=from_epsg(src.crs.to_epsg()), schema=schema) as output:
            for geom, value in results:
                # Only process non-zero values
                if value == 0:
                    continue

                # Create the feature: use shapely for geometry handling
                polygon = shape(geom)

                # Map the DN value to the predicted value
                predicted_value = dn_to_predicted.get(value, None)

                # Only write the feature if there is a valid 'predicted' value
                if predicted_value is not None:
                    output.write({
                        'geometry': polygon.__geo_interface__,
                        'properties': {'predicted': predicted_value}
                    })

        print(f"Polygonized shapefile created successfully at {output_path}")

def process_rasters_in_directory(input_directory, output_folder, report):
    # List all raster files in the directory (assuming .tif format)
    raster_files = glob.glob(os.path.join(input_directory, '*.tif'))

    if not raster_files:
        print("No raster files found in the directory.")
        return

    # Process each raster file
    for raster_file in raster_files:
        polygonize_raster_with_predicted(raster_file, output_folder, report)


