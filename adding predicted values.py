import os
import glob
from qgis.core import *
from qgis import processing
from PyQt5.QtCore import QVariant

def polygonize_raster_with_predicted(raster_path, output_folder):
    # Load the raster layer
    raster_layer = QgsRasterLayer(raster_path, os.path.basename(raster_path))
    
    if not raster_layer.isValid():
        print(f"Skipping invalid raster file: {raster_path}")
        return

    print(f"Processing raster file: {raster_path}")

    # Define the DN to predicted mapping
    dn_to_predicted = {1: 228, 2: 229, 3: 230}

    # Set up the output path for the polygonized vector layer
    output_path = os.path.join(output_folder, os.path.basename(raster_path).replace('.tif', '.shp'))

    # Run the GDAL Polygonize algorithm through the processing module
    params = {
        'INPUT': raster_layer,
        'BAND': 1,
        'FIELD': 'DN',
        'EIGHT_CONNECTEDNESS': False,
        'OUTPUT': output_path
    }

    # Execute the polygonization
    result = processing.run("gdal:polygonize", params)
    polygonized_layer = QgsVectorLayer(result['OUTPUT'], "polygonized", "ogr")

    if not polygonized_layer.isValid():
        print(f"Failed to create polygonized layer for: {raster_path}")
        return

    # Start editing the polygonized layer to add 'predicted' field
    polygonized_layer.startEditing()
    predicted_field = QgsField('predicted', QVariant.Int)
    polygonized_layer.dataProvider().addAttributes([predicted_field])
    polygonized_layer.updateFields()

    # Get field indices
    dn_field_index = polygonized_layer.fields().indexOf('DN')
    predicted_field_index = polygonized_layer.fields().indexOf('predicted')

    # Update each feature: set predicted values or delete if DN=0
    features_to_update = []
    for feature in polygonized_layer.getFeatures():
        dn_value = feature['DN']

        if dn_value == 0:
            # Mark feature for deletion if DN=0
            polygonized_layer.dataProvider().deleteFeatures([feature.id()])
        elif dn_value in dn_to_predicted:
            # Assign the predicted value based on DN
            feature[predicted_field_index] = dn_to_predicted[dn_value]
            features_to_update.append(feature)
    
    # Apply updates in batch
    polygonized_layer.dataProvider().changeAttributeValues({f.id(): {predicted_field_index: f[predicted_field_index]} for f in features_to_update})

    # Commit changes to save the output
    polygonized_layer.commitChanges()

    print(f"Polygonized shapefile created successfully at {output_path}")

def process_rasters_in_directory(input_directory, output_folder):
    # List all raster files in the directory (assuming .tif format)
    raster_files = glob.glob(os.path.join(input_directory, '*.tif'))

    if not raster_files:
        print("No raster files found in the directory.")
        return

    # Process each raster file
    for raster_file in raster_files:
        polygonize_raster_with_predicted(raster_file, output_folder)

# Usage example
input_directory = r'D:\Farmdar\Shaikhoo_Reports\NDRE\clipped\reclassified'  # Folder containing raster files
output_folder = r'D:\Farmdar\Shaikhoo_Reports\NDRE\clipped\reclassified\NDRE'  # Folder to save polygonized shapefiles

# Process all rasters in the directory and polygonize with predicted values
process_rasters_in_directory(input_directory, output_folder)
