# Functions that handle AWG mode, EIT mode, and serial transfers to the RP2040

import os
import io
import time
import serial
import wavegen
import numpy as np
import matplotlib.pyplot as plt
from pyeit.mesh.external import load_mesh, place_electrodes_equal_spacing
from pyeit.visual.plot import create_mesh_plot, create_plot
import pyeit.eit.protocol as protocol
from pyeit.eit.jac import JAC

# Generates the necessary objects for use in EIT mode.
# For now, these values are hardcoded.
def gen_eit_objs(n_el:int, dist_el:np.float64, is_adj:bool):
    # The example file is oriented in the following manner:
    # Left towards the X axis
    # Anterior direction towards the Y axis
    # This allows the 2D mesh to be displayed in the radiological view with no transformations
    simulation_mesh_filename = (
        "EIT/JAC/Meshes/Circle.ply"
    )
    n_electrodes = 16

    # Set up the EIT mesh and place the electrodes equally around it.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sim_mesh = load_mesh(os.path.join(current_dir, simulation_mesh_filename))
    electrode_nodes = place_electrodes_equal_spacing(sim_mesh, n_electrodes=16)
    sim_mesh.el_pos = np.array(electrode_nodes)

    # The protocol object generates the list of electrodes that we must excite and measure.
    protocol_obj = protocol.create(
        n_electrodes, dist_exc=1, step_meas=1, parser_meas="std"
    )

    # Recon
    # Set up eit object
    pyeit_obj = JAC(sim_mesh, protocol_obj)
    pyeit_obj.setup(p=0.5, lamb=0.001, method="kotre", perm=1, jac_normalized=False)

    return sim_mesh, protocol_obj, pyeit_obj

# Function that implements EIT mode
def eit_mode(ax, canvas):
    mesh, prot_obj, pyeit_obj = gen_eit_objs(16, None, None) # Options not implemented at the moment
    # Format the matrices for byte(8-bit)-level serial transfer
    int8_ext_mat = prot_obj.ex_mat.astype(dtype=np.int8)
    int8_mea_mat = prot_obj.meas_mat.astype(dtype=np.int8)
    # Explicitly put in C order, as Fortran order would cause parsing issues.
    int8_ext_bytes = int8_ext_mat.tobytes('C')
    int8_mea_bytes = int8_mea_mat.tobytes('C')
    # Send encoded text that kicks off the board's EIT mode
        # This function will automatically adjust channel 1 to start outputting a full-scale 50kHz sine with no phase shift.
        # It will also power down DDS 2, 3, 4, shut off all the DACs (except for channel 1), and restore them when EIT terminates.
            # ^ Not implemented here due to time constraints
        # main.py will be responsible for restoring the EIT channel's configuration at the end of EIT mode
    # The RP2040 will start listening for the excitation and measurement pairs
    ser = serial.Serial('COM8')
    ser.reset_input_buffer()
    ser.flush()
    sending = str.encode('start_eit()\n')
    ser.write(sending)
    ser.read(1) # Wait for the ack
    # Send the list of excitation pairs, then the list of measurement pairs
    # print (prot_obj.ex_mat)
    # print (prot_obj.meas_mat)
    ser.write(prot_obj.n_exc.to_bytes())
    ser.write(prot_obj.n_meas_tot.to_bytes())
    ser.write(int8_ext_bytes)
    ser.write(int8_mea_bytes)
    vi = np.zeros(prot_obj.n_meas_tot)
    vo = np.zeros(prot_obj.n_meas_tot)
    while True: # Come up with a way to terminate this from the GUI
        # The RP2040 will start to periodically send a bitstream made up of 16-bit voltage measurements.
        # It will continue to do so as long as there is nothing in the buffer when it goes to send the next measurement.
        # This will be how we cancel out of EIT mode, by writing something to the buffer and flushing it from the RP2040's side
        # Receive the full list of measurements in 16-bit binary form (# in number of measurements)
        # meas_vals = bulk_receive(prot_obj.n_meas_tot) # This function will block until the required number of bits are received
        # We are receiving n_meas_tot * 2 bytes because each measurement is 16-bits aka 2 bytes.
        meas_vals = ser.read(prot_obj.n_meas_tot * 2)
        meas_arr = np.frombuffer(meas_vals, dtype=np.uint16)
        # Convert from 16-bit int to floating-point with a 3.3V max.
        meas_conv = meas_arr.astype(dtype=np.float64) * (3.3 / pow(2, 16))
        # print (meas_vals, len(meas_vals))
        # print (meas_arr, len(meas_arr))
        print (meas_conv, len(meas_conv))
        vi = meas_conv
        ds_sim = pyeit_obj.solve(vi, vo, False, False)
        solution = np.real(ds_sim)
        x, y = mesh.node[:, 0], mesh.node[:, 1]
        tri = mesh.element
        ax.clear()
        # ax.plot(x,y)
        ax.tripcolor(x, y, tri, solution, alpha=1.0, cmap="viridis")
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        vo = vi
        break # Due to time constraints, I think we can only really figure out how to do this once.
        # Update the vi value, calculate and plot the new version of the EIT.

    pass

# Function that implements AWG wave updates
# Send encoded text that matches with an AWG update function on the RP2040
# Send the 1024-byte SRAM update that is generated by wavegen.py
# The device on the other end is responsible for shifting these numbers to the acceptable format (For the AD9106, this is 12-bit MSB with zeroed )
def awg_update(data:np.array, ch_n):
    # Format data to saturate a 12-bit number
    bit_depth = 12
    max = (np.power(2, bit_depth-1) - 1) # Maximum value based on bit depth (n-bit signed int)
    data *= max
    data = np.rint(data)
    data = data.astype(np.int16)
    # Set up the serial port
    ser = serial.Serial('COM8', stopbits=1)
    ser.flush()
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    # Send the kick-off command
    sending = str.encode('update_awg (' + str(len(data) * 2) + ')\n')
    ser.write(sending)
    print("Sending", len(sending), "bytes")
    # Send the data which matches the amount of bytes to transfer
    ser.read(1) # Wait for the transfer to be acked
    print("Sending", len(data.tobytes()), "bytes")
    ser.write(data.tobytes())
    ser.flush()
    ser.reset_output_buffer()
    ser.close()
    # TODO: Calculate and send a tuning gain to the RP2040 to implement amplitude scaling
    pass