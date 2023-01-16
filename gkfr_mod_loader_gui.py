import os.path
import shutil
import zipfile
import subprocess
import sys

import PySimpleGUI as sg

PLUGINS_FOLDER = 'BepInEx/plugins/'


def get_gkfr_files():
    gkfr_path = sg.user_settings_get_entry('-gkfr folder-', '')
    mods_path = sg.user_settings_get_entry('-mods folder-', '')

    try:
        mods_files = os.listdir(mods_path)
    except:
        mods_files = []

    try:
        gkfr_files = os.listdir(os.path.join(gkfr_path, PLUGINS_FOLDER))
    except:
        gkfr_files = []

    return gkfr_files, mods_files


def bepinex_window():
    layout = [[sg.T('BepInEx Zip', size=(20, 1)),
               sg.In(sg.user_settings_get_entry('-bepinex zip-', ''), k='-ZIP-'), sg.FileBrowse()],
              [sg.B('Install'), sg.B('Cancel')],
              ]

    window = sg.Window('BepInEx Install', layout)
    event, values = window.read(close=True)
    if event == 'Install':
        install_dir = sg.user_settings_get_entry('-gkfr folder-', '')
        sg.user_settings_set_entry('-bepinex zip-', values['-ZIP-'])
        with zipfile.ZipFile(sg.user_settings_get_entry('-bepinex zip-'), 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        try:
            os.mkdir(os.path.join(install_dir, PLUGINS_FOLDER))
        except:
            pass
        return True

    return False


def remove_bepinex_window():
    winhttp = 'winhttp.dll'
    config = 'doorstop_config.ini'
    changelog = 'changelog.txt'

    layout = [[sg.T('Are you sure you want to remove BepInEx?')],
              [sg.B('Yes'), sg.B('No')],
              ]

    window = sg.Window('BepInEx Uninstall', layout, element_justification='c')
    event, values = window.read(close=True)
    if event == 'Yes':
        install_dir = sg.user_settings_get_entry('-gkfr folder-', '')
        try:
            shutil.rmtree(os.path.join(install_dir, PLUGINS_FOLDER), ignore_errors=True)
            os.remove(os.path.join(install_dir, winhttp))
            os.remove(os.path.join(install_dir, config))
            os.remove(os.path.join(install_dir, changelog))
        except:
            pass
        return True

    return False


def settings_window():
    bepinex_folder_tooltip = 'Wherever your GKFR install is located.\ne.g. steamapps/common/Garfield Kart - Furious Racing'
    local_mods_folder_tooltip = 'Wherever you keep your pool of .dll mod files.'

    layout = [[sg.T('Program Settings', font='DEFAIULT 18')],
              [sg.T('Path to GKFR Install', size=(20, 1), tooltip=bepinex_folder_tooltip),
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
              [sg.Button('Settings'), sg.B('Install BepInEx'), sg.B('Remove BepInEx')],
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
        if event == sg.WINDOW_CLOSED:
            break
        elif event == '-COPY TO-':
            for file in values['-MODS LIST-']:
                shutil.copyfile(os.path.join(mods_path, file), os.path.join(gkfr_path, PLUGINS_FOLDER, file))
                gkfr_files, mods_files = get_gkfr_files()
                window['-GKFR LIST-'].update(values=gkfr_files)
        elif event == '-DELETE FROM-':
            for file in values['-GKFR LIST-']:
                try:
                    os.remove(os.path.join(gkfr_path, PLUGINS_FOLDER, file))
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
        elif event == 'Install BepInEx':
            if bepinex_window() is True:
                window.close()
                window = make_window()
        elif event == 'Remove BepInEx':
            if remove_bepinex_window() is True:
                window.close()
                window = make_window()
    window.close()


if __name__ == '__main__':
    main()
