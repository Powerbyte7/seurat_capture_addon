import bpy


class SEURAT_PT_seurat_interface(bpy.types.Panel):
    """Create user interface for Seurat Capture"""
    bl_idname = "SEURAT_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Seurat Capture"
    bl_label = "Seurat Capture"

    def draw(self, context):
        #SC = bpy.context.scene.LF

        self.layout.use_property_split = True

        self.layout.operator('seurat.create_capture_box',
                             text="Create capture box",
                             icon='MESH_CUBE')

        self.layout.operator('seurat.capture_data',
                             text="Capture Seurat data",
                             icon='CAMERA_DATA')

        self.layout.operator('seurat.process_data',
                            text="Process Seurat data",
                            icon='MOD_BUILD')

        col = self.layout.column(align=True)
        subcol = col.column()

        subcol.prop(context.scene.seurat_options,
                    'view_groups', text="View groups")
        subcol.prop(context.scene.seurat_options, 'image_resolution')
        subcol.prop(context.scene.seurat_options, 'near_clip')
        subcol.prop(context.scene.seurat_options, 'far_clip')
        subcol.prop(context.scene.seurat_options, 'capture_output_path')
        subcol.prop(context.scene.seurat_options, 'mesh_output_path')


def register():
    bpy.utils.register_class(SEURAT_PT_seurat_interface)


def unregister():
    bpy.utils.unregister_class(SEURAT_PT_seurat_interface)
