from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image

class LabelButton(ButtonBehavior,Label):
    pass
class ImageButton(ButtonBehavior,Image):
    pass