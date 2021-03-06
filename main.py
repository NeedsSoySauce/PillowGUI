from PIL import Image, ImageEnhance, ImageTk
from tkinter import Tk, Menu, Button, Label, Listbox, Canvas, Scrollbar, Toplevel, Scale, END, BooleanVar
from tkinter.filedialog import askopenfilenames, askdirectory
import modifiers
from os import path
from glob import glob
from widgets import FilePane, SliderDialog, ResizeImageDialog, CropImageDialog

# https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#fully-supported-formats
SUPPORTED_FILE_EXTENSIONS = (
                             'bmp', 'dib', 
                             'eps', 'epsf', 'epsi',
                             'gif', 
                             'icns', 
                             'ico', 
                             'im', 
                             'jpg', 'jpeg', 'jpe', 'jif', 'jfif', 'jfi',
                             'jp2', 'j2k', 'jpf', 'jpx', 'jpm', 'mj2',
                             'msp',
                             'pcx',
                             'png',
                             'pbm', 'pgm', 'ppm', 'pnm',
                             '.sgi',
                             'tiff', 'tif',
                             'webp',
                             'xbm'
                             )

class ImageBatch:
    def __init__(self):
        self.filenames = []
        self.modifiers = [] # What modifiers to apply in the order they should be applied
        self.confirmed_mod_count = 0 # Records the number of confirmed modifiers
        self.save_dest = "" # If None we overwrite the original images (TBD)
        self.im_width = 1.0
        self.im_height = 1.0
        self.maintain_aspect_ratio = True
        self.primary_dimension = 'width'
        self.anchor = 'Top'
        self.color = 1.0
        self.contrast = 1.0
        self.brightness = 1.0
        self.sharpness = 1.0

    def select_files(self):
        self.filenames = askopenfilenames()
        if self.filenames:
            self.preview_image = self.filenames[0]

    def select_folders(self):
        # askdirectory only allows one directory to be chosen
        dir_ = askdirectory()
        if dir_:
            self.filenames = []

            # From https://stackoverflow.com/a/40755802/11628429
            for ext in SUPPORTED_FILE_EXTENSIONS:
                self.filenames += glob(dir_ + "/**/*." + ext, recursive=True)

    def select_save_dest(self):
        dir_ = askdirectory()
        if dir_:
            self.save_dest = dir_

    def get_processed_image(self, filename):
        im = Image.open(filename)

        for modifier in self.modifiers:
            im = modifier.apply(im)

        return im

    def process_all(self):
        for filename in self.filenames:
            processed_im = self.get_processed_image(filename)
            outfile = f'{self.save_dest}/{path.split(filename)[1]}'
            processed_im.save(outfile)

    def get_tk_image(self, filename):
        return ImageTk.PhotoImage(self.get_processed_image(filename))

    def confirm_modifier(self):
        self.confirmed_mod_count += 1

    def cancel_modifier(self):
        try:
            del self.modifiers[self.confirmed_mod_count]
        except IndexError:
            pass

    def add_modifier(self, modifier):
        try:
            self.modifiers[self.confirmed_mod_count] = modifier
        except IndexError:
            self.modifiers.append(modifier)

    def set_image_size(self, width, height, maintain_aspect_ratio, primary_dimension='width'):
        self.im_width = width
        self.im_height = height
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.primary_dimension = primary_dimension
        self.add_modifier(modifiers.ResizeModifier(self.im_width, self.im_height, self.maintain_aspect_ratio, primary_dimension=self.primary_dimension))

    def set_image_crop(self, width, height, maintain_aspect_ratio, primary_dimension='width', anchor='Top'):
        self.im_width = width
        self.im_height = height
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.primary_dimension = primary_dimension
        self.anchor = anchor
        modifier = modifiers.CropModifier(self.im_width, self.im_height, self.maintain_aspect_ratio, primary_dimension=self.primary_dimension, anchor=self.anchor)
        self.add_modifier(modifier)

    def set_color(self, value):
        self.color = float(value)
        self.add_modifier(modifiers.ColorModifier(self.color))

    def set_contrast(self, value):
        self.contrast = float(value)
        self.add_modifier(modifiers.ContrastModifier(self.contrast))

    def set_brightness(self, value):
        self.brightness = float(value)
        self.add_modifier(modifiers.BrightnessModifier(self.brightness))

    def set_sharpness(self, value):
        self.sharpness = float(value)
        self.add_modifier(modifiers.SharpnessModifier(self.sharpness))


class GUI:
    def __init__(self):

        self.root = Tk()
        self.root.title("Batch Image Processor")
        self.root.geometry("800x600")
        self.files_selected = False
        self.preview_filename = ""

        self.filepane_open = BooleanVar(value=True)
        self.filepane = FilePane(self.root, on_selection=[self.set_preview], on_close=[self.on_filepane_close])

        self.batch = ImageBatch()

        # Create a toplevel menu (from http://effbot.org/tkinterbook/menu.htm)
        self.menubar = Menu(self.root)

        # Create a pulldown menu, and add it to the menu bar
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open File...", command=self.select_files)
        self.filemenu.add_command(label="Open Folder...", command=self.select_folders)
        self.filemenu.add_command(label="Set save destination", command=self.select_save_dest)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.imagemenu = Menu(self.menubar, tearoff=0)
        self.imagemenu.add_command(label="Resize", command=self.image_resize)
        self.imagemenu.add_command(label="Crop", command=self.image_crop)
        self.menubar.add_cascade(label="Image", menu=self.imagemenu)

        self.adjustmentsmenu = Menu(self.menubar, tearoff=0)
        self.adjustmentsmenu.add_command(label="Color", command=self.adjust_color)
        self.adjustmentsmenu.add_command(label="Contrast", command=self.adjust_contrast)
        self.adjustmentsmenu.add_command(label="Brightness", command=self.adjust_brightness)
        self.adjustmentsmenu.add_command(label="Sharpness", command=self.adjust_sharpness)
        self.menubar.add_cascade(label="Adjustments", menu=self.adjustmentsmenu)

        self.viewmenu = Menu(self.menubar, tearoff=0)
        self.viewmenu.add_checkbutton(label="Files", onvalue=True, offvalue=False, variable=self.filepane_open, command=self.toggle_filepane)
        # self.viewmenu.add_command(label="Files", command=self.adjust_color)
        self.menubar.add_cascade(label="View", menu=self.viewmenu)

        # effectsmenu = Menu(menubar, tearoff=0)
        # effectsmenu.add_command(label="Cut", command=hello)
        # effectsmenu.add_command(label="Copy", command=hello)
        # effectsmenu.add_command(label="Paste", command=hello)
        # menubar.add_cascade(label="Effects", menu=effectsmenu)

        self.menubar.add_command(label=":", state='disabled')
        self.menubar.add_command(label='Run', command=self.batch.process_all)

        # Display the menu
        self.root.config(menu=self.menubar)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.canvas = Canvas(self.root)
        self.canvas.grid(row=0, column=0)
        self.image = None
        self.imagesprite = self.canvas.create_image(0, 0, image=None, anchor='nw')

        self.sbarV = Scrollbar(self.root, orient='vertical')
        self.sbarH = Scrollbar(self.root, orient='horizontal')

        self.sbarV.config(command=self.canvas.yview)
        self.sbarH.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.sbarV.set)
        self.canvas.config(xscrollcommand=self.sbarH.set)

        self.sbarV.grid(row=0, column=1, sticky="ns")
        self.sbarH.grid(row=1, column=0, sticky="ew")

        self.disable_editing()

        self.root.mainloop()

    def toggle_filepane(self):
        if self.filepane_open.get():
            self.filepane.show()
        else:
            self.filepane.hide()

    def on_filepane_close(self):
        self.filepane_open.set(False)

    def enable_editing(self):
        self.menubar.entryconfig("Image", state="normal")
        self.menubar.entryconfig("Adjustments", state="normal")
        self.menubar.entryconfig("Run", state="normal")

    def disable_editing(self):
        self.menubar.entryconfig("Image", state="disabled")
        self.menubar.entryconfig("Adjustments", state="disabled")
        self.menubar.entryconfig("Run", state="disabled")

    def select_files(self):
        self.batch.select_files()

        if self.batch.filenames:
            self.filepane.set_items(self.batch.filenames)
            self.update_preview()
            self.enable_editing()
        else:
            self.disable_editing()

    def select_folders(self):
        self.batch.select_folders()

        if self.batch.filenames:
            self.filepane.set_items(self.batch.filenames)
            self.update_preview()
            self.enable_editing()
        else:
            self.disable_editing()

    def select_save_dest(self):
        self.batch.select_save_dest()

    def set_preview(self, filename):
        self.preview_filename = filename
        self.update_preview()

    def update_preview(self, *args, **kwargs):
        self.image = self.batch.get_tk_image(self.preview_filename)
        self.canvas.itemconfig(self.imagesprite, image=self.image)
        image_size = self.image.width(), self.image.height()
        self.canvas.configure(width=image_size[0], height=image_size[1])
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def setup_dialog(self, dialog, setter):
        dialog.on_change += [setter, self.update_preview]
        dialog.on_cancel += [self.batch.cancel_modifier, self.update_preview]
        dialog.on_confirm += [self.batch.confirm_modifier]

    def image_resize(self):
        width, height = self.image.width(), self.image.height()
        dialog = ResizeImageDialog(self.root, width, height, maintain_aspect_ratio=self.batch.maintain_aspect_ratio, primary_dimension=self.batch.primary_dimension)
        self.setup_dialog(dialog, self.batch.set_image_size)

    def image_crop(self):
        width, height = self.image.width(), self.image.height()
        dialog = CropImageDialog(self.root, width, height, maintain_aspect_ratio=self.batch.maintain_aspect_ratio, primary_dimension=self.batch.primary_dimension, anchor=self.batch.anchor)
        self.setup_dialog(dialog, self.batch.set_image_crop)

    def adjust_color(self):
        dialog = SliderDialog(self.root, 'Adjust Color', self.batch.color, 0, 10.0, 1.0, resolution=0.01)
        self.setup_dialog(dialog, self.batch.set_color)

    def adjust_contrast(self):
        dialog = SliderDialog(self.root, 'Adjust Contrast', self.batch.contrast, 0, 10.0, 1.0, resolution=0.01)
        self.setup_dialog(dialog, self.batch.set_contrast)

    def adjust_brightness(self):
        dialog = SliderDialog(self.root, 'Adjust Brightness', self.batch.brightness, 0, 10.0, 1.0, resolution=0.01)
        self.setup_dialog(dialog, self.batch.set_brightness)

    def adjust_sharpness(self):
        dialog = SliderDialog(self.root, 'Adjust Sharpness', self.batch.sharpness, -10.0, 10.0, 1.0, resolution=0.01)
        self.setup_dialog(dialog, self.batch.set_sharpness)


if __name__ == "__main__":
    root = GUI()

