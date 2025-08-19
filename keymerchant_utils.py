import ctypes
import threading

import customtkinter, tkinter, os, sys, enum, multiprocessing
import keyboard


class Logic:
    def __init__(self):
        pass

    class LoggingModes(enum.Enum):
        OFF = 0
        TXT = 1
        JSON = 2


    class PrintStates(enum.Enum):
        OFF = 0
        ON = 1


    def print_handler(self, target_state):
        sys.stdout = sys.__stdout__ if target_state == self.PrintStates.ON else open(os.devnull, 'w')



class KmManager:
    def __init__(self, handler):
        # Boolean program states (mostly enabled or disabled options)
        self.quiet_mode, self.hidden_mode, self.currently_listening, self.context_logging, self.start_minimize = \
            False, False, False, False, False

        # UI elements that need to be modified
        self.root, self.start_btn, self.stop_btn, self.logmode_box, \
            self.quietmode_chckbox, self.outdir_tip, self.min_icon = \
            None, None, None, None, None, None, None

        # Program data - "standard" variables
        self.kblisten, self.out_stream, self.out_path, self.logmode, self.json_dict = \
            None, None, '', Logic.LoggingModes.OFF, {'INTRO': '', 'KEYSTROKES': [], 'OUTRO': ''}

        # Constants
        self.CURRENT_OS = sys.platform

        # Listener
        # self.listener = threading.Thread(daemon = True, target = lambda: keyboard.on_press(handler))
        # self.listener = multiprocessing.Process(target = keyboard.on_press, args = (handle_event, ))



class Listener(threading.Thread):
    def __init__(self, name, handler):
        threading.Thread.__init__(self)
        self.name = name
        self.handler = handler
        self.internal_listener = None

    def run(self):
        try:
            self.internal_listener = keyboard.on_press(self.handler)
        finally:
            print('thread started')

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        keyboard.unhook(self.internal_listener)
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('couldn\'t raise exception')


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
        def __init__(self, frame, root, start, stop, modes, checkbox, dir_prompt, minimize):
            # Colors and fonts
            uitext_white_1, uitext_white_2, uitext_white_dis = '#E8E8E8', '#B8B8B8', '#9E9E9E'
            btn_blue_1, btn_blue_hvr = '#174EDD', '#1038A0'

            # Labels
            self.program_title = customtkinter.CTkLabel(frame, text = 'keymerchant 0.2b',
                text_color = uitext_white_1, justify = 'left', padx = 0, pady = 0, font = ('Nacelle Light', 20))

            self.hotkey_hint_label = customtkinter.CTkLabel(frame, text = 'ctrl + alt + k', text_color = uitext_white_2,
                justify = 'left', padx = 0, pady = 0, font = ('Nacelle Regular', 12, 'italic'))

            self.bracket_label = customtkinter.CTkLabel(frame, text = ']', text_color = uitext_white_2, justify = 'left',
                padx = 0, pady = 0, font = ('Nacelle Light', 40))

            self.quote_label = customtkinter.CTkLabel(root, text = 'mystify, mislead, surprise', text_color = uitext_white_2,
                justify = 'center', padx = 0, pady = 0, font = ('Nacelle Medium', 10, 'italic'))

            self.logging_mode_label = customtkinter.CTkLabel(frame, text = 'logging mode:', text_color = uitext_white_1,
                justify = 'center', padx = 0, pady = 0, font = ('Nacelle Regular', 13))

            # Buttons
            self.start_button = customtkinter.CTkButton(frame, text = 'start logging',
                command = start, width = 105, fg_color = '#139900', hover_color = '#0C6500', corner_radius = 0,
                text_color_disabled = uitext_white_dis, font = ('Nacelle Regular', 14), border_spacing = 0)

            self.stop_button = customtkinter.CTkButton(frame, text = 'stop logging', command = stop,
                width = 105, fg_color = '#E72424', hover_color = '#A01111', text_color_disabled = uitext_white_dis,
                state = 'disabled', font = ('Nacelle Regular', 14), corner_radius = 0)

            self.output_directory_button = customtkinter.CTkButton(frame, text = 'select output directory',
                command = dir_prompt, width = 180, fg_color = btn_blue_1, hover_color = btn_blue_hvr, state = 'normal',
                font = ('Nacelle Regular', 13), height = 24, corner_radius = 0)

            self.minimize_button = customtkinter.CTkButton(frame, text = 'minimize to tray',
                command = lambda: minimize(), fg_color = btn_blue_1, hover_color = btn_blue_hvr, state = 'normal',
                font = ('Nacelle Regular', 13), height = 24, width = 180, corner_radius = 0)

            # Check- and input boxes
            self.logging_mode_box = customtkinter.CTkComboBox(frame, values = modes, state = 'readonly',
                width = 100, font = ('Nacelle Light', 14), dropdown_font = ('Nacelle Light', 12), justify = 'right',
                corner_radius = 0)

            self.hidden_mode_checkbox = customtkinter.CTkCheckBox(frame, text = 'hidden mode', onvalue = 'on',
                offvalue = 'off', width = 100, text_color = '#E8E8E8', font = ('Nacelle Light', 15),
                command = lambda: checkbox('H'), corner_radius = 0)

            self.quiet_mode_checkbox = customtkinter.CTkCheckBox(frame, text='quiet mode', onvalue='on',
                offvalue='off', width=100, text_color='#E8E8E8', font = ('Nacelle Light', 15),
                command = lambda: checkbox('Q'), corner_radius = 0)

            self.context_logging_checkbox = customtkinter.CTkCheckBox(frame, text = 'context logging', onvalue = 'on',
                offvalue = 'off', width = 100, text_color = '#E8E8E8', font = ('Nacelle Light', 15),
                command = lambda: checkbox('C'), corner_radius = 0)

            self.minimization_checkbox = customtkinter.CTkCheckBox(frame, text = 'minimize on start', onvalue = 'on',
                offvalue = 'off', width = 100, text_color = '#E8E8E8', font = ('Nacelle Light', 15),
                command = lambda: checkbox('M'), corner_radius = 0)



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