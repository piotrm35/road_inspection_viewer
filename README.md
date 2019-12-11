Road Inspection Viewer

# Purpose
QGIS plugin displaying photos from road inspection.

# How to start work
One assumes that the QGIS layer has continuous ids of points. The points has "file_names" field of photo file names
that are separated with semicolons. The plugin can be started by a button with its icon on the plugin toolbar.
You should first set a path to photos folder ("path" button).
If in road inspection are more than one photo per point, You can add an extra windows ("extra window" button).
You can check the plugin by using the example from "example" subfolder of the plugin folder.
Remember to select a layer with a road inspection and a start point first.

If You want to see geotagged photos on a map and inspect them by this plugin take a look in my EXIF_parser Github repository.

If You want to make a very basic road inspection, to see it on a map and inspect by this plugin - take a look in my Aida_data_parser Github repository.
 
# License:
GNU General Public License, version 2

