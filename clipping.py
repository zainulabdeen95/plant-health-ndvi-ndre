import os
import rasterio
import fiona
import rasterio.mask
from shapely.geometry import shape, box, mapping
from fiona.transform import transform_geom
from pyproj import CRS, Transformer

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



