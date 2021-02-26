import os
import subprocess
import bpy
import platform



class SEURAT_OT_process_data(bpy.types.Operator):
    """Process the Seurat capture data and output it to a folder"""
    bl_idname = "seurat.process_data"
    bl_label = "Process Seurat capture data"

    def execute(self, context):
        scn = context.scene
        opt = scn.seurat_options

        if platform.system() != 'Windows':
            self.report({'ERROR'}, 'Processing Seurat data only possible on Windows')
            return {'CANCELLED'}

        output_directory = bpy.path.abspath(opt.mesh_output_path)

        input_path = bpy.path.abspath(opt.capture_output_path) + "manifest.json"
        output_path = bpy.path.abspath(opt.mesh_output_path) + "output"

        if not os.path.exists(output_directory):
            try:
                os.mkdir(output_directory)
            except:
                self.report({'ERROR'}, 'Failed to create output folder, check the mesh output path')
                return {'CANCELLED'}
            
            print ("Created output directory")
        else:
            print ("Output directory exists")

        script_file = os.path.realpath(__file__)
        directory = os.path.dirname(script_file)

        options = opt.seurat_command_flags
        # Default is "-texture_width 8192 -texture_height 8192 -pixels_per_degree 20 -triangle_count 180000"

        cmd = directory + "\seurat-pipeline-msvc2017-x64.exe -input_path " + input_path + " -output_path " + output_path + " " + options

        print(cmd)

        subprocess.run(cmd)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SEURAT_OT_process_data)

def unregister():
    bpy.utils.unregister_class(SEURAT_OT_process_data)