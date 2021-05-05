"""mcnPy Example1: Various Point Source Locations

NaI_Cs.txt is a simple MCNP input that contains a NaI detector and 137Cs point
source. mcnPy is used to vary the location of that source, and capture an F8 
tally for each location.

 """
# improts * Ensure mcnPy.py is in your directory
import numpy as np
import mcnPy

# Define x and y coordiantes of point soruce location in cm
x = np.array((10, 20, 30, 40, 50))
y = np.array((10, 20, 30, 40, 50))

# Create a list of SDEF cards to update the input file with.
# It is recomended to copy and paste the desired line to change to insure proper
updates = []
for i in range(len(x)):
    updates = np.append(updates, "SDEF POS={} {} 0 PAR=2 ERG 0.662".format(x[i], y[i]))

# File Names
input_file = "NaI_Cs.txt"
tally_file = "tallies_example1.npy"

# set MCNP paths (Open mcnPy.py to change)
mcnPy.path_setup()

# Extract tally parameters
tally_params = mcnPy.tally_extract(input_file)

# Main loop: Run input_file for each entry in updates and extract tally
for i in range(len(updates)):
    print("Starting: Run " + str(i + 1) + " of " + str(len(updates)))
    mcnPy.input_update(input_file, "SDEF", updates[i])
    mcnPy.runMCNP(input_file, tasks_number=2)
    mcnPy.saveOutput()
    tally = mcnPy.tally_parse_dict("outp", tally_params[0])
    mcnPy.writeData(tally_file, tally)
    mcnPy.cleanWorkspace()
    print("Finished: Run " + str(i + 1) + " of " + str(len(updates)))
