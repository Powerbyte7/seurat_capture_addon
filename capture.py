import bpy
import os
import json
import operator
from . import math_functions


class SEURAT_OT_create_capture_box(bpy.types.Operator):
    """Create a capture box (Box empty), this will be used to generate the camera positions"""
    bl_idname = "seurat.create_capture_box"
    bl_label = "Create Seurat capture box"

    def execute(self, context):
        scn = context.scene

        # Check to see if a capture box exists before adding one
        capture_box_exists = scn.objects.get("SeuratCaptureBox")

        if capture_box_exists is not None:
            print("Seurat capture box already present inside scene")
            return {'CANCELLED'}

        # Create empty to server as capture box
        seurat_capture_box = bpy.data.objects.new("SeuratCaptureBox", None)

        # Change empty display type to cube
        seurat_capture_box.empty_display_type = 'CUBE'

        # Lock object rotation, the capture box shouldn't be rotated
        seurat_capture_box.lock_rotation[0] = True
        seurat_capture_box.lock_rotation[1] = True
        seurat_capture_box.lock_rotation[2] = True

        # Link the object to the scene
        scn.collection.objects.link(seurat_capture_box)
        return {'FINISHED'}


class SEURAT_OT_capture_data(bpy.types.Operator):
    """Capture seurat data inside the capture box and export it to a folder"""
    bl_idname = "seurat.capture_data"
    bl_label = "Capture Seurat data"

    def execute(self, context):
        scn = context.scene
        mf = math_functions
        opt = scn.seurat_options

        # Get Seurat capture box transforms and store it as headbox_min and headbox_max

        # Get the Seurat capture box from the scene
        seurat_capture_box = scn.objects.get("SeuratCaptureBox")

        # If there's no capture box this will end the operator
        if seurat_capture_box is None:
            print("Seurat capture box not found")
            return {'CANCELLED'}

        # Get capture box transforms
        capture_box_location = seurat_capture_box.location
        capture_box_scale = seurat_capture_box.scale

        # Store the headbox data
        headbox_min = [capture_box_scale[0] + capture_box_location[0], capture_box_scale[1] +
                       capture_box_location[1], capture_box_scale[2] + capture_box_location[2]]
        headbox_max = [-capture_box_scale[0] + capture_box_location[0], -capture_box_scale[1] +
                       capture_box_location[1], -capture_box_scale[2] + capture_box_location[2]]

        # Calculate the camera positions used for capturing
        view_groups = int(opt.view_groups)

        camera_positions = mf.generate_camera_positions(
            headbox_min, headbox_max, view_groups)

        # Store variables, they will be used to restore the following:
        # - Render resolution and percentage
        # - The active camera

        render_resolution_x = scn.render.resolution_x
        render_resolution_y = scn.render.resolution_y
        resolution_percentage = scn.render.resolution_percentage
        active_camera = scn.camera

        # Get variables for rendering
        near_clip = opt.near_clip
        far_clip = opt.far_clip
        output_path = opt.capture_output_path
        image_resolution = int(opt.image_resolution)

        # Prepare the scene for rendering
        self.render_preparation(context, image_resolution)
        self.compositor_setup(context, output_path)

        # Create a render loop
        for view_group_index, position in enumerate(camera_positions):

            for face in ['front', 'back', 'left', 'right', 'bottom', 'top']:
                # Render image
                self.render_color_and_depth(context, face, position,
                                            output_path, near_clip, far_clip)

                # Blender forcibly adds a frame number to renders
                # This function corrects the name
                self.rename_renders(
                    context, view_group_index, face, output_path)

        # Restore user settings
        scn.render.resolution_x = render_resolution_x
        scn.render.resolution_y = render_resolution_y
        scn.render.resolution_percentage = resolution_percentage
        scn.camera = active_camera

        # Write JSON manifest
        headbox_center = mf.point_in_a_box(
            headbox_min, headbox_max, [0.5, 0.5, 0.5])
        absolute_output_path = bpy.path.abspath(output_path)

        print(absolute_output_path)

        view_groups = self.create_view_groups(headbox_center, camera_positions, image_resolution, near_clip, far_clip,  depth_type='EYE_Z',
                                              depth_channel_name='R', color_file_path_pattern='%s_color.%04d.exr', depth_file_path_pattern='%s_depth.%04d.exr')
        json_string = json.dumps({'view_groups': view_groups}, indent=2)
        with open((absolute_output_path + "manifest.json"), 'w') as json_file:
            json_file.write(json_string)

        return {'FINISHED'}

    def compositor_setup(self, context, output_path):
        # Switch on nodes and get reference
        # Global context required
        scene = bpy.context.scene
        scene.use_nodes = True

        tree = bpy.context.scene.node_tree

        # Clear nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create input image node
        render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers_node.location = 0, 0

        # Create output node
        file_output_node = tree.nodes.new('CompositorNodeOutputFile')
        file_output_node.base_path = output_path
        file_output_node.format.file_format = 'OPEN_EXR'

        # Create file subpaths
        file_output_node.layer_slots.new('color#')
        file_output_node.layer_slots.new('depth#')

        # Move file output node
        file_output_node.location = 400, 0

        # link nodes
        # links = tree.links
        # link = links.new(render_layers_node.outputs[0], file_output_node[1])
        # link = links.new(render_layers_node.outputs[1], file_output_node[2])

        tree.links.new(
            render_layers_node.outputs[0], file_output_node.inputs[1])
        tree.links.new(
            render_layers_node.outputs[2], file_output_node.inputs[2])

    def render_preparation(self, context, image_resolution):
        context.scene.render.resolution_x = image_resolution
        context.scene.render.resolution_y = image_resolution
        context.scene.render.resolution_percentage = 100

        if context.scene.render.engine == 'BLENDER_EEVEE':
            context.scene.eevee.use_overscan = True
            context.scene.eevee.overscan_size = 10.0

    def render_color_and_depth(self, context, face, position, output_path, near_clip, far_clip):

        # Create camera
        seurat_camera = bpy.data.cameras.new("SeuratCamera")
        seurat_camera.lens = 18
        seurat_camera.clip_start = near_clip
        seurat_camera.clip_end = far_clip

        seurat_camera_obj = bpy.data.objects.new("SeuratCamera", seurat_camera)

        # Set camera position
        seurat_camera_obj.location = (position[0], position[1], position[2])

        # Set camera rotation
        if face is 'front':
            seurat_camera_obj.rotation_euler = (
                1.5707963267948966, 0, 0)
        elif face is 'back':
            seurat_camera_obj.rotation_euler = (
                1.5707963267948966, 0, 3.141592653589793)
        elif face is 'left':
            seurat_camera_obj.rotation_euler = (
                1.5707963267948966, 0, 1.5707963267948966)
        elif face is 'right':
            seurat_camera_obj.rotation_euler = (
                1.5707963267948966, 0, -1.5707963267948966)
        elif face is 'bottom':
            seurat_camera_obj.rotation_euler = (0, 0, 0)
        elif face is 'top':
            seurat_camera_obj.rotation_euler = (3.141592653589793, 0, 0)

        # Set camera as active
        context.scene.camera = seurat_camera_obj

        # Render image
        bpy.ops.render.render()

        # Delete camera
        bpy.data.objects.remove(seurat_camera_obj, do_unlink=True)

    def rename_renders(self, context, view, face, output_path):
        # The following is not an optimal solution, but considering there's
        # no way to disable the automatic addition of a frame number
        # the file has to be renamed manually

        # Using the 'color#' and 'depth#' subpaths in the compositor makes renaming the files feasible

        # Get frame number and abosule path for renaming
        frame = context.scene.frame_current
        absolute_output_path = bpy.path.abspath(output_path)

        # Create absolute paths to the current render results
        color_path = absolute_output_path + "color" + str(frame) + ".exr"
        depth_path = absolute_output_path + "depth" + str(frame) + ".exr"

        # Create absolute paths to the wanted render results
        color_file_name = absolute_output_path + \
            face + "_color." + str(view).zfill(4) + ".exr"
        depth_file_name = absolute_output_path + \
            face + "_depth." + str(view).zfill(4) + ".exr"

        # Rename the color image
        try:
            os.rename(color_path, color_file_name)
        except FileNotFoundError:
            print("Color image not found")

        # Rename depth image
        try:
            os.rename(depth_path, depth_file_name)
        except FileNotFoundError:
            print("Depth image not found")

    def create_view_groups(self, headbox_center, camera_positions, image_size, near_clip, far_clip, depth_type, depth_channel_name, color_file_path_pattern, depth_file_path_pattern):
        mf = math_functions
        view_groups = []
        for view_group_index, absolute_position in enumerate(camera_positions):
            views = []
            for face in ['front', 'back', 'left', 'right', 'bottom', 'top']:
                # Camera position relative to headbox center.
                position = list(
                    map(operator.sub, absolute_position, headbox_center))
                clip_from_eye_matrix = mf.cube_face_projection_matrix(
                    near_clip, far_clip)
                world_from_eye_matrix = mf.world_eye_matrix_from_face(face)
                # Set translation component of world-from-eye matrix.
                for i in range(3):
                    world_from_eye_matrix[4 * i + 3] = position[i]

                # Create camera object
                camera = {
                    'image_width': image_size,
                    'image_height': image_size,
                    'clip_from_eye_matrix': clip_from_eye_matrix,
                    'world_from_eye_matrix': world_from_eye_matrix,
                    'depth_type': depth_type
                }

                # Create view object and add it to the view groups
                color_image_path = (color_file_path_pattern %
                                    (face, view_group_index))
                depth_image_path = (depth_file_path_pattern %
                                    (face, view_group_index))
                view = {
                    'projective_camera': camera,
                    'depth_image_file': {
                        'color': {
                            'path': color_image_path,
                            'channel_0': 'R',
                            'channel_1': 'G',
                            'channel_2': 'B',
                            'channel_alpha': 'A'
                        },
                        'depth': {
                            'path': depth_image_path,
                            'channel_0': depth_channel_name
                        }
                    }
                }
                views.append(view)
            view_group = {'views': views}
            view_groups.append(view_group)

        # Return the view_groups as a Python list.
        return view_groups


def register():
    bpy.utils.register_class(SEURAT_OT_create_capture_box)
    bpy.utils.register_class(SEURAT_OT_capture_data)


def unregister():
    bpy.utils.unregister_class(SEURAT_OT_create_capture_box)
    bpy.utils.unregister_class(SEURAT_OT_capture_data)
