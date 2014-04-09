import Tkinter
import tkMessageBox

from api.configuration_api import ConfigurationAPI

class FieldValidations(object):
    def validate_int_command(self):
        return (self.register(self.validate_int), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    def validate_int(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == '' or value_if_allowed == None:
            return True
        elif text in '0123456789':
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

class DripCalibrationUI(Tkinter.Frame, FieldValidations):
    update_drips_job = None

    def __init__(self,parent, configuration_api):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self._configuration_api = configuration_api
        self._configuration_api.start_counting_drips()
        self.drips = 0
        self.initialize()
        self.update_drips()

    def initialize(self):
        self.grid()
        
        self.instructions = u"Some much better text and instructions go here"
        instructions_label = Tkinter.Label(self,text=self.instructions, anchor="w",fg="pink",bg="green")
        instructions_label.grid(column=0,row=0,columnspan=4,sticky='EW')

        self.drip_count_label = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.drip_count_label, anchor="w",fg="black",bg="white")
        label.grid(column=1,row=1,columnspan=2,sticky='EW')
        self.drip_count_label.set(str(self._configuration_api.get_drips()))
        
        reset_button = Tkinter.Button(self,text=u"Reset Counter", command=self.reset_button_clicked)
        reset_button.grid(column=2,row=1)   

        height_mm_label = Tkinter.Label(self,text="End Height in Millimeters", anchor="w",fg="black",bg="white", justify="right")
        height_mm_label.grid(column=0,row=2,columnspan=1,sticky='EW')

        self.height_mm_entry = Tkinter.Entry(self, width=20, justify="left", text=str(10), validate = 'key', validatecommand=self.validate_int_command())
        self.height_mm_entry.grid(column=1,row=2)

        drips_per_mm_label = Tkinter.Label(self,text="Drips per mm", anchor="w",fg="black",bg="white", justify="right")
        drips_per_mm_label.grid(column=0,row=3,columnspan=1,sticky='EW')

        self.drips_per_mm_field_text = Tkinter.StringVar()
        drips_per_mm_field = Tkinter.Label(self,textvariable=self.drips_per_mm_field_text, anchor="w",fg="black",bg="white")
        drips_per_mm_field.grid(column=1,row=3,columnspan=1,sticky='EW')
        self.drips_per_mm_field_text.set("")

        mark_button = Tkinter.Button(self,text=u"Mark", command=self.mark_button_clicked)
        mark_button.grid(column=2,row=2) 

        quit_button = Tkinter.Button(self,text=u"Done", command=self.done_button_clicked)
        quit_button.grid(column=3,row=4)    
       
        self.grid_columnconfigure(3,weight=1)
        self.update()

    def update_drips(self):
        if self.update_drips_job:
            self.after_cancel(self.update_drips_job)
            self.update_drips_job = None
        self.drips = self._configuration_api.get_drips()
        self.drip_count_label.set("Drips: %d" % self.drips)
        self.update_drips_job=self.after(250, self.update_drips)

    def reset_button_clicked(self):
        self._configuration_api.reset_drips()
        self.update_drips()

    def done_button_clicked(self):
        self.close()
        self.parent.start_main_window()

    def mark_button_clicked(self):
        try:
            self._configuration_api.set_target_height(self.height_mm_entry.get())
            self._configuration_api.mark_drips_at_target()
            self.drips_per_mm_field_text.set("%.2f" %self._configuration_api.get_drips_per_mm())
        except Exception as ex:
            tkMessageBox.showwarning(
            "Error",
            ex.message
        )

    def close(self):
        self._configuration_api.stop_counting_drips()
        