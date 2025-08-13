from tkinter import *
from tkinter import filedialog
import json
import sys
import os

# TODO: fix the loading function
# TODO: add if-else capability
# TODO: add database functionality (look-up tables)

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

    # Recursive Helpers
    def load_rules_from_data(self,parent_container, rules_data, indent=0):
        frames = []
        for rule in rules_data:
            rf = _RulesFrame(parent_container, indent_level=indent)
            rf.selected_option.set(rule['type'])

            if rule['type'] == 'Set':
                rf.signal_entry_variable.set(rule['signal'])
                rf.sig_val_entry_variable.set(rule['value'])

            elif rule['type'] == 'Wait':
                rf.wait_time.set(rule['wait_time'])

            elif rule['type'] == 'Prompt':
                rf.prompt.set(rule['prompt'])

            elif rule['type'] in ('If', 'Exit When'):
                # Load conditions
                for j, cond_data in enumerate(rule['conditions']):
                    if j > 0:
                        rf.add_conditions_row()
                    cond_row = rf.conditions[j]
                    cond_row.var_name.set(cond_data['variable'])
                    cond_row.operator.set(cond_data['operator'])
                    cond_row.value.set(cond_data['value'])
                    cond_row.logic_op.set(cond_data['logic_op'])
                # Load sub-rules recursively
                if 'sub_rules' in rule:
                    rf.sub_rules = self.load_rules_from_data(rf.sub_rules_container, rule['sub_rules'], indent + 1)
                rf.add_if_sub_rule_btn.grid(row=len(rf.sub_rules) + 1, column=0, sticky='w', pady=(20, 20))

            elif rule['type'] == 'Loop':
                rf.sub_rules = self.load_rules_from_data(rf.sub_rules_container, rule['sub_rules'], indent + 1)
                rf.add_loop_sub_rule_btn.grid(row=len(rf.sub_rules) + 1, column=0, sticky='w', pady=(20, 20))


            rf.rule_frame.grid(row=len(frames) + 1, column=0, sticky='w')
            frames.append(rf)
        return frames

    def export_rule_to_json_and_ssi(self,rule_frame, indent=0):
        """Returns (json_data, ssi_code) for a single _RulesFrame"""
        prefix = "\t" * indent
        rule_type = rule_frame.selected_option.get()

        if rule_type == 'Set':
            sig = rule_frame.signal_entry_variable.get()
            val = rule_frame.sig_val_entry_variable.get()
            json_data = {"type": "Set", "signal": sig, "value": val}
            code = f'{prefix}{sig} =: {val if val.isdigit() else f'"{val}"'};\n'
            return json_data, code

        elif rule_type == 'Wait':
            wt = rule_frame.wait_time.get()
            return {"type": "Wait", "wait_time": wt}, f"{prefix}wait({wt},True);\n"

        elif rule_type == 'Prompt':
            p = rule_frame.prompt.get()
            return {"type": "Prompt", "prompt": p}, f'{prefix}prompt("{p}");\n'

        elif rule_type in ('If', 'Exit When'):
            # Conditions
            conds = []
            cond_strs = []
            op_map = {'Equals': '=',
                      'Greater Than': '>',
                      'Less Than': '<',
                      'Not Equals': '/='}
            for cond in rule_frame.conditions:
                cd = {
                    "variable": cond.var_name.get(),
                    "operator": cond.operator.get(),
                    "value": cond.value.get(),
                    "logic_op": cond.logic_op.get()
                }
                conds.append(cd)
                op = op_map.get(cd['operator'])
                if cd['value'].isdigit():
                    cond_str = f"{cd['variable']} {op} {cd['value']}"
                else:
                    cond_str = f'{cd["variable"]} {op} "{cd["value"]}"'
                if cd['logic_op']:
                    cond_str += f' {cd["logic_op"].lower()} '
                cond_strs.append(cond_str)

            # Sub Rules
            sub_json = []
            sub_code = ""
            for sr in rule_frame.sub_rules:
                sj, sc = self.export_rule_to_json_and_ssi(sr, indent + 1)
                sub_json.append(sj)
                sub_code += sc

            json_data = {"type": rule_type, "conditions": conds, "sub_rules": sub_json}

            if rule_type == 'If':
                return json_data, f"{prefix}if {''.join(cond_strs)} then\n{sub_code}{prefix}end if\n"
            elif rule_type == 'Exit When':
                return json_data, f"{prefix}exit when {''.join(cond_strs)};\n"

        elif rule_type == 'Loop':
            sub_json = []
            sub_code = ""
            for sr in rule_frame.sub_rules:
                sj, sc = self.export_rule_to_json_and_ssi(sr, indent + 1)
                sub_json.append(sj)
                sub_code += sc
            return {"type": "Loop", "sub_rules": sub_json}, f"{prefix}loop\n{sub_code}{prefix}end loop\n"


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
            page.rules_list = self.controller.load_rules_from_data(page, cfg['rules'])
            for idx, rule_frame in enumerate(page.rules_list):
                rule_frame.rule_frame.grid(row = idx + 1, column = 0, sticky = 'w')


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
                    json_rule, ssi_code = self.controller.export_rule_to_json_and_ssi(rule)
                    config_data["rules"].append(json_rule)
                    code_string += ssi_code

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
    def __init__(self,controller, options = ['Set','Wait','Prompt','If', 'Loop'], indent_level = 0):
        self.controller = controller
        self.indent_level = indent_level
        self.sub_rules = []
        self.conditions = []

        # Variables
        self.options = options

        # Frames Defined
        self.rule_frame = Frame(controller)
        self.sub_rules_container = Frame(self.rule_frame)
        self.if_container = Frame(self.rule_frame)


        # Labels and entries to use (more can be added)
        self.selected_option = StringVar()
        self.selector = OptionMenu(self.rule_frame, self.selected_option, *self.options)
        self.selector.grid(row=0, column=0, padx = (self.indent_level * 20,0))
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

        # If
        self.add_if_sub_rule_btn = Button(self.sub_rules_container, text='Add If Sub-Rule', command=self.add_if_sub_rule)

        # Loop
        self.add_loop_sub_rule_btn = Button(self.sub_rules_container, text='Add Loop Sub-Rule',command=self.add_loop_sub_rule)

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
            self.if_container.grid(row = 0,column = 1)
            self.add_conditions_row()
            self.sub_rules_container.grid(row = 2, column = 1, sticky = 'w')
            self.add_if_sub_rule_btn.grid(row =0, column = 0, sticky = 'w', pady = (20,20))

        elif self.selected_option.get() == 'Loop':
            self.sub_rules_container.grid(row = 2, column = 1, sticky = 'w')
            self.add_loop_sub_rule_btn.grid(row = 0, column = 0, sticky ='w', pady = (20,20))

        elif self.selected_option.get() == 'Exit When':
            self.if_container.grid(row = 0, column=1)
            self.add_conditions_row()

    def add_if_sub_rule(self): # For if statement
        sub_rule = _RulesFrame(self.sub_rules_container, ['Set', 'Wait', 'Prompt', 'Loop'], indent_level = self.indent_level + 1)
        sub_rule.rule_frame.grid(row = len(self.sub_rules)+1, column = 0, sticky = 'w')
        self.add_if_sub_rule_btn.grid(row=len(self.sub_rules) + 2, column=0, sticky = 'w')
        self.sub_rules.append(sub_rule)
    def add_loop_sub_rule(self):
        sub_rule = _RulesFrame(self.sub_rules_container, ['Set', 'Wait', 'Prompt', 'If', 'Exit When'], indent_level = self.indent_level + 1)
        sub_rule.rule_frame.grid(row=len(self.sub_rules) + 1, column=0, sticky = 'w')
        self.add_loop_sub_rule_btn.grid(row=len(self.sub_rules) + 2, column=0, sticky = 'w')
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