from ursina import *

class Draggable_Entity(Entity):
    """An entity which can be dragged to encapsulate other things in an editor menu, hijacked from ursina's prefabs for Buttons"""
    _z_plane = None

    def __init__(self, **kwargs):
        if not __class__._z_plane:
            __class__._z_plane = Entity(name='_z_plane', scale=(9999,9999), enabled=False, eternal=True)

        super().__init__(**kwargs)
        self.model="quad"
        self.collider="box"
        self.require_key = None
        self.dragging = False
        self.delta_drag = 0
        self.start_pos = self.world_position
        self.start_offset = (0,0,0)
        self.step = (0,0,0)
        self.plane_direction = (0,0,1)
        self.lock = Vec3(0,0,1)     # set to 1 to lock movement on any of x, y and z axes
        self.min_x, self.min_y, self.min_z = -inf, -inf, -inf
        self.max_x, self.max_y, self.max_z = inf, inf, inf

        if not Draggable_Entity._z_plane.model: # set these after game start so it can load the model
            Draggable_Entity._z_plane.model = 'quad'
            Draggable_Entity._z_plane.collider = Mesh(vertices=((-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)), triangles=((0,1,2,3),), mode='triangle')
            Draggable_Entity._z_plane.color = color.clear


        for key, value in kwargs.items():
            if key == 'collider' and value == 'sphere' and self.has_ancestor(camera.ui):
                print('error: sphere colliders are not supported on Draggables in ui space.')

            if key == 'text' or key in self.attributes:
                continue

            setattr(self, key, value)


    def input(self, key):
        if self.hovered and key == 'left mouse down':
            if self.require_key == None or held_keys[self.require_key]:
                self.start_dragging()

        if self.dragging and key == 'left mouse up':
            self.stop_dragging()


    def start_dragging(self):
        point = Vec3(0,0,0)
        if mouse.world_point:
            point = mouse.world_point

        Draggable_Entity._z_plane.world_position = point
        # Draggable_Entity._z_plane.world_position = self.world_position
        Draggable_Entity._z_plane.look_at(Draggable_Entity._z_plane.position - Vec3(*self.plane_direction))
        if self.has_ancestor(camera.ui):
            Draggable_Entity._z_plane.world_parent = camera.ui
        else:
            Draggable_Entity._z_plane.world_parent = scene

        self.start_offset = point - self.world_position
        self.dragging = True
        self.start_pos = self.world_position
        self.collision = False
        Draggable_Entity._z_plane.enabled = True
        mouse._original_traverse_target = mouse.traverse_target
        mouse.traverse_target = Draggable_Entity._z_plane
        if hasattr(self, 'drag'):
            self.drag()


    def stop_dragging(self):
        self.dragging = False
        self.delta_drag = self.world_position - self.start_pos
        Draggable_Entity._z_plane.enabled = False
        self.collision = True
        if hasattr(mouse, '_original_traverse_target'):
            mouse.traverse_target = mouse._original_traverse_target
        else:
            mouse.traverse_target = scene

        if hasattr(self, 'drop'):
            self.drop()

    # def drag(self):
    #     print('start drag test')
    #
    # def drop(self):
    #     print('drop test')

    def update(self):
        if self.dragging:
            if mouse.world_point:
                if not self.lock[0]:
                    self.world_x = mouse.world_point[0] - self.start_offset[0]
                if not self.lock[1]:
                    self.world_y = mouse.world_point[1] - self.start_offset[1]
                if not self.lock[2]:
                    self.world_z = mouse.world_point[2] - self.start_offset[2]

            if self.step[0] > 0:
                hor_step = 1/self.step[0]
                self.x = round(self.x * hor_step) /hor_step
            if self.step[1] > 0:
                ver_step = 1/self.step[1]
                self.y = round(self.y * ver_step) /ver_step
            if self.step[2] > 0:
                dep_step = 1/self.step[2]
                self.z = round(self.z * dep_step) /dep_step

        self.position = (
            clamp(self.x, self.min_x, self.max_x),
            clamp(self.y, self.min_y, self.max_y),
            clamp(self.z, self.min_z, self.max_z)
            )

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        if isinstance(value, (int, float, complex)):
            value = (value, value, value)

        self._step = value