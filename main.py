from tkinter import *
from tkinter import filedialog
import json
import sys
import os

# TODO: build repeat until functionality


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
                elif rule["type"] == "Wait":
                    r.wait_time.set(rule["wait_time"])
                elif rule["type"] == "Prompt":
                    r.prompt.set(rule["prompt"])
                elif rule['type'] == 'If':

                    # Populate the conditions
                    for j,cond_data in enumerate(rule['conditions']):
                        if j>0:
                            r.add_conditions_row()
                        cond_row = r.conditions[j]
                        cond_row.var_name.set(cond_data['variable'])
                        cond_row.operator.set(cond_data['operator'])
                        cond_row.value.set(cond_data['value'])
                        cond_row.logic_op.set(cond_data['logic_op'])
                    # Populate sub-rules
                    for sub in rule['sub_rules']:
                        sub_rule = _RulesFrame(r.sub_rules_container, ['Set', 'Wait', 'Prompt', 'Repeat Until'])
                        sub_rule.selected_option.set(sub['type'])
                        if sub['type'] == 'Set':
                            sub_rule.signal_entry_variable.set(sub['signal'])
                            sub_rule.sig_val_entry_variable.set(sub['value'])
                        elif sub['type'] == 'Wait':
                            sub_rule.wait_time.set(sub['wait_time'])
                        elif sub['type'] == 'Prompt':
                            sub_rule.prompt.set(sub['prompt'])
                        elif sub['type'] == 'Repeat Until':
                            # TODO
                            pass
                        sub_rule.rule_frame.grid(row = len(r.sub_rules) + 1, column =1, padx = (20,0))
                        r.sub_rules.append(sub_rule)

                r.rule_frame.grid(row=page.row_counter.get(), column=0, sticky = 'w')
                page.rules_list.append(r)
                page.row_counter.set(page.row_counter.get() + 1)

            self.controller.frames[f'Config{i}'] = page
            page.grid(row=0, column=0, sticky='nsew')
            page.row_counter.set(len(page.rules_list)+1)
            page.rule_btn.grid(row = page.row_counter.get(), column = 0)

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
        self.rule_btn.grid(row=1, column=0, stick = 'w')
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
        rule.rule_frame.grid(row=self.row_counter.get(), column=0, sticky = 'w')
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

                    elif rule.selected_option.get() == 'Wait':
                        wait_time = rule.wait_time.get()
                        config_data["rules"].append({
                            "type": "Wait",
                            "wait_time": wait_time,
                        })
                        code_string += f'wait({wait_time},True );\n'
                    elif rule.selected_option.get() == 'Prompt':
                        prompt = rule.prompt.get()
                        config_data["rules"].append({
                            "type": "Prompt",
                            "prompt": prompt,
                        })
                        code_string += f'prompt("{prompt}");\n'
                    elif rule.selected_option.get() == 'If':
                        conditions_data = []
                        cond_strings = [] # to be joined for ssl code.
                        op_map = {   # Mapping gui operators to the SSL
                            'Equals': '=',
                            'Greater Than': ">",
                            'Less Than': "<",
                            'Not Equals': '<>'
                        }
                        for cond in rule.conditions:
                            cond_data = {
                                "variable":cond.var_name.get(),
                                "operator":cond.operator.get(),
                                "value":cond.value.get(),
                                "logic_op": cond.logic_op.get()
                            }
                            ssl_op = op_map.get(cond_data['operator']) # Lookup the matching operator
                            if cond_data['value'].isdigit():
                                cond_str = f"{cond_data['variable']} {ssl_op} {cond_data["value"]}" # Combine the expressions
                            elif cond_data['value'].isalpha():
                                cond_str = f'{cond_data['variable']} {cond_data['operator']} "{cond_data['value']}"'
                            if cond_data['logic_op']:
                                cond_str += f' {cond_data['logic_op'].lower()} '
                            conditions_data.append(cond_data)
                            cond_strings.append(cond_str)
                        if_rule_data = {
                            "type": "If",
                            "conditions": conditions_data,
                            "sub_rules": []
                        }
                        ssl_condition = "".join(cond_strings).strip() # Remove whitespace
                        code_string += f'if {ssl_condition} then\n'

                        # Handle sub rules
                        for sub_rule in rule.sub_rules:
                            if sub_rule.selected_option.get() == 'Set':
                                sig = sub_rule.signal_entry_variable.get()
                                val = sub_rule.sig_val_entry_variable.get()
                                if_rule_data['sub_rules'].append({
                                    'type': 'Set',
                                    'signal': sig,
                                    'value': val
                                })
                                if val.isdigit():
                                    code_string += f'\t {sig} =: {val};\n'
                                else:
                                    code_string += f'\t {sig} =: "{val}";\n'
                            elif sub_rule.selected_option.get() == 'Wait':
                                wait_time =sub_rule.wait_time.get()
                                if_rule_data['sub_rules'].append({
                                    'type': 'Wait',
                                    'wait_time': wait_time,
                                })
                                code_string += f'\t wait({wait_time},True );\n'
                            elif sub_rule.selected_option.get() == 'Prompt':
                                prompt = sub_rule.prompt.get()
                                if_rule_data['sub_rules'].append({
                                    'type': 'Prompt',
                                    'prompt': prompt,
                                })
                                code_string += f'\t prompt("{prompt}");\n'
                            elif sub_rule.selected_option.get() == 'Repeat Until':
                                # TODO
                                pass
                        code_string += 'end if \n'
                        config_data["rules"].append(if_rule_data)





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
    def __init__(self,controller, options = ['Set','Wait','Prompt','If', 'Repeat Until']):
        self.controller = controller

        # Variables
        self.options = options

        # Frame Defined
        self.rule_frame = Frame(controller)

        # Labels and entries to use (more can be added)
        self.selected_option = StringVar()
        self.selector = OptionMenu(self.rule_frame, self.selected_option, *self.options)
        self.selector.grid(row=0, column=0)
        self.del_btn = Button(self.rule_frame, text='Delete', command=self.delete_rule)

        # ----Rules----

        # Set
        self.signal_entry_variable = StringVar()
        self.sig_val_entry_variable = StringVar()
        self.signal_entry = Entry(self.rule_frame, textvariable = self.signal_entry_variable)
        self.to_label = Label(self.rule_frame, text = 'to')
        self.sig_val_entry = Entry(self.rule_frame, textvariable = self.sig_val_entry_variable)


        # Wait
        self.wait_time = IntVar()
        self.wait_entry = Entry(self.rule_frame, textvariable = self.wait_time)
        self.seconds_label = Label(self.rule_frame, text = 'seconds')

        # Prompt
        self.prompt = StringVar()
        self.prompt_entry = Entry(self.rule_frame, textvariable = self.prompt)

        # Trace
        self.selected_option.trace_add('write', callback = self.selector_callback)

    def selector_callback(self, *args):
        self.del_btn.grid(row=0, column=5)
        for widget in self.rule_frame.grid_slaves():
            if widget not in (self.selector, self.del_btn):
                widget.grid_forget()
        if self.selected_option.get() == 'Set':
            self.signal_entry.grid(row=0, column=2)
            self.to_label.grid(row=0, column=3)
            self.sig_val_entry.grid(row=0, column=4)
        elif self.selected_option.get() == 'Wait':
            self.wait_entry.grid(row = 0, column =2)
            self.seconds_label.grid(row = 0, column = 3)
        elif self.selected_option.get() == 'Prompt':
            self.prompt_entry.grid(row = 0, column = 2)
        elif self.selected_option.get() == 'If':
            # Handling logic containers
            self.if_container = Frame(self.rule_frame)
            self.if_container.grid(row = 0,column = 1)
            self.conditions = []
            self.add_conditions_row()
            # Handling sub-rule Containers
            self.sub_rules_container = Frame(self.rule_frame)
            self.sub_rules_container.grid(row = 2, column = 1)
            self.add_sub_rule_btn = Button(self.sub_rules_container, text = 'Add Sub-Rule', command = self.add_sub_rule)
            self.add_sub_rule_btn.grid(row =0, column = 0)
            self.sub_rules = []
        elif self.selected_option.get() == 'Repeat Until':
            # TODO
            pass


        elif self.selected_option.get() == 'Repeat Until':
            pass
    def add_sub_rule(self):
        sub_rule = _RulesFrame(self.sub_rules_container, ['Set', 'Wait', 'Prompt', 'Repeat Until'])
        sub_rule.rule_frame.grid(row = len(self.sub_rules)+1, column = 1, padx = (20,0))
        self.add_sub_rule_btn.grid(row=len(self.sub_rules) + 2, column=1, pady = (0,25))
        self.sub_rules.append(sub_rule)

    def add_conditions_row(self):
        row = _ConditionRow(self.if_container, self.on_logic_change)
        self.conditions.append(row)
        row.set_grid(row = 0, column = len(self.conditions)-1)

    def on_logic_change(self,row):
        if row is self.conditions[-1] and row.logic_op.get() in ('AND', 'OR'):
            self.add_conditions_row()

    def delete_rule(self):
        self.rule_frame.destroy()


class _ConditionRow:
    """
    Private class used to define the boolean logic for conditionals (and loops)
    """
    def __init__(self, parent, on_logic_change): # on_logic_change is the callback function for the trace
        self.frame = Frame(parent)
        self.operator = StringVar(value = "Equals")
        self.logic_op = StringVar(value = "")
        self.var_name = StringVar()
        self.value = StringVar()

        Entry(self.frame, textvariable=self.var_name, width=10).grid(row=0, column=0)
        OptionMenu(self.frame, self.operator, "Equals", "Greater Than", "Less Than", "Not Equals").grid(row=0, column=1)
        Entry(self.frame, textvariable=self.value, width=10).grid(row=0, column=2)
        OptionMenu(self.frame, self.logic_op, "", "AND", "OR").grid(row=0, column=3)

        self.logic_op.trace_add('write', lambda *a: on_logic_change(self))
    def set_grid(self, **kwargs):
        self.frame.grid(**kwargs)

root = Tk()
app_instance = App(root)
root.mainloop()