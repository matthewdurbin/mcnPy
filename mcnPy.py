""" mcnPy: MCNP parsing and autmation fucntions. 

Authored by:
    Matthew Durbin
    Nick Grenci
    Aaron Fjeldsted
"""
import os
import numpy as np
import subprocess


def path_setup():
    """ Defines MCNP execuatable and data paths.
    
    Update to user specific MCNP instilation location
    """
    global my_env
    my_env = os.environ.copy()
    my_env["PATH"] = "\\PATH\\TO\\EXECUTABLE;" + my_env["PATH"]
    my_env["DATAPATH"] = "PATH\\To\\MCNP_DATA"
    my_env["DISPLAY"] = "localhost:0"


def tally_extract(input_file):
    """Extracts tally parameters from MCNP input.
    
    Reads MCNP input file ad extracts relevant tally data used for parsing the output file.
    
    Args:
        input_file: MCNP input
        
    Returns:
        alltallies: list of dictionaries, one for each found tally
            Dictonary entires:
                Tally Number: user defined tally number
                Tally Type: type of MCNP tally (Ex: 8 for F8 pulse height tally)
                Energy Bins: Boolean to determine if energy bins are used
                Gaussian Energy Broadening: Boolean tod etermine if GEB is used
    """
    print("Extracting tallies from MCNP Input: ", input_file)
    boolean = False
    # Keys can be added in accordance to table 3.3.5.1 in the MCNP6 manual
    # Keys are used to find unique tally information from the input file
    key = "f"
    key1 = "F"
    key2 = ":"
    key3 = "geb"
    key4 = "GEB"
    key5 = "ft"
    key6 = "FT"
    alltallies = []
    with open(input_file, "r") as inputfile:
        for num, line in enumerate(inputfile, 0):
            # Find basic tally
            if (
                line.startswith(key)
                and not line.startswith(key5)
                or line.startswith(key1)
                and not line.startswith(key6)
            ):
                boolean = True
                tally = line
                # print(line)
                tallydesignator = []
                for i in range(1, len(tally)):
                    if tally[i] == key2:
                        break
                    tallydesignator.append(tally[i])
                tallytype = int(tallydesignator[-1])
                tallynumber = "".join(map(str, tallydesignator))
            # Determine if energy bins are used
            if boolean == True:
                with open(input_file, "r") as energysearch:
                    for num, line in enumerate(energysearch, 0):
                        if line.startswith("E" + str(tallynumber)) or line.startswith(
                            "e" + str(tallynumber)
                        ):
                            energybins = True
                            break
                        else:
                            energybins = False
            # Determine if Gaussian energy broadening is used
            if boolean == True:
                print("hello")
                with open(input_file, "r") as gebsearch:
                    for num, line in enumerate(gebsearch, 0):
                        if (
                            line.startswith("ft" + str(tallynumber))
                            or line.startswith("FT" + str(tallynumber))
                        ) and (key3 in line or key4 in line):
                            print("yes")
                            geb = True
                            break
                        else:
                            geb = False
                boolean = False
                # Store tally information to a dictionary
                tallydictionary = {
                    "Tally type": tallytype,
                    "Tally number": tallynumber,
                    "Energy bins": energybins,
                    "Gaussian Energy Broadening": geb,
                }
                alltallies.append(tallydictionary)
    return alltallies


def tally_parse(output_file, tally_number, tally_type, energy_bins=False):
    """Parses a specified tally from MCNP output.
    
    Reads in MCNP output file to extract a tally based on type and number.
    If binned, extracts bin scheme, tally results, and uncertainty 
    
    Args:
        output_file: MCNP output to be parsed
        tally_number: tally number to be extracted
        tally_type: tally type to be extracted (determiens cell/surface)
        energy_bins: Boolean, extracts binned tally
        
    Returns:
        data_out: The extracted tally.
            If not binned, array of tally result and uncertainty 
            If binned, array of bins, tally results, and uncertainties 
    """
    print("Parsing Output")
    # accounts for space formating of 1/2 digit nubmers
    if len(str(tally_number)) == 1:
        tally_number = " " + str(tally_number)

    # determines if the tally is a surface or cell tally
    if tally_type == 1 or tally_type == 2:
        surface_cell = "surface  "
    else:
        surface_cell = "cell  "

    data = []
    with open(output_file, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        i = 0

        while i < len(lines):

            if "1tally       {}".format(tally_number) in lines[i]:
                tallyStart = i
                i += 1
                while i < tallyStart + 10:  # this 10 acts as a check

                    if surface_cell in lines[i]:
                        if energy_bins == False:
                            i += 1
                            data = lines[i]

                        if energy_bins == True:
                            i += 2
                            while "total" not in lines[i]:
                                data = np.append(data, lines[i])
                                i += 1

                    i += 1

            i += 1

    if energy_bins == False:
        data_out = np.zeros((1, 2))
        data_out[0] = data.split()

    if energy_bins == True:
        data_out = np.zeros((len(data), 3))
        for i in range(len(data)):
            data_out[i] = data[i].split()

    return data_out


def tally_parse_dict(output_file, tally_dict):
    """Parses a specified tally from MCNP output.
    
    Reads in MCNP output file to extract a tally based on dictonary provided by tally_extract function 
    
    Args:
        tally_dict: Tally parameters 
        
    Returns:
        data_out: The extracted tally.
            If not binned, array of tally result and uncertainty 
            If binned, array of bins, tally results, and uncertainties 
    """
    print("Parsing Output")
    tally_number = tally_dict["Tally number"]
    tally_type = tally_dict["Tally type"]
    energy_bins = tally_dict["Energy bins"]
    # accounts for space formating of 1/2 digit nubmers
    if len(str(tally_number)) == 1:
        tally_number = " " + str(tally_number)

    # determines if the tally is a surface or cell tally
    if tally_type == 1 or tally_type == 2:
        surface_cell = "surface  "
    else:
        surface_cell = "cell  "

    data = []
    with open(output_file, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        i = 0

        while i < len(lines):

            if "1tally       {}".format(tally_number) in lines[i]:
                tallyStart = i
                i += 1
                while i < tallyStart + 10:  # this 10 acts as a check

                    if surface_cell in lines[i]:
                        if energy_bins == False:
                            i += 1
                            data = lines[i]

                        if energy_bins == True:
                            i += 2
                            while "total" not in lines[i]:
                                data = np.append(data, lines[i])
                                i += 1

                    i += 1

            i += 1

    if energy_bins == False:
        data_out = np.zeros((1, 2))
        data_out[0] = data.split()

    if energy_bins == True:
        data_out = np.zeros((len(data), 3))
        for i in range(len(data)):
            data_out[i] = data[i].split()

    return data_out


def input_update(input_file, key, update):
    """Updates MCNP input.
    
    Reads in MCNP input file and updates a specific line. Saves input file.
    
    Args:
        input_file: exisitng MCNP input file 
        key: string to search for to indicate line to be changed
        update: string to replace line with
    """
    file = open(input_file, "r")
    lines = file.readlines()
    file.close()
    for i in range(len(lines)):
        if key in lines[i]:
            lines[i] = update + "\n"

    file = open(input_file, "w")
    file.writelines(lines)
    file.close()


def runMCNP(input_file, tasks_number=1):
    """ Runs an MCNP input.
    
    Args:
        input_files: existing MCNP input file
        tasks_number: number of threads to use        
    """
    print("Running MCNP")
    command = "mcnp6 i={0} tasks {1}".format(input_file, tasks_number)
    process = subprocess.Popen(command, shell=True, env=my_env)
    process.wait()


def saveOutput():
    """ Dumps entire ouput to master file.
            
    """
    print("Saving Output")
    file = open("outp", "r")
    lines = file.readlines()
    file.close()
    f = open("SavedOutp.txt", "a")
    f.write(
        "\n"
        + "============================ new run ==========================="
        + "\n"
        + "\n"
    )
    f.writelines(lines)
    f.close


def cleanWorkspace(system="windows"):
    """ Removes runtp and outp file.
            
    Args:
        system: if windows, files will be deleted. If not, the will be remobved
    """
    print("Cleaning Workspace")
    if system == "windows":
        commands = ["del runtp*", "del out*"]
    else:
        commands = ["rm runtp*", "rm out*"]
    for command in commands:
        subprocess.call(command, shell=True)


def writeData(tally_file, tally_data):
    """ Writes tally results to a single numpy file.
    
    Args:
        tally_file: master file for all tally results
        tally_data: tally data for single run
    """
    try:
        file = np.load(tally_file)
        out = np.dstack((file, tally_data))
        np.save(tally_file, out)
    except FileNotFoundError:
        np.save(tally_file, tally_data)
