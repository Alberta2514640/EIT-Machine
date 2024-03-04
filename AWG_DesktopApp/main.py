import PySimpleGUI as sg
import math
import string

#do pip install serial and pytime
import serial
import time


channel_count = 16
channel_list = [f"Channel {i}" for i in range(1,channel_count+1)]
#add a variable for keeping track of channel parameters and status
channel_frequencies = [f"{i} Hz" for i in range(1,channel_count+1)]
channel_amplitude = [f"{i} V" for i in range(1,channel_count+1)]
channel_phase = [f"{i} °" for i in range(1,channel_count+1)]
channel_status= [0 for _ in range(1,channel_count+1)]

graph_size_x=900
graph_size_y=375


current_channel="Channel 1"
use_custom_titlebar = False
# add variables for default values for parameters
mode=0

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


def make_window(mode, theme=None):

    NAME_SIZE = 16

    def name(name):
        #dots = NAME_SIZE-len(name)-2
        return sg.Text(name + ' ' + ':', size=(NAME_SIZE,1), justification='r',pad=(0,0), font='Courier 10')
        #return sg.Text(name + ' ' + '•'*dots, size=(NAME_SIZE,1), justification='r',pad=(0,0), font='Courier 10')

    sg.theme(theme)

    # Layouts
    # This is the left side layout
    ##### Standard Waveform Generator Layout
    layout_l = [[ sg.Text('Status',font='Courier 16')],
                [ sg.HSep()],
                #[ sg.Text('Channel 1',font='Courier 10')],
                *[[sg.Col([[sg.Text(f'Channel {i}'),sg.Text('●', size=(1, 1), text_color='red',key=f'-CIRCLE{i}-')]]) ]for i in range(1,channel_count+1)],
              #  [ sg.Input(s=15)],
              #  [ sg.Multiline(s=(15,2))],
               # [ sg.Output(s=(15,2))],
                #[ sg.Combo(sg.theme_list(), default_value=sg.theme(), s=(15,22), enable_events=True, readonly=True, k='-COMBO-')]
                ]
    
    #  Right side layout 
    parameter_layout =[[name('Frequency'), sg.Spin(['0 Hz',], s=(15,2), k='-FREQUENCY-')],
                       [name('Amplitude'), sg.Spin(['0 V',], s=(15,2), k='-AMPLITUDE-')],
                       [name('Phase Shift'), sg.Spin(['0 °',], s=(15,2),k='-PHASE-')],
                       #[name('Offset'), sg.Spin(['0 V',], s=(15,2))]
                       ]
    preset_layout =[[name('Presets'), sg.Combo(['Sine','Square','Triangle'], default_value='Sine', s=(15,22), enable_events=False, readonly=True, k='-PRESET-')],
                       [sg.Button('Use',expand_x=True, enable_events=True, k='-SETPRESET-')],
                       ]    
    
    function_layout =[[name('Input/Output:'), sg.Combo(['Output','Input'], default_value='Output', s=(15,22), enable_events=False, readonly=True, k='-FUNCTION-')],
                      [name('Mode:'), sg.Combo(['DAC','ADC'], default_value='Output', s=(15,22), enable_events=False, readonly=True, k='-MODE-')]
                      #[sg.Push(),sg.Checkbox('EIT Mode')],
                       #[sg.Button('Set',expand_x=True, enable_events=True, k='-SETPRESET-')],
                       ]    

    button_layout =[[sg.Slider(range=(0, 1), default_value=0, orientation='h', size=(8, 40), key='-SLIDER-', enable_events=True,tooltip='Toggle On/Off',disable_number_display=True),

                        ],
                        [sg.Text('State: '), sg.Text('Off', size=(5,1), key='-STATE-'),]
                ]

    frame_layout = [[sg.Graph((graph_size_x+80, graph_size_y+20), (0,20), (graph_size_x,graph_size_y),background_color='white', k='-GRAPH-')],
                    [
                       sg.Column([[sg.Frame("Parameters",parameter_layout)]]),
                       sg.Column([[sg.Frame("Presets",preset_layout)]]),
                       sg.Column([[sg.Frame("Function",function_layout,expand_y=True)]]),
                       sg.Column([[sg.Frame("On/Off",button_layout,expand_y=True)]])
                    ]
                 ]
    layout_r  = [[sg.Text(current_channel, k='-CHANNELTEXT-'),sg.Push(),sg.Combo(channel_list, default_value=current_channel, size=(15,22), enable_events=True, readonly=True, k='-CHANNELNUM-',)],
                 [sg.Frame("Waveform",frame_layout)]]
    #############################################
    ### EIT Layout ###
    layout_eit = [[name('Electrodes'), sg.Spin(['0 Hz',], s=(15,2), k='-ELECTRODES-')],
                       [name('Distance Between Electrodes'), sg.Spin(['0 V',], s=(15,2), k='-ELECTRODESD-')],
                       [name('Amplitude'), sg.Spin(['0 °',], s=(15,2),k='-AMPLITUDE2-')],
                       [name('Frequency of Injected Current'), sg.Spin(['0 °',], s=(15,2),k='-FREQUENCY2-')],
                       [name('Voltage Out'), sg.Spin(['0 °',], s=(15,2),k='-VOLTAGEOUT-')]]



    ###################
    
    ### Window drawing ###
    layout = [ [sg.Menu([['File', ['Import','Export','Exit']], ['Tools', ['EIT', ]],['Help', ['User Manual', 'Basics']]],  k='-CUST MENUBAR-',p=0)],
              [sg.Col(layout_l,size=(None,None),expand_x=True, expand_y=True, pad=(0,0), ), sg.VSep(), sg.Col(layout_r,vertical_alignment='top')]]
    
    eit_window_layout = [ [sg.Menu([['File', ['Import','Export','Exit']], ['Tools', ['EIT', ]],['Help', ['User Manual', 'Basics']]],  k='-CUST MENUBAR-',p=0)],
              [ sg.Col(layout_eit,vertical_alignment='top')]]    
    
    if mode=="eit":
        main_layout=[eit_window_layout]
    else:
        main_layout=[layout]

    window = sg.Window('16 Channel Arbitrary Waveform Generator', main_layout, finalize=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, keep_on_top=False, use_custom_titlebar=use_custom_titlebar)


    return window

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

def draw_graph(graph_element,preset):
    if preset == 'Sine':
        draw_sine_wave(graph_element)
    elif preset == 'Square':
        graph_element.draw_line((10, 10), (100, 100))  # Example line drawn in the graph
    #graph_element.draw_line((10, 10), (100, 100))  # Example line drawn in the graph



#
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

    serialConnection= serial.Serial('COM3',9600, timeout=1)
    serialConnection.write(b'Hello from GUI\n')

    timeout_seconds = 5  # Set timeout to 5 seconds
    start_time = time.time()  # Get current time
    while True:
        if time.time() - start_time > timeout_seconds:
            print("Timeout: No response from Raspberry Pi.")
            break  # Exit loop if timeout is reached
        data = serialConnection.read(10)#.decode().strip()
        if data:
            print("GUI Received:", data)
            break  # Exit loop if data is received
    '''
    # Serial Connection Communication with the Raspberry
    serialConnection.write(b'Hello from GUI\n')
    while True:
        data = serialConnection.readline().decode().strip()  # Read a line of data with a timeout
        if data:
            print("Received:", data)
            break
    '''
    serialConnection.close()
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

# Start of the program...




window = make_window("awg")

graph = window['-GRAPH-']  # Accessing the Graph element

if graph:  # Checking if the Graph element is present
    draw_axes(graph)


while True:
    event, values = window.read()
   # sg.popup(event, values)                     # show the results of the read in a popup Window
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    #if event != sg.WIN_CLOSED:  # Check if the event is not related to window closure
    #    sg.popup(event, values) 

    if mode == 0:
        ###if values['-COMBO-'] != sg.theme():
        ###    sg.theme(values['-COMBO-'])
        ###    window.close()
        ###    window = make_window("awg")
        if event == '-USE CUSTOM TITLEBAR-':
            use_custom_titlebar = values['-USE CUSTOM TITLEBAR-']
            window.close()
            window = make_window("awg")
        if event == '-SETPRESET-':
            use_preset = values['-PRESET-']
            draw_graph(window['-GRAPH-'],use_preset)  
        if event == '-CHANNELNUM-':
            change_channel(window)
            #current_channel = values['-CHANNELNUM-']
            #window['-CHANNELTEXT-'].update(str(current_channel))
            window['-GRAPH-'].erase()
            graph = window['-GRAPH-']
            draw_axes(graph)
            #call an update function in the future

        # Event for Channel On/Off
        if event == '-SLIDER-': 
            channel_num=window['-CHANNELTEXT-'].get().strip(string.ascii_letters).strip()
            slider_value = values['-SLIDER-']
            if slider_value == 0:
                window['-STATE-'].update('Off')
                window[f'-CIRCLE{channel_num}-'].update(text_color='red')
            else:
                window['-STATE-'].update('On')
                window[f'-CIRCLE{channel_num}-'].update(text_color='green')

    if event == 'EIT':
        #window.close()
        window=make_window("eit")
       # mode=1
        #menu_def_eit = [['File', ['Import', 'Export', 'Exit']],
        #                        ['Tools', ['EIT ✓']],
        #                        ['Help', ['User Manual', 'Basics']]]
        #window['-CUST MENUBAR-'].update(menu_definition=menu_def_eit)      
"""
    if event == 'EIT ✓':
        window.close()
        window=make_window("awg")
        mode=0
        menu_def = [['File', ['Import', 'Export', 'Exit']],
                                ['Tools', ['EIT']],
                                ['Help', ['User Manual', 'Basics']]]
        window['-CUST MENUBAR-'].update(menu_definition=menu_def)  
"""

window.close()
