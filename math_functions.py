import os
import json
import math
import operator


def project_point(matrix, point):
    """Projects a 3D point using a 4x4 matrix.
    Args:
      matrix: A 4x4 matrix represented as a list of 16 floats.
      point: A 3D point represented as a list of 3 floats.
    Returns:
      The projected point, represented as a list of 3 floats.
    """
    result_hom = [0.0, 0.0, 0.0, 0.0]
    for row in range(4):
        for col in range(3):
            result_hom[row] += matrix[4 * row + col] * point[col]
        # point.w = 1.0 implicitly
        result_hom[row] += matrix[4 * row + 3]
    w = result_hom[3]
    return list(map(operator.div, result_hom[0:3], [w, w, w]))


def world_eye_matrix_from_face(face_name):
    """Creates world-from-eye matrix for the given face of a cube map.
    Args:
      face_name: Name of the face. Must be one of 'front', 'back', 'left',
          'right', 'bottom', 'top'.
    Returns:
      The world-from-eye matrix for the given face as a list in row-major order.
    Raises:
      ValueError: face_name is not the name of a cube map face.
    """
    # pylint: disable=bad-whitespace
    # pylint: disable=bad-continuation
    if face_name is 'front':  # DONE
        return [1.0,  0.0,  0.0,  0.0,
                0.0,  0.0,  -1.0,  0.0,
                0.0,  1.0,  0.0,  0.0,
                0.0,  0.0,  0.0,  1.0]  # pyformat: disable
    elif face_name is 'back':  # DONE
        return [-1.0,  0.0,  0.0,  0.0,
                0.0,  0.0,  1.0,  0.0,
                0.0,  1.0, 0.0,  0.0,
                0.0,  0.0,  0.0,  1.0]  # pyformat: disable
    elif face_name is 'left':  # DONE
        return [0.0,  0.0,  1.0,  0.0,
                1.0,  0.0,  0.0,  0.0,
                0.0,  1.0,  0.0,  0.0,
                0.0,  0.0,  0.0,  1.0]  # pyformat: disable
    elif face_name is 'right':  # DONE
        return [0.0,  0.0, -1.0,  0.0,
                -1.0,  0.0,  0.0,  0.0,
                0.0,  1.0,  0.0,  0.0,
                0.0,  0.0,  0.0,  1.0]  # pyformat: disable
    elif face_name is 'bottom':  # DONE
        return [1.0,  0.0,  0.0,  0.0,
                0.0,  1.0,  0.0,  0.0,
                0.0,  0.0,  1.0,  0.0,
                0.0,  0.0,  0.0,  1.0]  # pyformat: disable
    elif face_name is 'top':  # DONE
        return [1.0,  0.0,  0.0,  0.0,
                0.0,  -1.0, 0.0,  0.0,
                0.0,  0.0,  -1.0,  0.0,
                0.0,  0.0,  0.0,  1.0]  # pyformat: disable
    else:
        raise ValueError('Invalid face_name')


def cube_face_projection_matrix(near, far):
    """Creates a cube-face 90 degree FOV projection matrix.
    The created matrix is an OpenGL-style projection matrix.
    Args:
      near: Eye-space Z position of the near clipping plane.
      far: Eye-space Z position of the far clipping plane.
    Returns:
      The clip-from-eye matrix as a list in row-major order.
    Raises:
      ValueError: Invalid clip planes. near <= 0.0 or far <= near.
    """
    if near <= 0.0:
        raise ValueError('near must be positive.')

    if far <= near:
        raise ValueError('far must be greater than near.')

    left = -near
    right = near
    bottom = -near
    top = near
    a = (2.0 * near) / (right - left)
    b = (2.0 * near) / (top - bottom)
    c = (right + left) / (right - left)
    d = (top + bottom) / (top - bottom)
    e = (near + far) / (near - far)
    f = (2.0 * near * far) / (near - far)

    # pylint: disable=bad-whitespace
    return [a,   0.0,  c,   0.0,
            0.0, b,    d,   0.0,
            0.0, 0.0,  e,   f,
            0.0, 0.0, -1.0, 0.0]  # pyformat: disable


# OLD FUNCTION, REMOVE
# def radical_inverse2(a, base):
#     """Computes the radical inverse of |a| in base |base|.
#     Args:
#       a: The integer number for which the radical inverse is computed.
#       base: The radical inverse is computed in this base (integer).
#     Returns:
#       The radical inverse as a float in the range [0.0, 1.0).
#     """
#     reversed_digits = 0
#     base_n = 1
#     # Compute the reversed digits, base b.
#     while a > 0:
#         next_a = a / base
#         digit = a - next_a * base
#         reversed_digits = reversed_digits * base + digit
#         base_n *= base
#         a = next_a
#     # Only when done are the reversed digits divided by b^n.
#     return min(reversed_digits / float(base_n), 1.0)


def radical_inverse(a, base):
    """Computes the radical inverse of |a| in base |base|.
    Args:
      a: The integer number for which the radical inverse is computed.
      base: The radical inverse is computed in this base (integer).
    Returns:
      The radical inverse as a float in the range [0.0, 1.0).
    """
    digit = 1.0 / float(base)
    radical = digit
    inverse = 0.0

    while (a > 0):
        inverse += digit * float(a % base)
        digit *= radical
        a /= base
    # Only when done are the reversed digits divided by b^n.
    return float(inverse)


def point_in_a_box(box_min, box_max, sample):
    """Computes a sample point inside a box with arbitrary number of dimensions.
    Args:
      box_min: A list of floats representing the lower bounds of the box.
      box_max: A list of floats representing the upper bounds of the box.
      sample: A list of floats in the range [0.0, 1.0] representing the
        relative sample position in the box.
    Returns:
      A list of floats, representing the absolute position of the sample in
      the box.
    """
    delta = list(map(operator.sub, box_max, box_min))
    offset = list(map(operator.mul, delta, sample))
    position = list(map(operator.add, box_min, offset))
    return position


def distance(point_a, point_b):
    """Computes the euclidean distance between two points.
    The points can have an aribtrary number of dimensions.
    Args:
      point_a: A list of numbers representing the first point.
      point_b: A list of numbers representing the second point.
    Returns:
      The euclidean distance as a float.
    """
    delta = list(map(operator.sub, point_a, point_b))
    delta_sqr = list(map(operator.mul, delta, delta))
    distance_sqr = 0.0
    for element in delta_sqr:
        distance_sqr += element
    return math.sqrt(distance_sqr)


def generate_camera_positions(headbox_min, headbox_max, num_cameras):
    """Generates camera positions in a headbox.
    Camera posittions are computed as a 3D Hammersley point set. The points are
    transformed such that their bounding box is exactly equal to the headbox. The
    points are then sorted according to distance to the headbox center. Finally,
    the point that is closest to the headbox center is replaced by the headbox
    center itself to include a view from the reference camera.
    Args:
      headbox_min: The lower bounds of the headbox as a list of 3 floats.
      headbox_max: The upper bounds of the headbox as a list of 3 floats.
      num_cameras: The number of cameras to generate. Should be a power of two.
    Returns:
      A list of 3D points (each a list of 3 floats), representing the positions
      of the generated cameras.
    Raises:
      ValueError: num_cameras is not positive.
    """
    if num_cameras <= 0:
        raise ValueError('num_cameras must be positive')

    if num_cameras == 1:
        # Use the headbox center if a single camera position is requested.
        return [point_in_a_box(headbox_min, headbox_max, [0.5, 0.5, 0.5])]

    samples = []
    max_sample = [0.0, 0.0, 0.0]
    for i in range(num_cameras):
        # Use a 3D Hammersley point set for the samples.
        sample = [
            i / float(num_cameras),
            radical_inverse(i, 2),
            radical_inverse(i, 3)
        ]
        for dim in range(3):
            max_sample[dim] = max(max_sample[dim], sample[dim])
        samples.append(sample)

    headbox_center = point_in_a_box(headbox_min, headbox_max, [0.5, 0.5, 0.5])
    camera_positions = []

    for sample in samples:
        # Normalize the samples so that their bounding box is the unit cube.
        for dim in range(3):
            sample[dim] /= max_sample[dim]
        position = point_in_a_box(headbox_min, headbox_max, sample)
        camera_positions.append(position)

    sorted_positions = sorted(
        camera_positions, key=lambda point: distance(point, headbox_center))
    # Replace the point closest to the headbox center by the headbox center
    # itself.
    sorted_positions[0] = point_in_a_box(
        headbox_min, headbox_max, [0.5, 0.5, 0.5])
    return sorted_positions
