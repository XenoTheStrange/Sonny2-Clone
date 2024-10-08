import ursina as u
from scripts.manager import Cursor

from scripts.mod_utils import after_hook

class test_button(u.Entity):
    def __init__(self, position=(0,0,0), scale=(1,1), parent=u.Default, model=u.Default, texture=None, onclick=(None, None), collider=None, **kwargs):
        super().__init__()
        self.position = position
        self.scale = scale
        self.parent = parent
        self.model = model
        self.texture = texture
        self.onclick = onclick
        self.collider=collider
    def destroy(self):
        self.on_mouse_exit()
        u.destroy(self)
    def input(self, key):
        if self.hovered:
            if self.onclick[0] is not None:
                if key == "left mouse down":
                    self.onclick[0]()
                if key == "right mouse down":
                    self.onclick[1]()
    def on_mouse_exit(self):
        Cursor.texture = "cursor_default"
    def on_mouse_enter(self):
        Cursor.texture = "cursor_fat"

def swap_texture(button):
    if button.texture.name == "sun.png":
        button.texture = "sun_yara"
    else:
        button.texture = "sun"

@after_hook("scenes.language_select.loader")
def my_scene_postfix(entities_list, *args, **kwargs):
    button = test_button(
        position=(0,0.35,-2),
        scale=(0.3,0.3),
        parent=u.camera.ui,
        model="quad",
        texture="sun"
        )
    button.onclick = (lambda:swap_texture(button), lambda:button.destroy())
    button.collider = u.SphereCollider(button, radius=.15)

    #the result passed in is the output of the function we're wrapping,
    #the return value of a loader is the list of entities in that scene, so we can append to it to add our button
    entities_list.append(button)
    return entities_list
