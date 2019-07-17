from PIL import Image, ImageEnhance, ImageTk
from tkinter import Tk, Menu, Button, Label, Listbox, Canvas, Scrollbar, Toplevel, Scale, END
from tkinter.filedialog import askopenfilenames, askdirectory
import modifiers
from os import path
from glob import glob

class FilePane:
    def __init__(self, root, items=list(), on_selection=None):
        self.items = items
        self.item_count = len(items)
        self.on_selection = on_selection

        self.window = Toplevel()
        self.window.title('Files')
        self.window.transient(root)

        self.menubar = Menu(self.window)
        self.menubar.add_command(label='Previous', command=self.previous)
        self.menubar.add_command(label='Next', command=self.next)

        # Display the menu
        self.window.config(menu=self.menubar)

        self.scrollbar = Scrollbar(self.window, orient='vertical')
        self.listbox = Listbox(self.window, yscrollcommand=self.scrollbar.set)
        self.set_items(items)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(side='left', fill='both', expand=1)

        self.listbox.bind('<<ListboxSelect>>', self.on_select)

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


class SliderDialog:
    def __init__(self, title="Slider Dialog", init_val=0, min_val=-1, max_val=1, default_val=0, on_change=list(), resolution=1, on_confirm=list(), on_cancel=list()):
        self.init_val = init_val
        self.default_val = default_val
        self.on_change = on_change
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.window = Toplevel()
        self.window.title(title)
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