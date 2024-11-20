import os
import rasterio
import fiona
import rasterio.mask
from shapely.geometry import shape, box, mapping
from fiona.transform import transform_geom
from pyproj import CRS, Transformer
from rasterio import mask as msk
import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# def clip_raster(tiff_path, shp_path, clipped_output_path):
#     '''
#     To clip raster on micro/field level
#     '''

#     with rasterio.open(tiff_path) as src:
#         clipped_img, clipped_transform = msk.mask(src, [geometry], crop=True, nodata= -999)
#         out_meta = src.meta.copy()
#         out_meta.update({
#             "driver": "GTiff",
#             "height": clipped_img.shape[1],
#             "width": clipped_img.shape[2],
#             "transform": clipped_transform,
#             "nodata": -999,
#         })
#         with rasterio.open(clipped_output_path, 'w', **out_meta) as dst:
#             dst.write(clipped_img)

def clip_raster_by_polygon(input_raster, clip_vector_file, output_folder):
    with rasterio.open(input_raster) as src:
        raster_crs = src.crs  
        raster_bounds = box(*src.bounds)  

        
        with fiona.open(clip_vector_file, "r") as vector_file:
            vector_crs = CRS.from_string(vector_file.crs['init']) if 'init' in vector_file.crs else CRS(vector_file.crs)
            
            
            transformer = Transformer.from_crs(vector_crs, raster_crs, always_xy=True) if raster_crs != vector_crs else None

            for feature in vector_file:
                polygon_id = feature['id']  
                geometry = shape(feature["geometry"])

                # Reproject geometry if necessary
                if transformer:
                    geometry = shape(transform_geom(vector_crs.to_string(), raster_crs.to_string(), feature["geometry"]))

                
                if not raster_bounds.intersects(geometry):
                    print(f"Polygon ID {polygon_id} does not overlap with the raster. Skipping.")
                    continue  # Skip polygons with no overlap
                
                
                try:
                    clipped_image, clipped_transform = rasterio.mask.mask(src, [mapping(geometry)], crop=True)
                    clipped_meta = src.meta.copy()

                    
                    clipped_meta.update({
                        "driver": "GTiff",
                        "height": clipped_image.shape[1],
                        "width": clipped_image.shape[2],
                        "transform": clipped_transform
                    })

                    
                    output_raster_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(input_raster))[0]}_clip_{polygon_id}.tif")

                    # Saving each clipped raster separately
                    with rasterio.open(output_raster_path, "w", **clipped_meta) as dest:
                        dest.write(clipped_image)

                    print(f"Clipped raster for polygon ID {polygon_id} saved at: {output_raster_path}")

                except ValueError as e:
                    print(f"Error clipping polygon ID {polygon_id}: {e}")

def clip_raster(tif_path, geojson, id_value, output_folder):
    # Open the raster file
    with rasterio.open(tif_path) as src:
        # Get the geometry that corresponds to the 'id_value'
        geometry = geojson[geojson['id'] == id_value].geometry.iloc[0]
        
        # Clip the raster using the geometry
        geom = [mapping(geometry)]  # Convert geometry to GeoJSON format
        out_image, out_transform = mask(src, geom, crop=True)
        
        # Update the metadata for the clipped raster
        out_meta = src.meta
        out_meta.update({
            "driver": "GTiff",
            "count": 1,  # Only one band for the clipped output
            "dtype": 'float32',  # Adjust based on your raster data type
            "crs": src.crs,
            "transform": out_transform
        })
        
        # Check the shape of the clipped image and make sure it's 2D
        # out_image should be (1, height, width), but we need to remove the extra dimension
        out_image = out_image[0]  # Remove the extra band dimension
        
        # Define the output file path
        output_file = os.path.join(output_folder, f"clipped_{id_value}.tif")
        
        # Save the clipped raster
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image, 1)  # Write the single band (first band)

    print(f"Clipped raster saved as: {output_file}")


def process_rasters(input_folder, geojson_file, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read the GeoJSON file using geopandas
    geojson = gpd.read_file(geojson_file)
    
    # Loop through all the TIFF files in the input folder
    for tif_file in os.listdir(input_folder):
        if tif_file.endswith(".tif"):
            # Extract the number from the file name (e.g., 1 from ndvi_output_clip_1_reclassified.tif)
            id_value = int(tif_file.split('_')[3])  # Adjust based on your file name pattern
            
            # Clip the raster and save it
            tif_path = os.path.join(input_folder, tif_file)
            clip_raster(tif_path, geojson, id_value, output_folder)