import PySimpleGUI as sg
import math
import string
#do pip install pyserial, pyusb and pytime
import serial.tools.list_ports
import time


# Global Variables
channel_count = 16
channel_list = [f"Channel {i}" for i in range(1,channel_count+1)]
#variables for keeping track of channel parameters and status
channel_frequencies = [f"{15.0}" for i in range(1,channel_count+1)]
channel_amplitude = [f"{0.0}" for i in range(1,channel_count+1)]
channel_phase = [f"{0.0}" for i in range(1,channel_count+1)]
channel_status= [0 for _ in range(1,channel_count+1)]

graph_size_x=900
graph_size_y=375


current_channel="Channel 1"
use_custom_titlebar = False
mode=0

# send_serial_message(message)
# Function for sending serial commands
# takes in a message for sending over serial to the RP2040
def send_serial_message(message):
    try:
        # Serial Connection Communication with the Raspberry
        # Open serial connection
        ser = serial.Serial('COM4', 9600)  # Adjust the port as needed

        # Send a message
        #message = "Hello, Raspberry Pi Pico!\n"
        ser.write(message.encode())

        timeout_seconds = 5  # Set timeout to 5 seconds
        start_time = time.time()  # Get current time
        while True:
            if time.time() - start_time > timeout_seconds:
                print("Timeout: No response from Raspberry Pi.")
                break  # Exit loop if timeout is reached
            data = ser.readline().decode().strip()
            if data:
                print("GUI Received:", data)
                break
    except serial.SerialException as e:
        print("Serial communication error:", e)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        try:
            ser.close()  # Close the serial connection
        except NameError:
            pass  # ser variable might not be defined if an exception occurred before opening the connection

# draw_axes(graph_element)
# Function for drawing the axes in the Graph element of the GUI
# Takes in the Graph, to apply the changes
def draw_axes(graph_element):
    # Define the graph size
    graph_size = (graph_size_x, graph_size_y)

    # Define the time and voltage ranges
    time_range_ms = 10
    voltage_range_volts = 1.7

    # Draw X-axis with time in milliseconds
    graph_element.draw_line((20, graph_size[1] // 2), (graph_size[0], graph_size[1] // 2), color='black')
    graph_element.draw_text('0 ms', (20, 10), color='black')
    # create a loop to display time multiple times
    graph_element.draw_text(f'{time_range_ms} ms', (graph_size[0] - 30, 10), color='black')
    graph_element.draw_line((20, graph_size[1]-20), (graph_size[0], graph_size[1] -20), color='black')
    graph_element.draw_line((20, 40), (graph_size[0], 40), color='black')

    # Draw Y-axis with voltage in Volts
    graph_element.draw_line((20, 0), (20, graph_size[1]), color='black')
    graph_element.draw_text('0V', (10, graph_size[1] // 2), color='black')
    graph_element.draw_text(f'{voltage_range_volts}V', (10, graph_size[1] - 20), color='black')
    graph_element.draw_text(f'-{voltage_range_volts}V', (10, 40), color='black')

# make_window()
# This function draws the window using the layouts 
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
                *[[sg.Col([[sg.Text(f'Channel {i}'),sg.Text('●', size=(1, 1), text_color='red',key=f'-CIRCLE{i}-')]]) ]for i in range(1,channel_count+1)],
                ]

    #  Right side layout
    parameter_layout =[[name('Frequency(kHz)'), sg.Spin([round(i * 0.1, 1) for i in range(150, 5000)],initial_value=15.0, s=(15,2), k='-FREQUENCY-', enable_events=True)],
                       [name('Amplitude(V)'), sg.Spin([round(i * 0.1, 1) for i in range(0, 150)],initial_value=0.0, s=(15,2), k='-AMPLITUDE-'),sg.Button('Set',expand_x=True, enable_events=True, k='-SETPARAMS-')],
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
    frame_layout = [[sg.Graph((graph_size_x+80, graph_size_y+20), (0,20), (graph_size_x,graph_size_y),background_color='white', k='-GRAPH-')],
                    [
                       sg.Column([[sg.Frame("Parameters",parameter_layout)]]),
                       sg.Column([[sg.Frame("Presets",preset_layout)]]),
                     #  sg.Column([[sg.Frame("Function",function_layout,expand_y=True)]]),
                       sg.Column([[sg.Frame("On/Off",button_layout,expand_y=True)]])
                    ]
                 ]
    ## Layout for the right side of the Interface; Includes the Graph, Channel name and all the parameter controls
    layout_r  = [[sg.Text(current_channel, k='-CHANNELTEXT-'),sg.Push(),sg.Combo(channel_list, default_value=current_channel, size=(15,22), enable_events=True, readonly=True, k='-CHANNELNUM-',)],
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
                            [sg.Frame("",[[sg.Graph((450,450),(0,450),(450,0),background_color='white',border_width=1)]])]
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



# draw_sine_wave(graph_element)
# Function for drawing a preset sine wave in the Graph element of the GUI
# Takes in the Graph, to apply the changes
# TODO: take in parameters to change the sine wave
def draw_sine_wave(graph_element):
    graph_size = (graph_size_x, graph_size_y)

    amplitude = graph_size[1] // 3
    frequency = 0.02
    step = 5  # Adjust the step size for the number of line segments

    points = []
    for x in range(0, graph_size[0], step):
        y = amplitude * math.sin(frequency * x)
        points.append((x+20, graph_size[1] // 2 - y))

    # Draw the sine wave using line segments
    for i in range(len(points) - 1):
        graph_element.draw_line(points[i], points[i + 1], color='blue')

# draw_graph(graph_element,preset)
# Function for drawing in the graph element of the GUI
# Takes in the graph element to be modified, and the preset wave as a string to draw
def draw_graph(graph_element,preset):
    if preset == 'Sine':
        draw_sine_wave(graph_element)
    elif preset == 'Square':
        graph_element.draw_line((10, 10), (100, 100))  # Example line drawn in the graph
    #graph_element.draw_line((10, 10), (100, 100))  # Example line drawn in the graph



# change_channel(window)
# This function handles all events for when a channel is changes
# Includes saving the current parameters and calling the function for sending a serial message
# and then retrieving the parameters for the channel that was switched to.
# takes in the window to access the elements
def change_channel(window):
    #Save the current parameters
    prev_channel=window['-CHANNELTEXT-'].get()
    prev_num= int(prev_channel.strip(string.ascii_letters))
    channel_frequencies[prev_num-1]=window['-FREQUENCY-'].get()
    channel_amplitude[prev_num-1]=window['-AMPLITUDE-'].get()
    channel_phase[prev_num-1]=window['-PHASE-'].get()
    slider_value = values['-SLIDER-']
    if slider_value == 0:
        channel_status[prev_num-1]=0
    else:
        channel_status[prev_num-1]=1

    # Send message to Raspberry Pi Pico
    send_serial_message("Hello, Raspberry Pi Pico!\n")
    #Update the window with the new channel parameters
    current_channel = values['-CHANNELNUM-']
    window['-CHANNELTEXT-'].update(str(current_channel))
    channel_num=int(current_channel.strip(string.ascii_letters))

    window['-FREQUENCY-'].update(str(channel_frequencies[channel_num-1]))
    window['-AMPLITUDE-'].update(str(channel_amplitude[channel_num-1]))
    window['-PHASE-'].update(str(channel_phase[channel_num-1]))
    if channel_status[channel_num-1] == 0:
        window['-SLIDER-'].update(value=0)
        window['-STATE-'].update('Off')
    else:
        window['-SLIDER-'].update(value=1)
        window['-STATE-'].update('On')

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
        send_serial_message(str("Params of "+str(amplitude)+","+str(frequency)+","+str(phase)+"\n"))

# set_preset_wave(wave)
# Function for when a preset wave is set
# Takes in the wave to be sent to the RP2040
def set_preset_wave(wave):
    print(wave+" preset used.")
    send_serial_message("Preset "+wave+" set.\n")








# swap_eit_mode(mode)
# handles swapping From AWG to EIT and vice-versa
# Sends the Change to the RP2040
def swap_eit_mode(mode):
    print("Mode swapped!")
    if mode == 0:
        send_serial_message("Swapped to EIT mode\n")
    else:
        send_serial_message("Swapped to AWG mode\n")

###### EIT Functions



# Start of the program...

window = make_window("awg")

graph = window['-GRAPH-']  # Accessing the Graph element

if graph:  # Checking if the Graph element is present
    draw_axes(graph)


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    # Events for when mode is in AWG Mode
    if mode == 0:
        # Event for setting a Preset Wave
        if event == '-SETPRESET-':
            use_preset = values['-PRESET-']
            draw_graph(window['-GRAPH-'],use_preset)
            set_preset_wave(use_preset)
        # Event for Changing Channel
        if event == '-CHANNELNUM-':
            change_channel(window)
            window['-GRAPH-'].erase()
            graph = window['-GRAPH-']
            draw_axes(graph)
            #TODO: call an update function in the future for the graph

        # Event for Channel On/Off
        if event == '-SLIDER-':
            channel_num=window['-CHANNELTEXT-'].get().strip(string.ascii_letters).strip()
            slider_value = values['-SLIDER-']
            # 
            if slider_value == 0:
                window['-STATE-'].update('Off')
                window[f'-CIRCLE{channel_num}-'].update(text_color='red')
            else:
                window['-STATE-'].update('On')
                window[f'-CIRCLE{channel_num}-'].update(text_color='green')

        # Event for setting parameters
        if event == '-SETPARAMS-':
            try:
                amplitude_input=window['-AMPLITUDE-'].get()
                frequency_input=window['-FREQUENCY-'].get()
                phase_input=window['-PHASE-'].get()


                amplitude = float(amplitude_input)#.strip(string.ascii_letters).strip()
                frequency = float(frequency_input)#.strip(string.ascii_letters).strip()
                phase = float(phase_input)#.strip(string.ascii_letters).strip()

            except Exception as e:
                sg.popup_error("ERROR: \nInput is not numeric or has invalid characters.", title="Error: Invalid Input")
                print("Invalid Input:", e)
            finally:
                try:
                    change_params(amplitude,frequency,phase)
                except NameError:
                    pass # parameters were not set

    #TODO: Events for EIT mode
             
    # Swap to EIT Mode
    if event == 'EIT':
        window['-AWG-'].update(visible=False)
        window['-EIT-'].update(visible=True)
        swap_eit_mode(mode)
        mode=1
        menu_def_eit = [['File', ['Import', 'Export', 'Exit']],
                                ['Tools', ['EIT ✓']],
                                ['Help', ['User Manual', 'Basics']]]
        window['-CUST MENUBAR-'].update(menu_definition=menu_def_eit)

    # Swapping back to AWG Mode
    if event == 'EIT ✓':
        window['-EIT-'].update(visible=False)
        window['-AWG-'].update(visible=True)
        swap_eit_mode(mode)

        mode=0
        menu_def = [['File', ['Import', 'Export', 'Exit']],
                                ['Tools', ['EIT']],
                                ['Help', ['User Manual', 'Basics']]]
        window['-CUST MENUBAR-'].update(menu_definition=menu_def)


window.close()
