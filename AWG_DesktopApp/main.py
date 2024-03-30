import PySimpleGUI as sg
import math
import string
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#do pip install pyserial, pyusb and pytime
import serial.tools.list_ports
import time

import wavegen

# Global Variables
mode=0
channel_count = 16
current_channel = 0
graph_size_x=900
graph_size_y=375
use_custom_titlebar = False
channel_list = ["Channel " + str(i) for i in range(0,15,1)]

# Variables for keeping track of channel parameters and status
# Initialize to default values
channel_frequencies = [15.0]*channel_count #In kHz
channel_amplitude = [1.0]*channel_count
channel_phase = [0.0]*channel_count
channel_wavetype = ['SINE']*channel_count
channel_status= [False]*channel_count

# make_window()
# This function defines the layouts, then draws the window
# returns the window to be drawn
def make_window(mode,theme=None):

    NAME_SIZE = 16

    #font to use
    interface_font='Courier 10'

    # name(name)
    # Creates a pySimpleGUI Text element and populates it with given text
    # takes in a string value to add to the text element
    def name(name):
        return sg.Text(name + ' ' + ':', size=(NAME_SIZE,1), justification='left',pad=(0,0), font=interface_font)

    sg.theme(theme)

    # Layouts
    ##### Standard Waveform Generator Layout
    # This is the left side layout that includes the statuses of all the channels
    layout_l = [[ sg.Text('Status',font='Courier 16')],
                [ sg.HSep()],
                *[[sg.Col([[sg.Text(f'Channel {i}'),sg.Text('●', size=(1, 1), text_color='red',key=f'-CIRCLE{i}-')]]) ]for i in range(0,channel_count)],
                ]

    #  Right side layout
    parameter_layout =[[name('Frequency(kHz)'), sg.Spin([round(i * 0.1, 1) for i in range(150, 5000)],initial_value=15.0, s=(15,2), k='-FREQUENCY-', enable_events=True)],
                       [name('Amplitude(V)'), sg.Spin([round(i * 0.1, 1) for i in range(0, 150)],initial_value=1.0, s=(15,2), k='-AMPLITUDE-'),sg.Button('Set',expand_x=True, enable_events=True, k='-SETPARAMS-')],
                       [name('Phase Shift(°)'), sg.Spin([round(i * 0.1, 1) for i in range(-3600, 3600)],initial_value=0.0, s=(15,2),k='-PHASE-')],
                       #[name('Offset'), sg.Spin(['0 V',], s=(15,2))]
                       ]
    # Layout that contains the presets for the waves
    preset_layout =[[name('Preset waves'), sg.Combo(['Sine','Square','Triangle'], default_value='Sine', s=(15,22), enable_events=False, readonly=True, k='-PRESET-')],
                       [sg.Button('Use',expand_x=True, enable_events=True, k='-SETPRESET-')],
                       ]

    ## Layout for determining the Input/Output and Mode of the AWG
    ### Currently unused, may be re-added in the future
    function_layout =[[name('Input/Output:'), sg.Combo(['Output','Input'], default_value='Output', s=(15,22), enable_events=False, readonly=True, k='-FUNCTION-')],
                      [name('Mode:'), sg.Combo(['DAC','ADC'], default_value='Output', s=(15,22), enable_events=False, readonly=True, k='-MODE-')]
                       ]
    ## The layout that includes the ON/OFF slider button
    button_layout =[[sg.Slider(range=(0, 1), default_value=0, orientation='h', size=(8, 40), key='-SLIDER-', enable_events=True,tooltip='Toggle On/Off',disable_number_display=True),

                        ],
                        [sg.Text('State: '), sg.Text('Off', size=(5,1), key='-STATE-'),]
                ]

    ## This is the layout for the parameter and channel control; Includes Parameter layout, preset layout and On/Off layout
    # frame_layout = [[sg.Graph((graph_size_x+80, graph_size_y+20), (0,20), (graph_size_x,graph_size_y),background_color='white', k='-GRAPH-')],
    frame_layout = [[sg.Canvas(size=(graph_size_x+80, graph_size_y+20), k='-AWG-GRAPH-')],
                    [
                       sg.Column([[sg.Frame("Parameters",parameter_layout)]]),
                       sg.Column([[sg.Frame("Presets",preset_layout)]]),
                     #  sg.Column([[sg.Frame("Function",function_layout,expand_y=True)]]),
                       sg.Column([[sg.Frame("On/Off",button_layout,expand_y=True)]])
                    ]
                 ]
    ## Layout for the right side of the Interface; Includes the Graph, Channel name and all the parameter controls
    layout_r  = [[sg.Text("Channel " + str(current_channel), k='-CHANNELTEXT-'),sg.Push(),sg.Combo(channel_list, default_value="Channel " + str(current_channel), size=(15,22), enable_events=True, readonly=True, k='-CHANNELNUM-',)],
                 [sg.Frame("Waveform",frame_layout)]]
    #############################################
    ### EIT Layout ###
    layout_eit_parameters = [[sg.Push(),sg.Text('Electrodes :',font=interface_font), sg.Spin(['0',], s=(15,2), k='-ELECTRODES-')],
                       [sg.Push(),sg.Text('Distance Between Electrodes (m) :',font=interface_font), sg.Spin(['0',], s=(15,2), k='-ELECTRODESD-')],
                       #[sg.Push(),sg.Text('Amplitude (V) :',font=interface_font), sg.Spin(['0',], s=(15,2),k='-AMPLITUDE2-')],
                       [sg.Push(),sg.Text('Frequency of Injected Current (Hz) :',font=interface_font), sg.Spin(['0',], s=(15,2),k='-FREQUENCY2-')],
                       #[sg.Push(),sg.Text('Voltage Out (V) :',font=interface_font), sg.Spin(['0',], s=(15,2),k='-VOLTAGEOUT-')],
                       [sg.Button('Submit',expand_x=True, enable_events=True, k='-SUBMITEIT-')]
                       ]
    layout_eit = [
                    [
                        sg.Column([
                            [sg.Text('Electrical Impedance Tomography (EIT)',font='Courier 16')],
                            [sg.Column([[sg.Frame("Parameters",layout_eit_parameters)]])],
                            [sg.Canvas(size=(450,450), k='-EIT-GRAPH-')]
                            # [sg.Frame("",[[sg.Graph((450,450),(0,450),(450,0),background_color='white',border_width=1)]])]
                        ],element_justification='center')
                    ]
                  ]

    ###################

    ### Window drawing ###
    layout = [ [sg.Col(layout_l,size=(None,None),expand_x=True, expand_y=True, pad=(0,0), ), sg.VSep(), sg.Col(layout_r,vertical_alignment='top')]]

    eit_window_layout = [[ sg.Col(layout_eit,vertical_alignment='top')]]


    main_layout = [
        [
            sg.Menu([['File', ['Import', 'Export', 'Exit']], ['Tools', ['EIT']], ['Help', ['User Manual', 'Basics']]],
                    k='-CUST MENUBAR-', p=0)
        ],
        [
            sg.Column(
                [
                    [
                        sg.Column(eit_window_layout, visible=(mode == "eit"), key='-EIT-'),
                        sg.Column(layout, visible=(mode == "awg"), key='-AWG-')
                    ]
                ],
                key='-MAIN COLUMN-', justification= 'center'
            )
        ]
    ]
    window_size= (1080,600)

    window = sg.Window('16 Channel Arbitrary Waveform Generator', main_layout, finalize=True,  keep_on_top=False, use_custom_titlebar=use_custom_titlebar, size= window_size)


    return window

def to_int (str:str):
    return int(str.strip(string.ascii_letters + string.punctuation))

def to_float (str:str):
    return float(str.strip(string.ascii_letters + string.punctuation))

def get_attrib (array, index):
    return array[index].strip(string.ascii_letters + string.punctuation)

def get_int (array, index):
    return int(get_attrib(array, index))

def get_float (array,index):
    return float(get_attrib(array, index))

def get_bool (array,index):
    string = array[index]
    if string == "On":
        return True
    if string == "Off":
        return False

def to_int (str:str):
    return int(str.strip(string.ascii_letters))

def gen_graph_data (ch_n):
    return wavegen.gen_graph(channel_frequencies[ch_n] * 1000, # Converting to kHz
                             channel_phase[ch_n],
                             "SINE") #get_attrib(channel_wavetype,ch_n) )

def update_graph (ch_n:int, ax:plt.axes, canvas):
    ax.clear()
    x, y = gen_graph_data (ch_n)
    ax.plot(x,y)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    pass

# change_channel(window)
# This function handles all events for when a channel is changes
# Includes saving the current parameters and calling the function for sending a serial message
# and then retrieving the parameters for the channel that was switched to.
# takes in the window to access the elements
def change_channel(window):
    # The current parameters are already saved by the parameter update event. There's no need to do that here.
    #Update the window with the new channel parameters
    channel_disp = values['-CHANNELNUM-'] # Get the updated channel number (Starting at 1)
    window['-CHANNELTEXT-'].update(channel_disp)
    current_channel = to_int(channel_disp)

    # Retrieve the values associated with the new channel
    amplitude_input = float(window['-AMPLITUDE-'].get())
    frequency_input = float(window['-FREQUENCY-'].get())
    phase_input     = float(window['-PHASE-'].get())
    use_preset = values['-PRESET-']

    # Reflect those new values in the GUI
    window['-FREQUENCY-'].update(frequency_input)
    window['-AMPLITUDE-'].update(amplitude_input)
    window['-PHASE-'].update(phase_input)
    window['-PRESET-'].update(use_preset)

    if channel_status[current_channel] == False:
        window['-SLIDER-'].update(value=0)
        window['-STATE-'].update('Off')
    else:
        window['-SLIDER-'].update(value=1)
        window['-STATE-'].update('On')

    update_graph(current_channel, ax_awg, awg_canvas_agg)

#check_params(amplitude, frequency, phase)
#checks if the parameters are within the expected ranges
# If the input is invalid, create a popup
# Returns a boolean: True if the input is valid, False otherwise
def check_params(amplitude, frequency, phase):
    message = "ERROR: \n"
    invalid_input = False
    if ((amplitude < 0) or (amplitude > 15)):
        message += "Amplitude input is invalid. Must be between 0 V and 15 V.\n"
        invalid_input = True
    if (frequency < 15) or (frequency > 500):
        message += "Frequency input is invalid. Must be between 15 kHz and 500 kHz.\n"
        invalid_input = True
    if (phase < -360) or (phase > 360):
        message += "Phase input is invalid. Must be between -360° and 360° \n"
        invalid_input = True

    if invalid_input == True:
        sg.popup_error(message, title="Error: Invalid Input")
        return False
    else:
        return True

# change_params(amplitude, frequency, phase)
# This handles the modification of the Parameters being sent to the RP2040
# Calls the check_params function to make sure the input is valid
# Takes in the amplitude, frequency and phase as floats.
def change_params(amplitude, frequency, phase):
    valid_input = check_params(amplitude, frequency, phase)
    if valid_input == True:
        print("Parameters sent: ", amplitude,frequency, phase)
        # send_serial_message(str("Params of "+str(amplitude)+","+str(frequency)+","+str(phase)+"\n"))

###### EIT Functions

# TODO: EIT functions

# Start of the program...

window = make_window("awg")

# Create new graph based on the current data on the channel

# Attach new graph to the AWG-GRAPH and EIT-GRAPH keys.
fig_awg, ax_awg = plt.subplots()
fig_awg.set_dpi(100)
fig_awg.set_size_inches(9, 3.75)
awg_canvas_agg = FigureCanvasTkAgg(fig_awg, window['-AWG-GRAPH-'].TKCanvas)
update_graph(current_channel, ax_awg, awg_canvas_agg)
# window['-EIT-GRAPH-']

# Main event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    # Events for when mode is in AWG Mode
    if mode == 0:
        # Event for Changing Channel
        if (event == '-CHANNELNUM-'):
            change_channel(window)
            update_graph(current_channel, ax_awg, awg_canvas_agg)

        # Event for setting a Preset Wave or changing wave parameters
        if (event == '-SETPRESET-') | (event == '-SETPARAMS-'):
            try:
                amplitude_input = float(window['-AMPLITUDE-'].get())
                frequency_input = float(window['-FREQUENCY-'].get())
                phase_input     = float(window['-PHASE-'].get())
                use_preset = values['-PRESET-']
            except Exception as e:
                sg.popup_error("ERROR: \nInput is not numeric or has invalid characters.", title="Error: Invalid Input")
                print("Invalid Input:", e)
            finally:
                try:
                    channel_amplitude[current_channel] = amplitude_input
                    channel_frequencies [current_channel] = frequency_input
                    channel_phase [current_channel] = phase_input
                    channel_wavetype[current_channel] = use_preset
                    update_graph(current_channel, ax_awg, awg_canvas_agg)
                    valid_input = check_params(amplitude_input, frequency_input, phase_input)
                except NameError:
                    pass # parameters were not set'''

        # Event for Channel On/Off
        if event == '-SLIDER-':
            channel_num=window['-CHANNELTEXT-'].get().strip(string.ascii_letters).strip()
            slider_value = values['-SLIDER-']
            #
            if slider_value == 0:
                window['-STATE-'].update('Off')
                window[f'-CIRCLE{channel_num}-'].update(text_color='red')
                # Send command to turn off channel
            else:
                window['-STATE-'].update('On')
                window[f'-CIRCLE{channel_num}-'].update(text_color='green')
                # Send command to turn on channel

    #TODO: Events for EIT mode

    # Swap to EIT Mode
    if event == 'EIT':
        window['-AWG-'].update(visible=False)
        window['-EIT-'].update(visible=True)
        # swap_eit_mode(mode)
        mode=1
        menu_def_eit = [['File', ['Import', 'Export', 'Exit']],
                                ['Tools', ['EIT ✓']],
                                ['Help', ['User Manual', 'Basics']]]
        window['-CUST MENUBAR-'].update(menu_definition=menu_def_eit)

    # Swapping back to AWG Mode
    if event == 'EIT ✓':
        window['-EIT-'].update(visible=False)
        window['-AWG-'].update(visible=True)
        # swap_eit_mode(mode)

        mode=0
        menu_def = [['File', ['Import', 'Export', 'Exit']],
                                ['Tools', ['EIT']],
                                ['Help', ['User Manual', 'Basics']]]
        window['-CUST MENUBAR-'].update(menu_definition=menu_def)

window.close()
