from PIL import ImageEnhance

class ImageModifier:

    """Base class for image modifiers, doesn't really do anything on it's own."""

    def apply(self, image):
        pass

    def __repr__(self):
        return self.__class__.__name__

class ColorModifier(ImageModifier):
    def __init__(self, value):
        self.value = value

    def apply(self, image):
        return ImageEnhance.Color(image).enhance(self.value)

class ContrastModifier(ImageModifier):
    def __init__(self, value):
        self.value = value

    def apply(self, image):
        return ImageEnhance.Contrast(image).enhance(self.value)

class BrightnessModifier(ImageModifier):
    def __init__(self, value):
        self.value = value

    def apply(self, image):

        enhanced_im = ImageEnhance.Brightness(image)
        enhanced_im = enhanced_im.enhance(self.value)

        return enhanced_im

class SharpnessModifier(ImageModifier):
    def __init__(self, value):
        self.value = value

    def apply(self, image):
        return ImageEnhance.Sharpness(image).enhance(self.value)
