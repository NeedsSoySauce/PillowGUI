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

class CropModifier(ImageModifier):
    def __init__(self, width, height, maintain_aspect_ratio, primary_dimension='width', anchor='Top'):

        if type(width) != type(height):
            raise TypeError('width and height must be the same type (float or int)')

        self.width = width
        self.height = height
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.primary_dimension = primary_dimension
        self.anchor = anchor

    def apply(self, image):
        im_width, im_height = image.width, image.height
        width, height = self.width, self.height

        # If the image is smaller than one of the dimensions we're trying to crop, we leave that dimension alone

        if isinstance(self.width, float) and isinstance(self.height, float):
            width = round(width * im_width)
            height = round(height * im_height)

        elif self.maintain_aspect_ratio:
            if self.primary_dimension == 'width':
                ratio = im_height / im_width
                height = round(width * ratio)
            else:
                ratio = im_width / im_height
                width = round(height * ratio)

        x_crop = im_width - width
        y_crop = im_height - height
        print(x_crop, y_crop)
        if self.anchor == 'Top Left':
            left_x = 0
            left_y = 0
            right_x = im_width - x_crop
            right_y = im_height - y_crop
        elif self.anchor == 'Top':
            left_x = x_crop / 2
            left_y = 0
            right_x = im_width - (x_crop / 2)
            right_y = im_height - y_crop
        elif self.anchor == 'Top Right':
            left_x = x_crop
            left_y = 0
            right_x = im_width
            right_y = im_height - y_crop
        elif self.anchor == 'Left':
            left_x = 0
            left_y = y_crop / 2
            right_x = im_width - x_crop
            right_y = im_height - (y_crop / 2)
        elif self.anchor == 'Middle':
            left_x = y_crop / 2
            left_y = y_crop / 2
            right_x = im_width - (x_crop / 2)
            right_y = im_height - (y_crop / 2)
        elif self.anchor == 'Right':
            left_x = x_crop
            left_y = y_crop / 2
            right_x = im_width
            right_y = im_height - (y_crop / 2)
        elif self.anchor == 'Bottom Left':
            left_x = 0
            left_y = y_crop
            right_x = im_width - x_crop
            right_y = im_height
        elif self.anchor == 'Bottom':
            left_x = x_crop / 2
            left_y = y_crop
            right_x = im_width - (x_crop / 2)
            right_y = im_height
        else: # 'Bottom Right'
            left_x = x_crop
            left_y = y_crop
            right_x = im_width
            right_y = im_height

        return image.crop((left_x, left_y, right_x, right_y))
