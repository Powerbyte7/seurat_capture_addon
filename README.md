# Seurat Capture addon for Blender
Seurat Capture uses [Google Seurat](https://github.com/googlevr/seurat) in order to simplify scenes in Blender for use in VR. Here's how it works:

1. Create a capture box, this will be the area the viewer will be able to move in. Make sure this does NOT intersect with any geometry.

2. Capture the images needed for Seurat, this will render images from various positions inside of the box. Depending on the render engine and render settings this can take quite some time.

3. Process the data, this will also take some time. Once this is finished you will be able to import the generated output.obj and output.exr files.

Extra tips:
- You can view progress by going to Window > Toggle system console on Windows
- Avoid using scenes with a lot of transparency
- You can change the Seurat command flags in the user preferences, you can find more info about them [here](https://github.com/googlevr/seurat#command-line-parameters)

Limitations:
- The addon needs to use the compositor in order to work and will delete any existing nodes
- Blender's UI might freeze when capturing or processing data, this doesn't mean the addon stopped working
- Processing data on Linux and Mac directly with the addon isn't supported, only capturing
- Using Seurat for Oculus home environments isn't recommended on firmware V25 and later, the texture interpolation causes noticable artifacts. With the introduction of teleportation inside homes, the limited view also becomes a big limitation.