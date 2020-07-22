import tkinter as tk
from tkinter import Event, filedialog
import platform
from functools import partial

# from https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.ctrlKeyName = ""
        self.assignCtrlKeyName()

        self.FONT_SIZE = 12
        self.WINDOW_TITLE = "Text Editor"

        # the path of cur file
        self.open_file = ""
        self.is_saved = False

        self.title(self.WINDOW_TITLE)
        self.geometry("800x600")
  
        self.menubar = tk.Menu(self, bg="lightgrey", fg="black")
        self.file_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(label="New", command=self.file_new, accelerator="%s+N" % (self.ctrlKeyName))
        self.file_menu.add_command(label="Open", command=self.file_open, accelerator="%s+O" % (self.ctrlKeyName))
        self.file_menu.add_command(label="Save", command=self.file_save, accelerator="%s+S" % (self.ctrlKeyName))

        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.configure(menu=self.menubar)

        self.main_text = CustomText(self, bg="white", fg="black", font=("Ubuntu Mono", self.FONT_SIZE))

        self.main_text.pack(expand=1, fill=tk.BOTH)
        self.main_text.bind("<Tab>", self.insert_spaces)
        set_unsaved_flag = partial(self.set_saved_flag, is_saved=False)
        self.main_text.bind("<<TextModified>>", set_unsaved_flag)

        self.bind("<%s-s>" % (self.ctrlKeyName), self.file_save)
        self.bind("<%s-o>" % (self.ctrlKeyName), self.file_open)
        self.bind("<%s-n>" % (self.ctrlKeyName), self.file_new)

    def assignCtrlKeyName(self):
        os = platform.system()
        if os == "Darwin":
            self.ctrlKeyName = "Command"
        else:
            self.ctrlKeyName = "Control"
        
    def file_new(self, event=None):
        file_name = filedialog.asksaveasfilename()
        self.open_file = file_name
        self.main_text.delete(1.0, tk.END)
        self.set_saved_flag(None, True)

    def file_open(self, event=None):
        file_to_open = filedialog.askopenfilename()

        if file_to_open:
            self.open_file = file_to_open
            self.main_text.delete(1.0, tk.END)

            with open(file_to_open, "r") as file_contents:
                file_lines = file_contents.readlines()
                if len(file_lines) > 0:
                    for index, line in enumerate(file_lines):
                        index = float(index) + 1.0
                        self.main_text.insert(index, line)
            
            self.set_saved_flag(None, True)

    def file_save(self, event=None):
        if not self.open_file:
            new_file_name = filedialog.asksaveasfilename()
            if new_file_name:
                self.open_file = new_file_name

        if self.open_file:
            new_contents = self.main_text.get(1.0, tk.END)
            with open(self.open_file, "w") as open_file:
                open_file.write(new_contents)
        self.set_saved_flag(None,True)

    # tab == four spaces
    def insert_spaces(self, event=None):
        self.main_text.insert(tk.INSERT, "    ")
        return "break"

    def set_saved_flag(self,event=None,is_saved=False):
        self.is_saved = is_saved
        savedFlag = ''
        if not self.is_saved:
            savedFlag = ' *'
        if self.open_file:
            self.title(" - ".join([self.WINDOW_TITLE, self.open_file]) + savedFlag)

if __name__ == "__main__":
    editor = Editor()
    editor.mainloop()