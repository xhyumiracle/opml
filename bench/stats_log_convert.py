import csv
import re
import os
# Convert m:ss format to seconds
def time_to_seconds(time_str):
    minutes, seconds = map(float, time_str.split(':'))
    return minutes * 60 + seconds

def convert_model_log_dir(log_dir, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header row

        csv_writer.writerow([
            'Node ID', 'Mips Steps',
            'Phase 1 NonSysIO time (sec)', 'Phase 1 vmIOTime', 'Phase 1 vmExecTime', 'Phase 1 sysIOTime','Phase 1 Peak Mem (kb)',
            'Phase 2 NonSysIO time (sec)', 'Phase 2 vmIOTime', 'Phase 2 vmExecTime', 'Phase 2 sysIOTime','Phase 2 Peak Mem (kb)'
        ])
        for nodeid in range(10000):
          file_path = os.path.join(log_dir, 'node_' + str(nodeid) + '.log')
          if os.path.exists(file_path):
              row = extract_row(file_path)
              csv_writer.writerow([nodeid]+row)
          else: # end of valid nodeid log files
              continue
    
    print(f"Converted {log_dir} to {output_file}")

# nonSysIOTime: 0.175505551
# vmIOTime: 1.6996e-05
# vmExecTime: 0.141659372
def extract_row(log_file):
    # Regular expressions to match patterns in the log
    mips_steps_pattern = re.compile(r'reach the final state, total step: (\d+), target: -1')
    # user_time_pattern = re.compile(r'User time \(seconds\): (\d+\.\d+)')
    # system_time_pattern = re.compile(r'System time \(seconds\): (\d+\.\d+)')
    nonSysIOTime_pattern = re.compile(r'nonIOTime: (\d+\.\d+([eE][+-]?\d+)?)')
    vmIOTime_pattern = re.compile(r'vmIOTime: (\d+\.\d+([eE][+-]?\d+)?)')
    vmExecTime_pattern = re.compile(r'vmExecTime: (\d+\.\d+([eE][+-]?\d+)?)')
    sysIOTime_pattern = re.compile(r'sysIOTime: (\d+\.\d+([eE][+-]?\d+)?)')
    elapsed_time_pattern = re.compile(r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\d+:\d+\.\d+)')
    max_resident_set_pattern = re.compile(r'Maximum resident set size \(kbytes\): (\d+)')
    
    mips_steps = None
    # user_time = None
    # system_time = None
    phase = [{"nonSysIOTime": None, "vmExecTime": None, "vmIOTime": None, "sysIOTime": None, "max_resident_set": None},
             {"nonSysIOTime": None, "vmExecTime": None, "vmIOTime": None, "sysIOTime": None, "max_resident_set": None},]
    # Read and process the log
    phase_count = 0

    with open(log_file, 'r') as f:
        for line in f:
            line=line.strip()

            # Match the log data
            mips_steps_match = mips_steps_pattern.match(line)
            # user_time_match = user_time_pattern.match(line)
            # system_time_match = system_time_pattern.match(line)
            elapsed_time_match = elapsed_time_pattern.match(line)
            nonSysIOTime_match = nonSysIOTime_pattern.match(line)
            vmIOTime_match = vmIOTime_pattern.match(line)
            vmExecTime_match = vmExecTime_pattern.match(line)
            sysIOTime_match = sysIOTime_pattern.match(line)
            max_resident_set_match = max_resident_set_pattern.match(line)

            # if line == "reach the final state, total step: 424746, target: -1".strip():
            #     print ('000000000000', reach_final_match)
            # if reach_final_match:
            #     print ('000000000000')
            if mips_steps_match:
                mips_steps = mips_steps_match.group(1)
                phase_count = 1
            # elif user_time_match:
            #     user_time = user_time_match.group(1)
            # elif system_time_match:
            #     system_time = system_time_match.group(1)
            elif elapsed_time_match:
                elapsed_time = time_to_seconds(elapsed_time_match.group(1))
                phase[phase_count]["nonSysIOTime"] = phase[phase_count]["nonSysIOTime"] or elapsed_time
            elif nonSysIOTime_match:
                nonSysIOTime = nonSysIOTime_match.group(1)
                phase[phase_count]["nonSysIOTime"] = nonSysIOTime
            elif vmIOTime_match:
                vmIOTime = vmIOTime_match.group(1)
                phase[phase_count]["vmIOTime"] = vmIOTime
            elif vmExecTime_match:
                vmExecTime = vmExecTime_match.group(1)
                phase[phase_count]["vmExecTime"] = vmExecTime
            elif sysIOTime_match:
                sysIOTime = sysIOTime_match.group(1)
                phase[phase_count]["sysIOTime"] = sysIOTime
            
            elif max_resident_set_match:
                max_resident_set = max_resident_set_match.group(1)
                phase[phase_count]["max_resident_set"] = max_resident_set

    return [mips_steps, 
            phase[0]["nonSysIOTime"], phase[0]["vmIOTime"], phase[0]["vmExecTime"], phase[0]["sysIOTime"], phase[0]["max_resident_set"],
            phase[1]["nonSysIOTime"], phase[1]["vmIOTime"], phase[1]["vmExecTime"], phase[1]["sysIOTime"], phase[1]["max_resident_set"],]


# # Define input and output files
# log_file = 'logs/challenge_llama_layered.log'  # Replace with your actual log file name
# # log_file = 'logs/test.log'  # Replace with your actual log file name
# output_file = 'logs/challenge_llama_layered.csv'  # Replace with your desired output CSV file name

# Define the folder path
folder_path = 'logs/stats'

# Loop through all files in the folder
for date_dir in os.listdir(folder_path):
    if not os.path.isfile(date_dir) and date_dir.startswith('202'): # date format: 202x-xx-xx
        for model_log_dir in os.listdir(os.path.join(folder_path, date_dir)):
            model_log_dir_full = os.path.join(folder_path, date_dir, model_log_dir)
            
            # if model_log_dir != "MNIST": # skip, for test, can rm
            #     continue
            
            model_csv = os.path.join(folder_path, model_log_dir + '-' + date_dir + '.csv')
            convert_model_log_dir(model_log_dir_full, model_csv)
    # Check if it's a file (not a directory)
    # if os.path.isfile(filepath) and filename.endswith('.log'):
    #     convert_log(filepath, filepath+'.csv')
# convert_log(log_file, output_file)