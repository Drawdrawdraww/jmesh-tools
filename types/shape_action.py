import gpu
from gpu_extras.batch import batch_for_shader

from .. utils.fc_draw_utils import draw_circle_2d, set_poly_smooth

from .. fc_preferences import get_preferences

import bgl
import blf

class Shape_Action:

  def __init__(self):
    self._x = 0
    self._y = 0
    self._shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

  def mouse_inside(self, context, event, mouse_pos_2d, mouse_pos_3d) -> bool:
    x = mouse_pos_2d[0]
    y = mouse_pos_2d[1]

    if x >= self._x and x <= self._x + 14 and y <= self._y and y >= self._y - 14:
      return True

    return False

  def set_hover(self, is_hover):
    pass

  def get_position(self):
    return (self._x, self._y)

  def set_position(self, x, y):
    self._x = x
    self._y = y

  def draw(self):
    pass

class Shape_Size_Action(Shape_Action):

  def draw(self):
    set_poly_smooth()
    self._shader.bind()
    self._shader.uniform_float("color", (0.9, 0.0, 0.0, 1.0))
    self._batch.draw(self._shader)
    set_poly_smooth(False)

  def set_position(self, x, y):
    super().set_position(x, y)

    x_r = x + 14
    y_r = y - 12

    indices = ((0, 1, 2), (2, 0, 3))
    coords_middle = [(x, y - 6), (x + 7,  y_r), (x_r, y - 6), (x + 7, y)]
    self._batch = batch_for_shader(self._shader, 'TRIS', {"pos" : coords_middle}, indices=indices)

class Shape_Action_Symmetry(Shape_Action):

  def __init__(self, offset, axis = 'X', color=[1.0, 0.21, 0.33, 1.0]):
    super().__init__()
    self._axis = axis
    self._color = color
    self._offset = offset
    self._radius = 20
    self.set_symmetry()

  def set_symmetry(self):

    prefs = get_preferences()
    sd = prefs.symmetrize_direction

    if sd == 'Selected to opposite':
      pos_prefix = "POSITIVE"
      neg_prefix = "NEGATIVE"
    else:
      pos_prefix = "NEGATIVE"
      neg_prefix = "POSITIVE"     

    if self._axis == "X":
      self._symmetry_command = pos_prefix + "_X"
    elif self._axis == "-X":
      self._symmetry_command = neg_prefix + "_X"
    elif self._axis == "Y":
      self._symmetry_command = pos_prefix + "_Y"
    elif self._axis == "-Y":
      self._symmetry_command = neg_prefix + "_Y"
    elif self._axis == "Z":
      self._symmetry_command = pos_prefix + "_Z"
    elif self._axis == "-Z":
      self._symmetry_command = neg_prefix + "_Z"

  def get_symmetry_command(self):
    return self._symmetry_command

  def mouse_inside(self, context, event, mouse_pos_2d, mouse_pos_3d) -> bool:
    x = mouse_pos_2d[0]
    y = mouse_pos_2d[1]

    if x >= self._x - self._radius and x <= self._x + self._radius and y <= self._y + self._radius and y >= self._y - self._radius:
      return True

    return False

  def set_hover(self, is_hover):
    if is_hover:
      self._color[3] = 1.0
    else:
      self._color[3] = 0.5

  def set_position(self, x, y):
    super().set_position(x, y)

  def get_offset(self):
    return self._offset

  def draw(self):

    circle_co = draw_circle_2d((self._x, self._y), self._color, self._radius, 32)
    
    blf.size(1, 14, 72)
    blf.color(1, 0, 0, 0, 1)
    dim = blf.dimensions(1, self._axis)
    blf.position(1, self._x - dim[0] / 2, self._y - dim[1] / 2, 0)
    blf.draw(1, self._axis)


class Shape_Array_Action(Shape_Action):

  def __init__(self, axis = 'Y'):
    self._axis = axis
    self._offset = 0.5
    super().__init__()

  def get_axis(self):
    return self._axis

  @property
  def offset(self):
    return self._offset

  @offset.setter
  def offset(self, value):
      self._offset = value
    
  def draw(self):
    set_poly_smooth()
    self._shader.bind()
    self._shader.uniform_float("color", (1.0, 0.2, 0.0, 1.0))
    self._batch.draw(self._shader)
    set_poly_smooth(False)

  def set_position(self, x, y):
    super().set_position(x, y)

    x_r = x + 11
    y_b = y - 11

    lines = []

    if self._axis == 'Y':
      for i in range(1, 5):
        lines.append((x,   y + 2 - (i * 3)))
        lines.append((x_r, y + 2 - (i * 3)))
    else:
      for i in range(1, 5):
        lines.append((x + (i * 3),   y))
        lines.append((x + (i * 3), y_b))

    self._batch = batch_for_shader(self._shader, 'LINES', {"pos": lines})

class Shape_Mirror_Action(Shape_Action):
   
  def draw(self):

    set_poly_smooth()
    bgl.glLineWidth(2)

    self._shader.bind()
    self._shader.uniform_float("color", (0.8, 0.30, 1.0, 1.0))

    self._batch.draw(self._shader)

    bgl.glLineWidth(1)
    set_poly_smooth(False)

  def set_position(self, x, y):
    super().set_position(x, y)

    x_m = x + 6
    y_t = y - 11

    points = []

    # Left 
    points.append((x_m-6, y_t))
    points.append((x_m-6, y))
    points.append((x_m, y - 5))

    points.append((x_m+6, y))
    points.append((x_m+6, y_t))

    self._batch = batch_for_shader(self._shader, 'LINE_STRIP', {"pos": points})


class Shape_Operation_Action(Shape_Action):

  def __init__(self):
    super().__init__()
    self._color=[0.8, 0.0, 0.2, 1.0]
   
  def draw(self):

    circle_co = draw_circle_2d((self._x + 6, self._y - 6), self._color, 6, 16)

  def set_position(self, x, y):
    super().set_position(x, y)

class Shape_CircleArray_Action(Shape_Action):

  def __init__(self):
    super().__init__()
    self._color=[0.2, 0.2, 0.8, 1.0]
   
  def draw(self):

    circle_co = draw_circle_2d((self._x + 5, self._y - 6), self._color, 6, 5, 'POINTS')

  def set_position(self, x, y):
    super().set_position(x, y)
    