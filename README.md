# Seurat Capture addon for Blender
Seurat Capture uses Google Seurat in order to simplify scenes in Blender for use in VR. Here's how it works:

1. Create a capture box, this will be the area the viewer will be able to move in. Make sure this does NOT intersect with any geometry.

2. Capture the images needed for Seurat, this will render images from various positions inside of the box. Depending on the render engine and render settings this can take some time.

3. Process the data, this will also take some time. Once this is finished you will be able to import the generated output.obj and output.exr files.

Extra tips:
- You can view progress by going to Window > Toggle system console.
- Avoid using scenes with a lot of transparency.
- You can change the Seurat command flags in the user preferences, you can find more info about them here

Limitations:
- The addon needs to use the compositor in order to work and will delete any existing nodes
- Blender's UI might freeze when capturing or processing data, this doesn't mean the addon stopped working
- Processing data on Linux and Mac directly with the addon isn't supported, only capturing
