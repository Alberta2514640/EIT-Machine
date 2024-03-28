import os
import io
import numpy as np
import matplotlib.pyplot as plt
from pyeit.mesh.external import load_mesh, place_electrodes_equal_spacing
from pyeit.visual.plot import create_mesh_plot, create_plot
import pyeit.eit.protocol as protocol
from pyeit.eit.jac import JAC
from pyeit.eit.fem import EITForward


def main():
    # The example file is oriented in the following manner:
    # Left towards the X axis
    # Anterior direction towards the Y axis
    # This allows the 2D mesh to be displayed in the radiological view with no transformations
    simulation_mesh_filename = (
        "Meshes/Circle.ply"
    )
    n_electrodes = 16

    # Set up the EIT mesh and place the electrodes equally around it.
    # It looks like this only needs to be done once.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sim_mesh = load_mesh(os.path.join(current_dir, simulation_mesh_filename))
    electrode_nodes = place_electrodes_equal_spacing(sim_mesh, n_electrodes=16)
    sim_mesh.el_pos = np.array(electrode_nodes)

    fig, ax = plt.subplots()
    create_mesh_plot(
        ax, sim_mesh, electrodes=electrode_nodes, coordinate_labels="radiological"
    )

    # The protocol object generates the list of electrodes that we must excite and measure.
    # We could possible save time on the implementation by just hardcoding this into the RP2040 script.
    # I think this is the best way forward, considering our time constraints.
    protocol_obj = protocol.create(
        n_electrodes, dist_exc=1, step_meas=1, parser_meas="std"
    )

    # Recon
    # Set up eit object
    pyeit_obj = JAC(sim_mesh, protocol_obj)
    pyeit_obj.setup(p=0.5, lamb=0.001, method="kotre", perm=1, jac_normalized=False)

    # Loop starts here

    # Insert new data here.

    fwd = EITForward(sim_mesh, protocol_obj)
    vh = fwd.solve_eit(perm=1)
    vi = fwd.solve_eit(perm=sim_mesh.perm)
    # ^ These are 208-element arrays that represent the voltage differences of each pair.
    # Instead of the solve_eit simulated data here, we should put in real data from the device.

    # # Dynamic solve data
    ds_sim = pyeit_obj.solve(v1=vi, v0=vh, normalize=False)
    solution = np.real(ds_sim)


    fig, ax = plt.subplots()
    create_plot(
        ax,
        solution,
        pyeit_obj.mesh,
        electrodes=electrode_nodes,
        coordinate_labels="radiological",
    )

    vi = vh # Shift the current data back and refill with fresh data at the start of the loop
    # plt.savefig('JAC.png')


if __name__ == "__main__":
    main()
