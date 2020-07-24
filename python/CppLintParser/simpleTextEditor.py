import tkinter as tk
from tkinter import filedialog
import platform
from functools import partial
import re
import tkinter.messagebox as msg


class FindPopup(tk.Toplevel):

    def __init__(self, master):
        super().__init__()

        self.master = master

        self.title("Find in file")
        self.center_window()

        self.transient(master)

        self.matches_are_highlighted = False

        self.main_frame = tk.Frame(self, bg="lightgrey")
        self.button_frame = tk.Frame(self.main_frame, bg="lightgrey")

        self.find_label = tk.Label(
            self.main_frame, text="Find: ", bg="lightgrey", fg="black")
        self.find_entry = tk.Entry(self.main_frame, bg="white", fg="black")
        self.find_button = tk.Button(
            self.button_frame,
            text="Find All",
            bg="lightgrey",
            fg="black",
            command=self.find)
        self.next_button = tk.Button(
            self.button_frame,
            text="Next",
            bg="lightgrey",
            fg="black",
            command=self.jump_to_next_match)
        self.cancel_button = tk.Button(
            self.button_frame,
            text="Cancel",
            bg="lightgrey",
            fg="black",
            command=self.cancel)

        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.find_button.pack(side=tk.LEFT, pady=(0, 10), padx=(20, 20))
        self.next_button.pack(side=tk.LEFT, pady=(0, 10), padx=(15, 20))
        self.cancel_button.pack(side=tk.LEFT, pady=(0, 10), padx=(15, 0))
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.find_label.pack(side=tk.LEFT, fill=tk.X, padx=(20, 0))
        self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=(0, 20))

        self.find_entry.focus_force()
        self.find_entry.bind("<Return>", self.jump_to_next_match)
        self.find_entry.bind("<KeyRelease>", self.matches_are_not_highlighted)
        self.bind("<Escape>", self.cancel)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def find(self, event=None):
        text_to_find = self.find_entry.get()
        if text_to_find and not self.matches_are_highlighted:
            self.master.remove_all_find_tags()
            self.master.highlight_matches(text_to_find)
            self.matches_are_highlighted = True

    def jump_to_next_match(self, event=None):
        text_to_find = self.find_entry.get()
        if text_to_find:
            if not self.matches_are_highlighted:
                self.find()
            self.master.next_match()

    def cancel(self, event=None):
        self.master.remove_all_find_tags()
        self.destroy()

    def matches_are_not_highlighted(self, event):
        key_pressed = event.keysym
        if not key_pressed == "Return":
            self.matches_are_highlighted = False

    def center_window(self):
        master_pos_x = self.master.winfo_x()
        master_pos_y = self.master.winfo_y()

        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()

        my_width = 300
        my_height = 100

        pos_x = (master_pos_x + (master_width // 2)) - (my_width // 2)
        pos_y = (master_pos_y + (master_height // 2)) - (my_height // 2)

        geometry = "{}x{}+{}+{}".format(my_width, my_height, pos_x, pos_y)
        self.geometry(geometry)


class Editor(tk.Tk):

    def __init__(self):
        super().__init__()

        self.initCtrlKeyName()

        self.FONT_SIZE = 12
        self.WINDOW_TITLE = "Text Editor"

        # the path of cur file
        self.open_file = ""
        self.is_saved = False

        self.title(self.WINDOW_TITLE)
        self.geometry("800x600")

        self.menubar = tk.Menu(self, bg="lightgrey", fg="black")

        self.file_menu = tk.Menu(
            self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(
            label="New",
            command=self.file_new,
            accelerator="%s+N" % (self.ctrlKeyName))
        self.file_menu.add_command(
            label="Open",
            command=self.file_open,
            accelerator="%s+O" % (self.ctrlKeyName))
        self.file_menu.add_command(
            label="Save",
            command=self.file_save,
            accelerator="%s+S" % (self.ctrlKeyName))

        self.edit_menu = tk.Menu(
            self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.edit_menu.add_command(
            label="Cut",
            command=self.edit_cut,
            accelerator="%s+X" % (self.ctrlKeyName))
        self.edit_menu.add_command(
            label="Paste",
            command=self.edit_paste,
            accelerator="%s+V" % (self.ctrlKeyName))
        self.edit_menu.add_command(
            label="Undo",
            command=self.edit_undo,
            accelerator="%s+Z" % (self.ctrlKeyName))
        self.edit_menu.add_command(
            label="Redo",
            command=self.edit_redo,
            accelerator="%s+Y" % (self.ctrlKeyName))

        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

        self.configure(menu=self.menubar)

        self.line_numbers = tk.Text(self, bg="lightgrey", fg="black", width=6)
        self.line_numbers.insert("end", "1\n")
        self.line_numbers.configure(state="disabled")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.line_numbers.bind("<MouseWheel>", self.skip_event)
        self.line_numbers.bind("<Button-4>", self.skip_event)
        self.line_numbers.bind("<Button-5>", self.skip_event)

        self.main_text = tk.Text(
            self,
            bg="white",
            fg="black",
            font=("Ubuntu Mono", self.FONT_SIZE),
            undo=True)
        self.main_text.pack(expand=1, fill=tk.BOTH)
        self.main_text.bind("<Tab>", self.insert_spaces)
        set_unsaved_flag = partial(self.updateTitle, is_saved=False)
        self.main_text.bind("<Key>", set_unsaved_flag)
        self.main_text.bind("<KeyRelease>", self.update_line_numbers)
        self.main_text.bind("<MouseWheel>", self.scroll_text_and_line_numbers)
        self.main_text.bind("<Button-4>", self.scroll_text_and_line_numbers)
        self.main_text.bind("<Button-5>", self.scroll_text_and_line_numbers)
        self.main_text.tag_config("findmatch", background="yellow")

        self.bind("<%s-a>" % (self.ctrlKeyName), self.select_all)
        self.bind("<%s-f>" % (self.ctrlKeyName), self.show_find_window)
        self.bind("<Control-v>", self.edit_paste)

        self.bind("<%s-s>" % (self.ctrlKeyName), self.file_save)
        self.bind("<%s-o>" % (self.ctrlKeyName), self.file_open)
        self.bind("<%s-n>" % (self.ctrlKeyName), self.file_new)

    def scroll_text_and_line_numbers(self, *args):
        #from mouse MouseWheel
        event = args[0]
        if event.delta:
            move = -1 * (event.delta / 120)
            if (move < 0 and int(move) == 0):
                move = -1
            elif (move > 0 and int(move) == 0):
                move = 1
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1
        self.main_text.yview_scroll(int(move), "units")
        self.line_numbers.yview_scroll(int(move), "units")
        return "break"

    def skip_event(self, event=None):
        return "break"

    def edit_cut(self, event=None):
        self.main_text.event_generate("<<Cut>>")
        self.updateTitle(None, False)
        return "break"

    def edit_paste(self, event=None):
        self.main_text.event_generate("<<Paste>>")
        self.updateTitle(None, False)
        self.update_line_numbers()
        return "break"

    def edit_undo(self, event=None):
        self.main_text.event_generate("<<Undo>>")
        self.updateTitle(None, False)
        return "break"

    def edit_redo(self, event=None):
        self.main_text.event_generate("<<Redo>>")
        self.updateTitle(None, False)
        return "break"

    def initCtrlKeyName(self):
        os = platform.system()
        if os == "Darwin":
            self.ctrlKeyName = "Command"
        else:
            self.ctrlKeyName = "Control"

    def file_new(self, event=None):
        file_name = filedialog.asksaveasfilename()
        self.open_file = file_name
        self.main_text.delete(1.0, tk.END)

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

            self.update_line_numbers()
            self.updateTitle()

    def file_save(self, event=None):
        if not self.open_file:
            new_file_name = filedialog.asksaveasfilename()
            if new_file_name:
                self.open_file = new_file_name

        if self.open_file:
            new_contents = self.main_text.get(1.0, tk.END)
            with open(self.open_file, "w") as open_file:
                open_file.write(new_contents)
            self.updateTitle()

    def select_all(self, event=None):
        self.main_text.tag_add("sel", 1.0, tk.END)
        return "break"

    # tab == four spaces
    def insert_spaces(self, event=None):
        self.main_text.insert(tk.INSERT, "    ")
        return "break"

    def updateTitle(self, event=None, is_saved=False):
        if event:  # call by key event, should set unsaved
            self.is_saved = is_saved
        else:  # call by operation such as open/new file
            self.is_saved = True
        savedFlag = ''
        if not self.is_saved:
            savedFlag = ' *'
        if self.open_file:
            self.title(
                " - ".join([self.WINDOW_TITLE, self.open_file]) + savedFlag)

    def update_line_numbers(self, event=None):
        self.line_numbers.configure(state="normal")
        # get real line num
        # the last num line must be a single '\n'
        old_num_of_lines = int(self.line_numbers.index(
            tk.END).split(".")[0]) - 1
        cur_number_of_lines = int(self.main_text.index(
            tk.END).split(".")[0])
        offset = cur_number_of_lines - old_num_of_lines
        # calculate offset
        if (offset == 0):
            return
        if (offset > 0):
            # insert content such as "2\n3\n" ....
            line_number_string = "".join(
                str(num) + '\n'
                for num in range(old_num_of_lines, cur_number_of_lines))
            self.line_numbers.insert("end", line_number_string)
        if (offset < 0):
            for _ in range((-offset)):
                line_number_string = self.line_numbers.get("end-1l", "end")
                # fix bug about cur_line only contain a '\n'
                if line_number_string == "\n":
                    self.line_numbers.delete("end-1l", "end")
                self.line_numbers.delete("end-1l", "end")
            # add '\n' into num line
            self.line_numbers.insert("end", "\n")
        self.line_numbers.configure(state="disabled")

    def show_find_window(self, event=None):
        FindPopup(self)

    def highlight_matches(self, text_to_find):
        self.main_text.tag_remove("findmatch", 1.0, tk.END)
        self.match_coordinates = []
        self.current_match = -1

        find_regex = re.compile(text_to_find)
        search_text_lines = self.main_text.get(1.0, tk.END).split("\n")

        for line_number, line in enumerate(search_text_lines):
            line_number += 1
            for match in find_regex.finditer(line):
                start, end = match.span()
                start_index = ".".join([str(line_number), str(start)])
                end_index = ".".join([str(line_number), str(end)])
                self.main_text.tag_add("findmatch", start_index, end_index)
                self.match_coordinates.append((start_index, end_index))

    def next_match(self, event=None):
        try:
            current_target, current_target_end = self.match_coordinates[
                self.current_match]
            self.main_text.tag_remove("sel", current_target, current_target_end)
            self.main_text.tag_add("findmatch", current_target,
                                   current_target_end)
        except IndexError:
            pass

        try:
            self.current_match = self.current_match + 1
            next_target, target_end = self.match_coordinates[self.current_match]
        except IndexError:
            if len(self.match_coordinates) == 0:
                msg.showinfo("No Matches", "No Matches Found")
            else:
                if msg.askyesno("Wrap Search?",
                                "Reached end of file. Continue from the top?"):
                    self.current_match = -1
                    self.next_match()
        else:
            self.main_text.mark_set(tk.INSERT, next_target)
            self.main_text.tag_remove("findmatch", next_target, target_end)
            self.main_text.tag_add("sel", next_target, target_end)
            self.main_text.see(next_target)

    def remove_all_find_tags(self):
        self.main_text.tag_remove("findmatch", 1.0, tk.END)
        self.main_text.tag_remove("sel", 1.0, tk.END)


if __name__ == "__main__":
    editor = Editor()
    editor.mainloop()
