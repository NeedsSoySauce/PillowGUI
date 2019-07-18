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

class ResizeModifier(ImageModifier):
    def __init__(self, width, height, maintain_aspect_ratio, primary_dimension='width'):

        if type(width) != type(height):
            raise TypeError('width and height must be the same type (float or int)')

        self.width = width
        self.height = height
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.primary_dimension = primary_dimension

    def apply(self, image):
        im_width, im_height = image.width, image.height

        if isinstance(self.width, float) and isinstance(self.height, float):
            self.width = round(self.width * im_width)
            self.height = round(self.height * im_height)

        elif self.maintain_aspect_ratio:
            if self.primary_dimension == 'width':
                ratio = im_height / im_width
                self.height = round(self.width * ratio)
            else:
                ratio = im_width / im_height
                self.width = round(self.height * ratio)

        return image.resize((self.width, self.height))
