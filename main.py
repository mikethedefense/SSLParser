from tkinter import *
from tkinter import filedialog
import json
import sys
import os

# --- Rudimentary App structure ---
# Tk (root window)
# └── container Frame
#     ├── InitPage Frame
#     └── TestCreationPage Frames

class App: # Master Controller
    def __init__(self,master):
        self.master = master
        master.title('AutoScript')
        master.geometry('1000x1000')
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
        self.test_procedure_name = StringVar()
        self.init_btn = Button(self, text="Create Test Procedure", command = self.init_btn_pressed)
        self.init_btn.grid(row=0, column=0)
        self.load_btn = Button(self, text="Load Test Procedure", command=self.load_json)
        self.load_btn.grid(row=0, column=1)
        self.exit_btn = Button(self, text = 'Quit', command = self.quit)
        self.exit_btn.grid(row=1, column=0)
        self.config_label = Label(self, text='Enter # of Configs')
        self.config_entry = Entry(self, textvariable =self.config_num)
        self.test_procedure_name_label =Label(self, text='Enter Test Procedure Name')
        self.test_procedure_name_entry = Entry(self, textvariable = self.test_procedure_name)
        self.submit_btn = Button(self, text = 'Submit', command = self.submit)

    def init_btn_pressed(self):
        self.init_btn.destroy()
        self.load_btn.destroy()
        self.exit_btn.destroy()
        self.test_procedure_name_label.grid(row = 0, column = 0)
        self.test_procedure_name_entry.grid(row = 0, column = 1, padx = 5, pady = 5)
        self.config_label.grid(row=1, column = 0)
        self.config_entry.grid(row = 1, column = 1, padx=5, pady=5)
        self.submit_btn.grid(row = 2, column = 0)
    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Set test procedure name
        self.test_procedure_name.set(data["procedure_name"])
        total = len(data["configs"])

        # Create pages from JSON
        for i, cfg in enumerate(data["configs"]):
            page = TestCreationPage(self.controller.container, self.controller, i, total)
            for rule in cfg["rules"]:
                r = _RulesFrame(page)
                r.selected_option.set(rule["type"])
                if rule["type"] == "Set":
                    r.signal_entry_variable.set(rule["signal"])
                    r.sig_val_entry_variable.set(rule["value"])
                elif rule["type"] == "Takeoff":
                    r.v_rot_entry_variable.set(rule["vrot"])
                    r.pitch_entry_variable.set(rule["pitch"])
                r.rule_frame.grid(row=page.row_counter.get(), column=0)
                page.rules_list.append(r)
                page.row_counter.set(page.row_counter.get() + 1)

            self.controller.frames[f'Config{i}'] = page
            page.grid(row=0, column=0, sticky='nsew')

        self.controller.show_frame('Config0')


    def submit(self): # go to test creation page
        total = self.config_num.get()
        for i in range(total):
            self.controller.frames[f'Config{i}'] = TestCreationPage(self.controller.container, self.controller,i, total)
            self.controller.frames[f'Config{i}'].grid(row = 0, column = 0,sticky='nsew')
        self.controller.show_frame('Config0')

    def quit(self):
        sys.exit()


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
        self.rules_list = []

        self.config_label = Label(self, text = f'Config {self.index + 1}', font = ('arial', 20), pady = 5)
        self.config_label.grid(row = 0, column = 0)

        # Config Pages Cycling
        if index > 0: # Back btn
            self.back_btn = Button(
                self, text='Back',
                command=lambda: self.controller.show_frame(f'Config{index - 1}')
            )
            self.back_btn.grid(row=99, column=0, sticky='w')
        if index < total - 1: # Forward Btn
            self.next_btn = Button(self, text = 'Next Config', command = lambda: self.controller.show_frame(f'Config{index + 1}'))
            self.next_btn.grid(row = 99, column = 10)
        else: # Generate Script Btn
            self.next_btn = Button(self, text = 'Generate SSL Script', command = lambda: self.finish())
            self.next_btn.grid(row=99, column=10)


    def add_rule(self,*args):
        rule = _RulesFrame(self)
        rule.rule_frame.grid(row=self.row_counter.get(), column=0)
        self.rules_list.append(rule)
        self.rule_btn.grid(row = self.row_counter.get() + 1, column = 0)
        self.row_counter.set(self.row_counter.get() + 1)

    def finish(self):
        """
        Creates an SSI file for scripting, and adds test data to JSON for loading
        """
        data = {
            "procedure_name": None,
            "configs": []
        }
        if not os.path.exists('Test Procedures'):
            os.makedirs('Test Procedures')

        for page in self.controller.frames.values():
            code_string = (
                'if file_exists(base.ssi) then\n'
                '\tinclude base.ssi;\n'
                'end if\n'
            )
            if isinstance(page, InitPage):
                data["procedure_name"] = page.test_procedure_name.get()
                tp_name = data["procedure_name"]
                folder_path = os.path.join("Test Procedures", tp_name)
                os.makedirs(folder_path, exist_ok = True)
            elif isinstance(page, TestCreationPage):
                config_data = {"rules": []}
                code_string += f'\n-- Config {page.index + 1}\n'

                for rule in page.rules_list:
                    # If more rules are added, more conditions need to be added.
                    if rule.selected_option.get() == 'Set':
                        sig = rule.signal_entry_variable.get()
                        val = rule.sig_val_entry_variable.get()
                        config_data["rules"].append({
                            "type": "Set",
                            "signal": sig,
                            "value": val
                        })
                        if val.isdigit():
                            code_string += f'{sig} =: {val};\n'
                        elif val.isalpha():
                            code_string += f'{sig} =: "{val}";\n'

                    elif rule.selected_option.get() == 'Takeoff':
                        vrot = rule.v_rot_entry_variable.get()
                        alt = rule.pitch_entry_variable.get()
                        config_data["rules"].append({
                            "type": "Takeoff",
                            "vrot": vrot,
                            "pitch": alt
                        })
                        code_string += f'takeoff({vrot}, {alt});\n'

                # Create the config ssi files
                ssi_config_path = os.path.join("Test Procedures",tp_name, f'Config{page.index}.ssi')
                with open(ssi_config_path, 'w') as f:
                    f.write(code_string)

                data["configs"].append(config_data)

        # Create the JSON data
        json_config_path = os.path.join("Test Procedures", tp_name, f'{tp_name}.json')
        with open(json_config_path, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Scripts saved to {tp_name}")
        print(f"Procedure saved to {tp_name}.json")

        # Go to Success page
        success_page = SuccessPage(self.controller.container, self.controller)
        self.controller.frames['SuccessPage'] = success_page
        success_page.grid(row=0, column=0, sticky='nsew')
        self.controller.show_frame('SuccessPage')

class SuccessPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.success_label = Label(self, text = 'Procedure Created', font = ('arial', 20), pady = 5)
        self.success_label.grid(row = 0, column = 0, sticky='nsew')
        self.exit_btn = Button(self, text = 'Exit', command = self.quit)
        self.exit_btn.grid(row = 1, column = 0)
        self.return_btn = Button(self, text = 'Create Another Test Procedure', command = self.reset)
        self.return_btn.grid(row = 1, column = 1)

    def quit(self):
        sys.exit()

    def reset(self):
        """
        If we want to create another test procedure, we reset everything and go back to init page
        """
        for page in self.controller.frames.values():
            page.destroy()
        self.controller.frames.clear()

        init_page = InitPage(self.controller.container, self.controller)
        self.controller.frames['InitPage'] = init_page
        init_page.grid(row=0, column=0, sticky='nsew')
        self.controller.show_frame('InitPage')


class _RulesFrame:
    """
    Private class used to define the rules base
    """
    def __init__(self,controller):
        self.controller = controller

        # Variables
        options = ['Takeoff', 'Set'] # Add more options here
        self.selected_option = StringVar()
        self.pitch_entry_variable = IntVar()
        self.signal_entry_variable = StringVar()
        self.sig_val_entry_variable = StringVar()
        self.v_rot_entry_variable = IntVar()

        # Frame Defined
        self.rule_frame = Frame(controller)

        # Labels and entries to use (more can be added)
        self.selector = OptionMenu(self.rule_frame, self.selected_option, *options)
        self.selector.grid(row=0, column=0)

        # Rules - more can be added
        self.v_rot_entry = Entry(self.rule_frame, textvariable = self.v_rot_entry_variable)
        self.knots_label = Label(self.rule_frame, text = 'Knots')
        self.pitch_label = Label(self.rule_frame, text = 'Degrees')
        self.pitch_entry = Entry(self.rule_frame, textvariable = self.pitch_entry_variable)
        self.signal_entry = Entry(self.rule_frame, textvariable = self.signal_entry_variable)
        self.sig_val_entry = Entry(self.rule_frame, textvariable = self.sig_val_entry_variable)

        self.del_btn = Button(self.rule_frame, text = 'Delete', command = self.delete_rule)

        # Trace
        self.selected_option.trace_add('write', callback = self.selector_callback)

    def selector_callback(self, *args):
        self.del_btn.grid(row=0, column=5)

        # Needs to be updated according to new rules added.
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