## This python script reads exawatcher mpstat output files and graphs cpu usage
# It accepts a directory name and reads all files in the dir
# If you specify a begin and end time, then only the data in that timeframe is graphed
# Author : Rajeev
'''
    Modified: 06.10.2017 by Roman M.
        python3.6 compatibility
        use context manager to work with file
        for loop instead of while to iterate through a file
        Tested on Exadata x4-2 12.1.2.3.5.170418
'''


# Import python modules required
import os
import re
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Initialize the lists
l_time = []
l_pctused = []
l_outfile = 'exwmpstat.png'
l_btime = datetime.strptime('01/01/1900 00:01:00', "%m/%d/%Y %H:%M:%S")
l_etime = datetime.strptime('01/01/2020 00:01:00', "%m/%d/%Y %H:%M:%S")

# Check arguments and see if directory exists
if len(sys.argv) > 1:
    l_dirname = sys.argv[1]
    if not os.path.isdir(l_dirname):
        print("Directory {} Does not Exist".format(l_dirname))
        sys.exit()
    if (len(sys.argv) == 4):
        l_btime = datetime.strptime(sys.argv[2], "%m/%d/%Y %H:%M:%S")
        l_etime = datetime.strptime(sys.argv[3], "%m/%d/%Y %H:%M:%S")
        if (l_etime <= l_btime):
            print("End Time has to be > Begin Time")
            sys.exit()
else:
    print('Syntax : parsexwmp.py dirname ["mm/dd/yyyy hh24:mi:ss" "mm/dd/yyyy hh24:mi:ss"]')
    sys.exit()


# This function processes a single exawatcher mpstat file
# Read the file
# Skip headers
# push first column into a list named l_time
# push the 10th column into a list named l_pctused

def process_file(p_fname):
    global l_time
    global l_pctused

    l_day = None
    with open(p_fname, "r") as dat_file:
        for line in dat_file:
            if (line.startswith('Linux') or line.startswith('Average') or re.search(r'CPU', line) or not line.strip()) or line.startswith('#'):
                continue
            elif line.startswith('zzz'):
                match = re.search(r'<(.*)>', line)
                l_day = match.group(1).split()[0]
                # If the year is in YY format convert it to YYYY
                if (len(l_day) == 8):
                    l_day = datetime.strftime(datetime.strptime(l_day, "%m/%d/%y"), '%m/%d/%Y')
                continue
            elif not re.search(r'all', line):
                continue


            # Extract the time and the AM PM indicator from the row
            l_hh_mi_ss = line[0:8]
            l_am_pm = line[9:11]

            # If the AM PM indicator exists then the time is in 12Hr format else it is in the 24 Hr format
            if (l_am_pm in ('AM', 'PM')):
                l_datetime_s = '{} {} {}'.format(l_day, l_hh_mi_ss, l_am_pm)
                l_datetime = datetime.strptime(l_datetime_s, "%m/%d/%Y %I:%M:%S %p")
            else:
                l_datetime_s = '{} {}'.format(l_day, l_hh_mi_ss)
                l_datetime = datetime.strptime(l_datetime_s, "%m/%d/%Y %H:%M:%S")

            # If the time is within the range specified add row to list
            if (l_datetime >= l_btime and l_datetime <= l_etime):
                l_time.append(l_datetime)
                l_pctused.append(round(100 - float(line[82:88]), 2))





# Function to get list of files sorted by timestamp on file
def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


# The program starts here
# Get a list of files in the directory sorted by timestamp

l_files = sorted_ls(l_dirname)

for f in (l_files):
    print(('{0:20} {1:100}'.format('Processing : ', f)))
    l_fname = os.path.join(l_dirname, f)
    process_file(l_fname)

# Convert lists to numpy arrays
xv = np.array(l_time)
yv = np.array(l_pctused)

# Format and print the plot
plt.close('all')
fig, ax = plt.subplots(1)
ax.plot_date(xv, yv, 'b-')
fig.autofmt_xdate()
plt.title('Cpu Used')
plt.ylabel('Cpu Used')
plt.xlabel('HH24:MI')

plt.savefig(l_outfile)
