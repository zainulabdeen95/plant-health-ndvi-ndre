import os
from osgeo import gdal, ogr, osr

# Function to vectorize a TIFF image and save it as a GeoJSON
def vectorize_image(image_path, output_path):
    # Open the input image (TIFF file)
    raster = gdal.Open(image_path)
    if not raster:
        print(f"Failed to open image {image_path}")
        return

    # Get raster bands (we assume a single-band image)
    band = raster.GetRasterBand(1)

    # Create an output shapefile (GeoJSON)
    driver = ogr.GetDriverByName("GeoJSON")
    if not driver:
        print("GeoJSON driver is not available.")
        return

    # Create the GeoJSON file
    output_ds = driver.CreateDataSource(output_path)
    
    # Define the spatial reference system (we use the raster's SRS)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(raster.GetProjectionRef())

    # Create the layer for storing polygons
    layer = output_ds.CreateLayer('layer', srs=srs, geom_type=ogr.wkbPolygon)

    # Add a field for the pixel value (optional)
    field = ogr.FieldDefn("predicted", ogr.OFTInteger)
    layer.CreateField(field)

    # Polygonize the raster band
    gdal.Polygonize(band, None, layer, 0, [], callback=None)

    # Close the output dataset
    output_ds = None
    print(f"Vectorized image and saved as {output_path}")

def process_vector_folder(input_folder, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all TIFF files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.tif') or file_name.lower().endswith('.tiff'):
            image_path = os.path.join(input_folder, file_name)
            
            # Define the output GeoJSON path
            output_file = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.geojson")
            
            # Vectorize and save as GeoJSON
            vectorize_image(image_path, output_file)

# Example usage:
# input_folder = 'path/to/your/tiff/folder'
# output_folder = 'path/to/save/geojson/folder'
# process_folder(input_folder, output_folder)
