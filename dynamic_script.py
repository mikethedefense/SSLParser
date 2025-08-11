from tkinter import *
# --- App structure ---
# Tk (root window)
# └── container Frame
#     ├── InitPage Frame
#     └── TestCreationPage Frames

# TODO: convert the rules to SSL scripting and save to txt file
# TODO: add defined variables data to csv file

class App: # Master Controller
    def __init__(self,master):
        self.master = master
        master.title('AutoScript')
        master.geometry('700x700')
        master.resizable(True, True)

        self.container = Frame(master)
        self.container.pack(fill = 'both', expand = True)
        page_init_frame = InitPage(self.container, self)
        self.frames = {'InitPage': page_init_frame}
        page_init_frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame('InitPage')


    def show_frame(self,page_name):
        frame = self.frames[page_name]
        frame.tkraise()





class InitPage(Frame):
    def __init__(self,parent, controller): # the parent is the frame
        super().__init__(parent)
        self.controller = controller
        self.config_num = IntVar()
        self.init_btn = Button(self, text="Create Test Procedure", command = self.init_btn_pressed)
        self.init_btn.grid(row=0, column=0)
        self.config_label = Label(self, text='Enter # of Configs')
        self.config_entry = Entry(self, textvariable =self.config_num)
        self.submit_btn = Button(self, text = 'Submit', command = self.submit)

    def init_btn_pressed(self):
        self.init_btn.destroy()
        self.config_label.grid(row=0, column = 0)
        self.config_entry.grid(row = 0, column = 1, padx=5, pady=5)
        self.submit_btn.grid(row = 1, column = 0)

    def submit(self): # go to test creation page
        total = self.config_num.get()
        for i in range(total):
            self.controller.frames[f'Config{i}'] = TestCreationPage(self.controller.container, self.controller,i, total)
            self.controller.frames[f'Config{i}'].grid(row = 0, column = 0,sticky='nsew')
        self.controller.show_frame('Config0')


class TestCreationPage(Frame):
    def __init__(self, parent, controller, index, total):
        super().__init__(parent)
        self.controller = controller
        self.index = index
        self.total = total
        self.rule_btn = Button(self, text = 'Add Rule', command = self.add_rule)
        self.rule_btn.grid(row=1, column=0)
        self.row_counter = IntVar()
        self.row_counter.set(1)
        self.config_label = Label(self, text = f'Config {self.index + 1}', font = ('arial', 20), pady = 5)
        self.config_label.grid(row = 0, column = 0)

        # Config Pages Cycling

        if index < total - 1:
            self.next_btn = Button(self, text = 'Next Config', command = lambda: self.controller.show_frame(f'Config{index + 1}'))
            self.next_btn.grid(row = 99, column = 10)
        else:
            self.next_btn = Button(self, text = 'Generate SSL Script', command = lambda: self.finish)
            self.next_btn.grid(row=99, column=10)


    def add_rule(self,*args):
        rule = _RulesFrame(self)
        rule.rule_frame.grid(row=self.row_counter.get(), column=0)
        self.rule_btn.grid(row = self.row_counter.get() + 1, column = 0)
        self.row_counter.set(self.row_counter.get() + 1)
    def finish(self):
        pass

class _RulesFrame:
    def __init__(self,controller):
        self.controller = controller

        # Variables
        options = ['Takeoff', 'Set']
        self.selected_option = StringVar()
        self.alt_entry_variable = IntVar()
        self.pitch_entry_variable = IntVar()
        self.signal_entry_variable = StringVar()
        self.sig_val_entry_variable = IntVar()

        # Frame Defined
        self.rule_frame = Frame(controller)

        # Labels and entries to use (more can be added)
        self.selector = OptionMenu(self.rule_frame, self.selected_option, *options)
        self.selector.grid(row=0, column=0)

        self.v_rot_entry = Entry(self.rule_frame)
        self.knots_label = Label(self.rule_frame, text = 'Knots')
        self.pitch_label = Label(self.rule_frame, text = 'Degrees')
        self.pitch_entry = Entry(self.rule_frame)
        self.signal_entry = Entry(self.rule_frame, textvariable = self.signal_entry_variable)
        self.sig_val_entry = Entry(self.rule_frame, textvariable = self.sig_val_entry_variable)
        self.del_btn = Button(self.rule_frame, text = 'Delete', command = self.delete_rule)

        # Trace
        self.selected_option.trace_add('write', callback = self.selector_callback)

    def selector_callback(self, *args):
        self.del_btn.grid(row=0, column=5)
        if self.selected_option.get() == 'Takeoff':
            self.v_rot_entry.grid(row = 0, column =1)
            self.knots_label.grid(row=0, column=2)
            self.pitch_entry.grid(row=0, column=3)
            self.pitch_label.grid(row=0, column=4)
            self.signal_entry.grid_forget()
            self.sig_val_entry.grid_forget()
        elif self.selected_option.get() == 'Set':
            self.signal_entry.grid(row=0, column=2)
            self.sig_val_entry.grid(row=0, column=3)
            self.v_rot_entry.grid_forget()
            self.knots_label.grid_forget()
            self.pitch_entry.grid_forget()
            self.pitch_label.grid_forget()
    def delete_rule(self):
        self.rule_frame.destroy()




root = Tk()
app_instance = App(root)
root.mainloop()