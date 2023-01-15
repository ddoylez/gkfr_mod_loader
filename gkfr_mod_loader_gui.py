import os.path
import shutil
import subprocess
import sys

import PySimpleGUI as sg


def get_gkfr_files():
    gkfr_path = sg.user_settings_get_entry('-gkfr folder-', '')
    mods_path = sg.user_settings_get_entry('-mods folder-', '')

    try:
        mods_files = os.listdir(mods_path)
    except:
        mods_files = []

    try:
        gkfr_files = os.listdir(gkfr_path)
    except:
        gkfr_files = []

    return gkfr_files, mods_files


def settings_window():
    bepinex_folder_tooltip = 'Wherever your BepInEx folder is inside the GKFR install.\ne.g. steamapps/common/Garfield Kart - Furious Racing/BepInEx/plugins'
    local_mods_folder_tooltip = 'Wherever you keep your pool of local mod files.'

    layout = [[sg.T('Program Settings', font='DEFAIULT 18')],
              [sg.T('Path to GKFR BepInEx Install', size=(20, 1), tooltip=bepinex_folder_tooltip),
               sg.In(sg.user_settings_get_entry('-gkfr folder-', ''), k='-GKFR-'), sg.FolderBrowse()],
              [sg.T('Path to Local Mods', size=(20, 1), tooltip=local_mods_folder_tooltip),
               sg.In(sg.user_settings_get_entry('-mods folder-', ''), k='-MODS-'), sg.FolderBrowse()],
              [sg.Combo(sg.theme_list(), sg.user_settings_get_entry('-theme-', None), k='-THEME-')],
              [sg.B('Ok'), sg.B('Cancel')],
              ]

    window = sg.Window('Settings', layout)
    event, values = window.read(close=True)
    if event == 'Ok':
        sg.user_settings_set_entry('-gkfr folder-', values['-GKFR-'])
        sg.user_settings_set_entry('-mods folder-', values['-MODS-'])
        sg.user_settings_set_entry('-theme-', values['-THEME-'])
        return True

    return False


# --------------------------------- Create the window ---------------------------------
def make_window():
    theme = sg.user_settings_get_entry('-theme-')
    gkfr_files, mods_files = get_gkfr_files()

    sg.theme(theme)
    # First the window layout...2 columns

    filter_tooltip = "Filter files\nEnter a string in box to narrow down the list of files.\nFile list will update with list of files with string in filename."

    left_col = [
        [sg.Text('Loaded BepInEx Plugins', font='Any 20')],
        [sg.Listbox(values=gkfr_files, select_mode=sg.SELECT_MODE_EXTENDED, size=(40, 20), key='-GKFR LIST-')],
        [sg.Text('Filter:', tooltip=filter_tooltip),
         sg.Input(size=(25, 1), enable_events=True, key='-FILTER-', tooltip=filter_tooltip)],
        [sg.Button('Unload ->', key='-DELETE FROM-')],
    ]

    right_col = [
        [sg.Text('Available BepInEx Plugins', font='Any 20')],
        [sg.Listbox(values=mods_files, select_mode=sg.SELECT_MODE_EXTENDED, size=(40, 20), key='-MODS LIST-')],
        [sg.Text('Filter:', tooltip=filter_tooltip),
         sg.Input(size=(25, 1), enable_events=True, key='-FILTER2-', tooltip=filter_tooltip)],
        [sg.Button('<- Load', key='-COPY TO-')],
    ]

    # ----- Full layout -----

    layout = [[sg.vtop(sg.Column(left_col, element_justification='c')), sg.VSeperator(),
               sg.vtop(sg.Column(right_col, element_justification='c'))],
              [sg.HorizontalSeparator()],
              [sg.Button('Exit'), sg.B('Settings')],
              ]

    # --------------------------------- Create Window ---------------------------------
    window = sg.Window('GKFR Mod Loader', layout)

    return window


# --------------------------------- Main Program Layout ---------------------------------

def main():
    """
    The main program that contains the event loop.
    It will call the make_window function to create the window.
    """

    gkfr_path = sg.user_settings_get_entry('-gkfr folder-', '')
    mods_path = sg.user_settings_get_entry('-mods folder-', '')
    gkfr_files, mods_files = get_gkfr_files()

    window = make_window()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        elif event == '-COPY TO-':
            for file in values['-MODS LIST-']:
                shutil.copyfile(os.path.join(mods_path, file), os.path.join(gkfr_path, file))
                gkfr_files, mods_files = get_gkfr_files()
                window['-GKFR LIST-'].update(values=gkfr_files)
        elif event == '-DELETE FROM-':
            for file in values['-GKFR LIST-']:
                try:
                    os.remove(os.path.join(gkfr_path, file))
                except:
                    pass
                gkfr_files, mods_files = get_gkfr_files()
                window['-GKFR LIST-'].update(values=gkfr_files)
        elif event == '-FILTER-':
            new_list = [i for i in gkfr_files if values['-FILTER-'].lower() in i.lower()]
            window['-GKFR LIST-'].update(values=new_list)
        elif event == '-FILTER2-':
            new_list = [i for i in mods_files if values['-FILTER2-'].lower() in i.lower()]
            window['-MODS LIST-'].update(values=new_list)
        elif event == 'Settings':
            if settings_window() is True:
                window.close()
                window = make_window()
                gkfr_path = sg.user_settings_get_entry('-gkfr folder-')
                mods_path = sg.user_settings_get_entry('-mods folder-')
                gkfr_files, mods_files = get_gkfr_files()
    window.close()


if __name__ == '__main__':
    main()
