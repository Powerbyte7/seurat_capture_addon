bl_info = {  # noqa
    'name': 'Seurat Capture for Blender',
    'author': 'Digified',
    'description': 'Addon to capture data for use with Google Seurat',
    'version': (1, 1, 0),
    'blender': (2, 90, 1),
    'location': 'View3D',
    'category': 'Render'
}  # noqa

# Imports

import bpy  # noqa

# Global properties used in the addon, they are configurable in the UI


class SeuratOptionsPropertyGroup(bpy.types.PropertyGroup):

    view_groups: bpy.props.EnumProperty(
        items=[('2', '2', 'TODO'),
               ('4', '4', 'TODO'),
               ('8', '8', 'TODO'),
               ('16', '16', 'TODO'),
               ('32', '32', 'TODO'),
               ('64', '64', 'TODO')],
        name='View groups',
        default='16',
        description='Number of unique view groups used by seurat'
    )

    image_resolution: bpy.props.EnumProperty(
        items=[('256', '256', 'TODO'),
               ('512', '512', 'TODO'),
               ('1024', '1024', 'TODO'),
               ('2048', '2048', 'TODO'),
               ('4096', '4096', 'TODO'),
               ('8192', '8192', 'TODO')],
        name='Resolution [px]',
        default='1024',
        description='Seurat image resolution in [px]'
    )

    near_clip: bpy.props.FloatProperty(
        name='Clip Start',
        default=0.01,
        description='Seurat camera clipping distance'
    )

    far_clip: bpy.props.FloatProperty(
        name='Clip End',
        default=1000,
        description='Seurat camera clipping distance'
    )

    capture_output_path: bpy.props.StringProperty(
        name='Capture output path',
        default="//CaptureOutput/",
        subtype='DIR_PATH',
        description='Directory capture data will be exported to'
    )

    mesh_output_path: bpy.props.StringProperty(
        name='Mesh output path',
        default="//MeshOutput/",
        subtype='DIR_PATH',
        description='Directory Seurat mesh will be exported to'
    )

    seurat_command_flags: bpy.props.StringProperty(
        name='Seurat command flags',
        default="-texture_width 8192 -texture_height 8192 -pixels_per_degree 20 -triangle_count 180000",
        description='Seurat command flags used for processing'
    )

class SeuratAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.prop(context.scene.seurat_options, "seurat_command_flags", text="Seurat command flags")

# classes = (
#     SeuratOptionsPropertyGroup
# )

# register, unregister = bpy.utils.register_classes_factory(classes)
# bpy.types.Scene.SC = bpy.props.PointerProperty(type=SeuratOptionsPropertyGroup)


def register():
    # Register properties
    from bpy.utils import register_class
    from . import capture
    from . import interface
    from . import processing

    capture.register()
    processing.register()
    interface.register()
    
    register_class(SeuratAddonPreferences)

    register_class(SeuratOptionsPropertyGroup)
    bpy.types.Scene.seurat_options = bpy.props.PointerProperty(
        type=SeuratOptionsPropertyGroup)


def unregister():
    # Register properties
    from bpy.utils import unregister_class
    from . import capture
    from . import interface
    from . import processing

    capture.unregister()
    processing.unregister()
    interface.unregister()

    unregister_class(SeuratAddonPreferences)

    unregister_class(SeuratOptionsPropertyGroup)


# def unregister():
#     bpy.utils.unregister_module(__name__)


# if __name__ == "__main__":
#     register()
