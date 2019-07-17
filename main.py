from PIL import Image, ImageEnhance, ImageTk
from tkinter import Tk, Menu, Button, Label, Listbox, Canvas, Scrollbar, Toplevel, Scale
from tkinter.filedialog import askopenfilenames, askdirectory

class ImageBatch:
    def __init__(self):
        self.filenames = ()
        self.actions = [] # What actions to take in the order they should be done
        self.save_dest = "" # If None we overwrite the original images
        self.brightness = 1.0

    def select_files(self):
        self.filenames = askopenfilenames()
        if self.filenames:
            self.preview_image = self.filenames[0]

    def select_folders(self):
        # askdirectory only allows one directory to be chosen
        self.filenames = askdirectory()

    def select_save_dest(self):
        self.save_dest = askdirectory()

    def get_processed_image(self, filename):
        im = Image.open(filename)
        enhancement = ImageEnhance.Brightness(im)
        enhanced_im = enhancement.enhance(self.brightness)
        return enhanced_im

    def process_all(self):
        for filename in self.filenames:
            enhanced_im = self.get_processed_image(filename)
            enhanced_im.save('output.png')

    def set_brightness(self, value):
        self.brightness = float(value) / 100
        if self.brightness and 'brightness' not in self.actions:
            self.actions.append('brightness')
        else:
            try:
                self.actions.remove('brightness')
            except ValueError:
                pass

    def get_tk_image(self, index=0):
        return ImageTk.PhotoImage(self.get_processed_image(self.filenames[index]))

class SliderDialog:
    def __init__(self, title="Slider Dialog", init_val=0, min_val=-1, max_val=1, default_val=0, callbacks=list()):
        self.window = Toplevel()
        self.window.title(title)
        self.init_val = init_val
        self.default_val = default_val
        self.callbacks = callbacks

        self.scale = Scale(self.window, orient='horizontal', from_=min_val, to=max_val, command=self.on_change)
        self.scale.set(init_val)
        self.scale.grid(row=0, column=0, sticky='nesw')

        self.cancel_button = Button(self.window, text='Cancel', command=self.cancel)
        self.cancel_button.grid(row=1, column=0)

        self.reset_button = Button(self.window, text='Reset', command=self.reset)
        self.reset_button.grid(row=1, column=1)

        self.confirm_button = Button(self.window, text='Confirm', command=self.confirm)
        self.confirm_button.grid(row=1, column=2)

    def on_change(self, value):
        for callback in self.callbacks:
            callback(value)

    def cancel(self):
        self.on_change(self.init_val)
        self.window.destroy()

    def reset(self):
        self.scale.set(self.default_val)

    def confirm(self):
        self.window.destroy()

class GUI:
    def __init__(self):

        self.root = Tk()
        self.root.title("Batch Image Processor")
        self.root.geometry("800x600")
        self.filename_index = 0
        self.files_selected = False

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

        self.adjustmentsmenu = Menu(self.menubar, tearoff=0)
        self.adjustmentsmenu.add_command(label="Color", command=hello)
        self.adjustmentsmenu.add_command(label="Contrast", command=hello)
        self.adjustmentsmenu.add_command(label="Brightness", command=self.adjust_brightness)
        self.adjustmentsmenu.add_command(label="Sharpness", command=hello)
        self.menubar.add_cascade(label="Adjustments", menu=self.adjustmentsmenu)

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

    def enable_editing(self):
        self.menubar.entryconfig("Adjustments", state="normal")
        self.menubar.entryconfig("Run", state="normal")

    def disable_editing(self):
        self.menubar.entryconfig("Adjustments", state="disabled")
        self.menubar.entryconfig("Run", state="disabled")

    def select_files(self):
        self.batch.select_files()
        self.update_preview()

        if self.batch.filenames:
            self.enable_editing()
        else:
            self.disable_editing()

    def select_folders(self):
        self.batch.select_folders()
        self.update_preview()

        if self.batch.filenames:
            self.enable_editing()
        else:
            self.disable_editing()

    def select_save_dest(self):
        self.batch.select_save_dest()
        self.update_preview()

    def update_preview(self, *args, **kwargs):
        self.image = self.batch.get_tk_image(self.filename_index)
        self.canvas.itemconfig(self.imagesprite, image=self.image)
        image_size = self.image.width(), self.image.height()
        self.canvas.configure(width=image_size[0], height=image_size[1])
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def adjust_brightness(self):
        dialog = SliderDialog('Adjust Brightness', self.batch.brightness * 100, 0, 200, 100)
        dialog.callbacks = [self.batch.set_brightness, self.update_preview]



def hello():
    print('TBD')

if __name__ == "__main__":

    root = GUI()

