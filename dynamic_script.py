from tkinter import *

class App(): # Master
    def __init__(self,master):
        self.master = master
        master.title('AutoScript')
        master.geometry('700x700')
        master.resizable(True, True)

        # TODO: Add frames for cycling


class InitPage(App):
    def __init__(self,controller):
        super().__init__(controller)
        self.init_btn = Button(controller, text="Create Test Procedure", command = self.init_btn_pressed)
        self.init_btn.grid(row=0, column=0)
        self.config_label = Label(controller, text='Enter # of Configs')
        self.config_entry = Entry(controller)
        self.submit_btn = Button(controller, text = 'Plan Test Procedure', command = self.submit)

    def init_btn_pressed(self):
        self.init_btn.destroy()
        self.config_label.grid(row=0, column = 0)
        self.config_entry.grid(row = 0, column = 1, padx=5, pady=5)
        self.submit_btn.grid(row = 1, column = 0)

    def submit(self): # go to test creation page
        pass



class TestCreationPage(App):
    def __init__(self, controller):
        super().__init__(controller)


root = Tk()
app_instance = InitPage(root)
root.mainloop()
