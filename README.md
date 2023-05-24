# picoAWG
Arbitrary Waveform Generator for the Raspberry Pi Pico 16 Channels

## AWG Desktop Application
Desktop application to interface with Arbitrary Waveform Generator

TODO
- Implement Control of 16 Channels to Control Amplitude, Frequency, Offset 
- Read Back Output with Monitor to see the output
- Control LED s as needed

## PCB Design 
The board design for the waveform generator

TODO
- Update PCB design to include RP2040 directly and a cheaper OP AMP
- Update PCB design to shrink the design down to a more reasonable size and add a small status display beyond the current 5 status LEDs.


## RP2040 Code 
The code loaded onto the Pi Pico. 

TODO
- Monitor Output Needs to be fixed to setup the output
    - Write Values to the Output and Read Corresponding Voltage Changes 
- Control over channels 1-16 with Output Adjustments
    - Split the ADC control and the communication/ led control to seperate cores communicating between one another.
    - Utilize the PIO to drive the SPI peripheral and set the outputs appropriately. 
- Add functions to set the Configuration Register, Offset, Calibration, Data, Registers 