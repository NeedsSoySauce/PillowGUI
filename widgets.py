from PIL import Image, ImageEnhance, ImageTk
from tkinter import Tk, Menu, Button, Label, Listbox, Canvas, Scrollbar, Toplevel, Scale, END, Checkbutton, Radiobutton, StringVar, IntVar, Entry, Spinbox, OptionMenu
from tkinter.filedialog import askopenfilenames, askdirectory
import modifiers
from os import path
from glob import glob

class FilePane:
    def __init__(self, root, items=list(), on_selection=list(), on_close=list()):
        self.items = items
        self.item_count = len(items)
        self.on_selection = on_selection
        self.on_close = on_close

        self.window = Toplevel()
        self.window.title('Files')
        self.window.transient(root)
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.menubar = Menu(self.window)
        self.menubar.add_command(label='Previous', command=self.previous)
        self.menubar.add_command(label='Next', command=self.next)

        # Display the menu
        self.window.config(menu=self.menubar)

        self.scrollbar = Scrollbar(self.window, orient='vertical')
        self.listbox = Listbox(self.window, yscrollcommand=self.scrollbar.set, exportselection=False)
        self.set_items(items)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(side='left', fill='both', expand=1)

        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_window_close(self):
        for callback in self.on_close:
            callback()
        self.window.withdraw()

    def hide(self):
        self.window.withdraw()

    def show(self):
        self.window.deiconify()

    def selected_item(self):
        return self.items[self.listbox.curselection()[0]]

    def select_index(self, index):
        self.listbox.selection_clear(0, END)

        # From https://stackoverflow.com/a/25451279/11628429
        self.listbox.select_set(index) #This only sets focus on the first item. 
        self.listbox.event_generate("<<ListboxSelect>>")

    def set_items(self, items):
        self.items = items
        self.item_count = len(items)
        self.listbox.delete(0, END)

        for item in items:
            item = path.split(item)[1]
            self.listbox.insert(END, item)
        
        self.select_index(0)

    def previous(self):
        index = self.listbox.curselection()[0] - 1
        if index < 0:
            index = self.item_count - 1
        self.select_index(index)

    def next(self):
        index = self.listbox.curselection()[0] + 1
        if index >= self.item_count:
            index = 0
        self.select_index(index)

    def on_select(self, event):
        if self.on_selection:
            for callback in self.on_selection:
                callback(self.selected_item())

class CustomDialog:
    def __init__(self, on_change=list(), on_cancel=list(), on_confirm=list()):
        self.on_change = on_change
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.window = Toplevel()

    def on_update(self, value):
        for callback in self.on_change:
            callback(value)

    def cancel(self):
        for callback in self.on_cancel:
            callback()
        self.window.destroy()

    def confirm(self):
        for callback in self.on_confirm:
            callback()
        self.window.destroy()

class SliderDialog(CustomDialog):
    def __init__(self, root, title="Slider Dialog", init_val=0, min_val=-1, max_val=1, default_val=0, on_change=list(), resolution=1, on_confirm=list(), on_cancel=list()):
        self.init_val = init_val
        self.default_val = default_val
        self.on_change = on_change
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.window = Toplevel()
        self.window.title(title)
        self.window.transient(root)
        self.window.grab_set()

        self.scale = Scale(self.window, orient='horizontal', from_=min_val, to=max_val, command=self.on_update, resolution=resolution)
        self.scale.set(init_val)
        self.scale.grid(row=0, column=0, sticky='nesw')

        self.cancel_button = Button(self.window, text='Cancel', command=self.cancel)
        self.cancel_button.grid(row=1, column=0)

        self.reset_button = Button(self.window, text='Reset', command=self.reset)
        self.reset_button.grid(row=1, column=1)

        self.confirm_button = Button(self.window, text='Confirm', command=self.confirm)
        self.confirm_button.grid(row=1, column=2)

    def on_update(self, value):
        for callback in self.on_change:
            callback(value)

    def cancel(self):
        for callback in self.on_cancel:
            callback()
        self.on_change[0](self.init_val) # hardcoded atm, so assumes the set method is first (good enough for now)
        self.window.destroy()

    def reset(self):
        self.scale.set(self.default_val)

    def confirm(self):
        for callback in self.on_confirm:
            callback()
        self.window.destroy()

class ResizeImageDialog(CustomDialog):
    def __init__(self, root, width, height, maintain_aspect_ratio=False, primary_dimension='width', title="Resize", on_change=list(), on_cancel=list(), on_confirm=list(), **kwargs):
        self.init_width = width
        self.init_height = height
        self.init_maintain_aspect_ratio = maintain_aspect_ratio
        self.init_primary_dimension = primary_dimension
        self.on_change = on_change
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.window = Toplevel()
        self.window.title(title)
        self.window.transient(root)
        self.window.grab_set()

        self.primary_dimension = StringVar()
        self.primary_dimension.set(primary_dimension)

        self.resize_mode = StringVar()
        self.resize_mode.set('percentage')

        self.resize_percentage = IntVar()
        self.resize_percentage.set(100.0)

        self.resize_width = IntVar()
        self.resize_width.set(width)
        self.resize_height = IntVar()
        self.resize_height.set(height)

        self.maintain_aspect_ratio = IntVar()

        # See https://stackoverflow.com/a/4140988/11628429
        self.vcmd_is_float = (self.window.register(self.is_float), '%P')
        self.vcmd_is_int = (self.window.register(self.is_int), '%P')

        self.percentage_radiobutton = Radiobutton(self.window, text='By percentage', value='percentage', variable=self.resize_mode, command=self.set_mode)
        self.percentage_radiobutton.grid(row=0, column=0)

        self.percentage_entry = Spinbox(self.window, from_=0, to=float('inf'), textvariable=self.resize_percentage, validate='all', validatecommand=self.vcmd_is_float)
        self.percentage_entry.grid(row=0, column=1)

        self.absolute_radiobutton = Radiobutton(self.window, text='By absolute value', value='absolute', variable=self.resize_mode, command=self.set_mode)
        self.absolute_radiobutton.grid(row=2, column=0)

        self.ratio_checkbox = Checkbutton(self.window, text='Maintain aspect ratio', variable=self.maintain_aspect_ratio, command=self.ratio_change)
        self.ratio_checkbox.grid(row=3, column=0)

        self.width_label = Label(self.window, text='Width')
        self.width_label.grid(row=5, column=0)

        self.width_entry = Spinbox(self.window, from_=0, to=float('inf'), textvariable=self.resize_width, validate='all', validatecommand=self.vcmd_is_int) # needs a command to respect aspect ratio on change
        self.width_entry.grid(row=5, column=1)

        self.height_label = Label(self.window, text='Height')
        self.height_label.grid(row=6, column=0)

        self.height_entry = Spinbox(self.window, from_=0, to=float('inf'), textvariable=self.resize_height, validate='all', validatecommand=self.vcmd_is_int)
        self.height_entry.grid(row=6, column=1)

        self.cancel_button = Button(self.window, text='Cancel', command=self.cancel)
        self.cancel_button.grid(row=9, column=0)

        self.reset_button = Button(self.window, text='Reset', command=self.reset)
        self.reset_button.grid(row=9, column=1)

        self.confirm_button = Button(self.window, text='Confirm', command=self.confirm)
        self.confirm_button.grid(row=9, column=2)

        self.resize_percentage.trace('w', self.on_percentage_change)
        self.resize_width_trace_id = self.resize_width.trace('w', self.on_width_change)
        self.resize_height_trace_id = self.resize_height.trace('w', self.on_height_change)
        self.set_mode()

    def set_resize_width_without_trace(self, value):
        if not isinstance(value, int):
            raise TypeError('height should be an int')
        self.resize_width.trace_vdelete("w", self.resize_width_trace_id)
        self.resize_width.set(value)
        self.resize_width_trace_id = self.resize_width.trace('w', self.on_width_change)

    def set_resize_height_without_trace(self, value):
        if not isinstance(value, int):
            raise TypeError('width should be an int')
        self.resize_height.trace_vdelete("w", self.resize_height_trace_id)
        self.resize_height.set(value)
        self.resize_height_trace_id = self.resize_height.trace('w', self.on_height_change)

    def on_update(self, *args):
        mode = self.resize_mode.get()
        for callback in self.on_change:
            if mode == 'percentage':
                percentage = self.resize_percentage.get() / 100
                callback(percentage, percentage, self.maintain_aspect_ratio.get(), self.primary_dimension.get())
            else:
                callback(self.resize_width.get(), self.resize_height.get(), self.maintain_aspect_ratio.get(), self.primary_dimension.get())

    def on_percentage_change(self, *args):
        self.on_update()

    def on_width_change(self, *args):
        self.primary_dimension.set('width')
        if self.maintain_aspect_ratio.get():
            self.set_resize_height_without_trace(round(self.init_height * (self.resize_width.get() / self.init_width)))
        self.on_update()

    def on_height_change(self, *args):
        self.primary_dimension.set('height')
        if self.maintain_aspect_ratio.get():
            self.set_resize_width_without_trace(round(self.init_width * (self.resize_height.get() / self.init_height)))
        self.on_update()

    def reset(self):
        self.resize_percentage.set(100.0)
        self.set_resize_width_without_trace(self.init_width)
        self.set_resize_height_without_trace(self.init_height)
        self.maintain_aspect_ratio.set(self.init_maintain_aspect_ratio)
        self.primary_dimension.set(self.init_primary_dimension)
        self.on_update()

    def set_mode(self):
        mode = self.resize_mode.get()
        if mode == 'percentage':
            self.percentage_entry.config(state='normal')
            self.ratio_checkbox.config(state='disabled')
            self.width_label.config(state='disabled')
            self.width_entry.config(state='disabled')
            self.height_label.config(state='disabled')
            self.height_entry.config(state='disabled')
        else:
            self.percentage_entry.config(state='disabled')
            self.ratio_checkbox.config(state='normal')
            self.width_label.config(state='normal')
            self.width_entry.config(state='normal')
            self.height_label.config(state='normal')
            self.height_entry.config(state='normal')

    def is_float(self, P):
        try:
            float(P)
            return True
        except ValueError:
            return False

    def is_int(self, P):
        return str.isdecimal(P)

    def ratio_change(self):
        if self.maintain_aspect_ratio.get():
            if self.primary_dimension.get() == 'width':
                self.set_resize_height_without_trace(round(self.init_height * (self.resize_width.get() / self.init_width)))
            else:
                self.set_resize_width_without_trace(round(self.init_width * (self.resize_height.get() / self.init_height)))             
            self.on_update()
        print(self.maintain_aspect_ratio.get())
        
        print('w', self.resize_width.get())
        print('h', self.resize_height.get())

class CropImageDialog(ResizeImageDialog):
    def __init__(self, *args, **kwargs):
        kwargs['title'] = 'Crop'
        super().__init__(*args, **kwargs)

        anchors = ['Top Left', 'Top', 'Top Right', 'Left', 'Middle', 'Right', 'Bottom Left', 'Bottom', 'Bottom Right']
        self.anchor = StringVar()
        self.anchor.set(anchors[0])

        self.anchor_label = Label(self.window, text='Anchor')
        self.anchor_label.grid(row=8, column=0)

        self.anchor_option_menu = OptionMenu(self.window, self.anchor, anchors[0], *anchors[1:])
        self.anchor_option_menu.grid(row=8, column=1)

        self.anchor.trace('w', self.on_update)

    def on_update(self, *args):
        mode = self.resize_mode.get()
        for callback in self.on_change:
            if mode == 'percentage':
                percentage = self.resize_percentage.get() / 100
                callback(percentage, percentage, self.maintain_aspect_ratio.get(), self.primary_dimension.get(), self.anchor.get())
            else:
                callback(self.resize_width.get(), self.resize_height.get(), self.maintain_aspect_ratio.get(), self.primary_dimension.get(), self.anchor.get())