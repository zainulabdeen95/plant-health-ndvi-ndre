from osgeo import gdal, ogr
import numpy as np

import math  # For NaN (Not a Number)

def vectorize_tif(input_tif, output_shapefile, Values_Dict):
    """
    Vectorizes a raster (GeoTIFF) into polygons, adding a 'range' column for the DN values
    from the Values_Dict and a 'mean' column for each DN value from the Mean_Dict.
    
    :param input_tif: Path to the input TIFF file (raster).
    :param output_shapefile: Path to the output shapefile where the vectorized polygons will be saved.
    :param Values_Dict: A dictionary mapping DN values to ranges (e.g., {'1': '0.0 - 0.14'}).
    :param Mean_Dict: A dictionary mapping DN values to mean values (e.g., {'1': 0.13, '2': 0.4}).
    """
    # Open the input TIFF file using GDAL
    dataset = gdal.Open(input_tif)
    
    if dataset is None:
        raise FileNotFoundError(f"Could not open the input TIFF file: {input_tif}")
    
    # Get the raster band (assuming single-band raster for simplicity)
    band = dataset.GetRasterBand(1)
    
    # Get the projection (spatial reference system) from the input TIFF
    projection = dataset.GetProjection()
    
    # Create an in-memory shapefile driver to save vector output
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    if driver is None:
        raise RuntimeError("ESRI Shapefile driver not available.")
    
    # Create the shapefile and define a polygon layer
    output_ds = driver.CreateDataSource(output_shapefile)
    
    if output_ds is None:
        raise RuntimeError(f"Could not create shapefile: {output_shapefile}")
    
    # Set the spatial reference (projection) for the output shapefile
    spatial_ref = ogr.osr.SpatialReference(wkt=projection)
    
    # Define the layer to store polygons, with the same spatial reference
    layer = output_ds.CreateLayer('polygonized_layer', geom_type=ogr.wkbPolygon, srs=spatial_ref)
    
    if layer is None:
        raise RuntimeError(f"Could not create layer in shapefile: {output_shapefile}")
    
    # Create the 'DN' field in the attribute table of the shapefile
    field_dn = ogr.FieldDefn('predicted', ogr.OFTInteger)  # Assuming the raster values are integers
    layer.CreateField(field_dn)
    
    # Create the 'range' field to store the corresponding range from Values_Dict
    field_range = ogr.FieldDefn('range', ogr.OFTString)
    layer.CreateField(field_range)
    
    # Create the 'mean' field to store the Mean_Value
    # field_mean = ogr.FieldDefn('mean', ogr.OFTReal)
    # layer.CreateField(field_mean)
    
    # Read the raster data into an array
    raster_data = band.ReadAsArray()
    
    # Create a mask where we keep only values 1, 2, 3, 4 and set others to a background value (e.g., -1)
    mask = (raster_data == 1) | (raster_data == 2) | (raster_data == 3) | (raster_data == 4)
    raster_data[~mask] = -1  # Set all non-1,2,3,4 values to -1
    
    # Update the band with the filtered data (optional, depending on if you want to change the raster)
    band.WriteArray(raster_data)
    
    # Use the polygonize function to convert the raster to polygons, now with filtered values
    gdal.Polygonize(band, None, layer, layer.GetLayerDefn().GetFieldIndex('predicted'), [], callback=None)
    
    # Iterate over each feature in the layer to add 'range' and 'mean' values
    for feature in layer:
        # Get the DN value of the feature
        dn_value = feature.GetField('predicted')
        
        # Get the corresponding range from Values_Dict
        range_value = Values_Dict.get(str(dn_value), 'Unknown')  # Default to 'Unknown' if not found
        
        # Set the 'range' and 'mean' fields
        feature.SetField('range', range_value)
        
        # Update the feature in the layer
        layer.SetFeature(feature)
    
    # Close datasets
    output_ds = None
    dataset = None

    print(f"Vectorization completed. Shapefile saved as {output_shapefile}")


