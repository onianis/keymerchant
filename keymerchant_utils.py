import customtkinter, tkinter, os, sys
from enum import Enum



class Logic:
    def __init__(self):
        pass

    class LoggingModes(Enum):
        OFF = 0
        TXT = 1
        JSON = 2


    class PrintStates(Enum):
        OFF = 0
        ON = 1


    def print_handler(self, target_state):
        sys.stdout = sys.__stdout__ if target_state == self.PrintStates.ON else open(os.devnull, 'w')



class GuiUtils:
    def center_window(window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")


    class Elements:
        def __init__(self, frame, root, start, stop, modes, checkbox, dir_prompt):
            self.program_title = customtkinter.CTkLabel(frame, text = 'keymerchant 0.5a',
                text_color = '#E8E8E8', justify = 'left', padx = 0, pady = 0, font = ('Nacelle Light', 20))

            self.start_button = customtkinter.CTkButton(frame, text = 'start logging',
                command = start, width = 105, fg_color = '#139900', hover_color = '#0C6500',
                text_color_disabled = '#9E9E9E', font = ('Nacelle Regular', 14), border_spacing = 0)

            self.stop_button = customtkinter.CTkButton(frame, text = 'stop logging', command = stop,
                width = 105, fg_color = '#E72424', hover_color = '#A01111', text_color_disabled = '#9E9E9E',
                state = 'disabled', font = ('Nacelle Regular', 14))

            self.logging_mode_label = customtkinter.CTkLabel(frame, text = 'logging mode:', text_color = '#E8E8E8',
                justify = 'center', padx = 0, pady = 0, font = ('Nacelle Regular', 13))

            self.logging_mode_box = customtkinter.CTkComboBox(frame, values = modes, state = 'readonly',
                width = 100, font = ('Nacelle Light', 14), dropdown_font = ('Nacelle Light', 12), justify = 'right')

            self.hidden_mode_checkbox = customtkinter.CTkCheckBox(frame, text = 'hidden mode', onvalue = 'on',
                offvalue = 'off', width = 100, text_color = '#E8E8E8', font = ('Nacelle Light', 15), command = lambda: checkbox('H'))

            self.quiet_mode_checkbox = customtkinter.CTkCheckBox(frame, text='quiet mode', onvalue='on',
                offvalue='off', width=100, text_color='#E8E8E8', font = ('Nacelle Light', 15), command = lambda: checkbox('Q'))

            self.context_logging_checkbox = customtkinter.CTkCheckBox(frame, text = 'context logging', onvalue = 'on',
                offvalue = 'off', width = 100, text_color = '#E8E8E8', font = ('Nacelle Light', 15), command = lambda: checkbox('C'))

            self.quote_label = customtkinter.CTkLabel(root, text = 'mystify, mislead, surprise', text_color = '#B8B8B8',
                justify = 'center', padx = 0, pady = 0, font = ('Nacelle Medium', 10, 'italic'))

            self.output_directory_button = customtkinter.CTkButton(frame, text = 'select output directory', command = dir_prompt,
                width = 150, fg_color = '#174EDD', hover_color = '#1038A0', state = 'normal', font = ('Nacelle Regular', 14))



    class CustomTooltip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.tooltip_window = None

        def enter(self, event=None):
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            self.tooltip_window = tkinter.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry("+%d+%d" % (x, y))
            label = tkinter.Label(self.tooltip_window, text=self.text, justify='left',
                             background='#ffffff', relief='solid', borderwidth=1,
                             font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)

        def leave(self, event=None):
            if self.tooltip_window:
                self.tooltip_window.destroy()