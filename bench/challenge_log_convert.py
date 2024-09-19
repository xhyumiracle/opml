import csv
import re
import os
# Convert m:ss format to seconds
def time_to_seconds(time_str):
    minutes, seconds = map(float, time_str.split(':'))
    return minutes * 60 + seconds

def convert_log(log_file, output_file):
    # Regular expressions to match patterns in the log
    # user_time_pattern = re.compile(r'User time \(seconds\): (\d+\.\d+)')
    # system_time_pattern = re.compile(r'System time \(seconds\): (\d+\.\d+)')
    elapsed_time_pattern = re.compile(r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\d+:\d+\.\d+)')
    # mips_steps_pattern = re.compile(r'reach the final state, total step: (\d+), target: -1')
    step_pattern = re.compile(r'--- STEP (\d+)')
    nonSysIOTime_pattern = re.compile(r'nonIOTime: (\d+\.\d+([eE][+-]?\d+)?)')
    vmIOTime_pattern = re.compile(r'vmIOTime: (\d+\.\d+([eE][+-]?\d+)?)')
    vmExecTime_pattern = re.compile(r'vmExecTime: (\d+\.\d+([eE][+-]?\d+)?)')
    sysIOTime_pattern = re.compile(r'sysIOTime: (\d+\.\d+([eE][+-]?\d+)?)')
    max_resident_set_pattern = re.compile(r'Maximum resident set size \(kbytes\): (\d+)')

    # Read and process the log
    with open(log_file, 'r') as f, open(output_file, 'w', newline='') as csvfile:
        
        csv_writer = csv.writer(csvfile)
        # Write the header row
        csv_writer.writerow([
            'STEP number', 'layer num', 'searching step',
            'Challenger 0 NonSysIO time (sec)', 'Challenger 0 vmIOTime', 'Challenger 0 vmExecTime', 'Challenger 0 sysIOTime','Challenger 0 Peak Mem (kb)',
            'Challenger 1 NonSysIO time (sec)', 'Challenger 1 vmIOTime', 'Challenger 1 vmExecTime', 'Challenger 1 sysIOTime','Challenger 1 Peak Mem (kb)',
            # 'Challenger 0 User time (seconds)', 'Challenger 0 System time (seconds)', 'Challenger 0 Elapsed time', 'Challenger 0 Maximum resident set size (kb)',
            # 'Challenger 1 User time (seconds)', 'Challenger 1 System time (seconds)', 'Challenger 1 Elapsed time', 'Challenger 1 Maximum resident set size (kb)'
        ])

        current_step = None
        layer_num = None
        searching_step = None
        # challenger0 = {'user_time': None, 'system_time': None, 'elapsed_time': None, 'max_resident_set': None}
        # challenger1 = {'user_time': None, 'system_time': None, 'elapsed_time': None, 'max_resident_set': None}

        challenger = [{"nonSysIOTime": None, "vmExecTime": None, "vmIOTime": None, "sysIOTime": None, "max_resident_set": None},
                      {"nonSysIOTime": None, "vmExecTime": None, "vmIOTime": None, "sysIOTime": None, "max_resident_set": None},]
        challengerID = 0

        for line in f:
            line=line.strip()
            step_match = step_pattern.match(line)
            if step_match:
                if current_step is not None:# and len(challenge_data) == 2:
                    # Write the row for the previous step
                    csv_writer.writerow([
                        current_step, layer_num, searching_step,
                        # challenger0['user_time'], challenger0['system_time'], challenger0['elapsed_time'], challenger0['max_resident_set'],
                        # challenger1['user_time'], challenger1['system_time'], challenger1['elapsed_time'], challenger1['max_resident_set']
                        challenger[0]["nonSysIOTime"], challenger[0]["vmIOTime"], challenger[0]["vmExecTime"], challenger[0]["sysIOTime"], challenger[0]["max_resident_set"],
                        challenger[1]["nonSysIOTime"], challenger[1]["vmIOTime"], challenger[1]["vmExecTime"], challenger[1]["sysIOTime"], challenger[1]["max_resident_set"],
                    ])
                # Reset for the next step
                current_step = step_match.group(1)
                # challenger0 = {'user_time': None, 'system_time': None, 'elapsed_time': None, 'max_resident_set': None}
                # challenger1 = {'user_time': None, 'system_time': None, 'elapsed_time': None, 'max_resident_set': None}
                challenger = [{"nonSysIOTime": None, "vmExecTime": None, "vmIOTime": None, "sysIOTime": None, "max_resident_set": None},
                            {"nonSysIOTime": None, "vmExecTime": None, "vmIOTime": None, "sysIOTime": None, "max_resident_set": None},]
                continue
            
            if 'current layer:' in line:
                layer_num = line.split(':')[-1].strip()
            elif 'searching step:' in line:
                searching_step = line.split(':')[-1].strip()
            elif 'isChallenger:  true' in line:
                # challenger = challenger1
                challengerID = 1
            elif 'isChallenger:  false' in line:
                # challenger = challenger0
                challengerID = 0
            elif 'search is done' in line:
                # end of challenge, no need to record this step
                return
            
            # Match the performance data
            # user_time_match = user_time_pattern.match(line)
            # system_time_match = system_time_pattern.match(line)
            elapsed_time_match = elapsed_time_pattern.match(line)
            elapsed_time_match = elapsed_time_pattern.match(line)
            nonSysIOTime_match = nonSysIOTime_pattern.match(line)
            vmIOTime_match = vmIOTime_pattern.match(line)
            vmExecTime_match = vmExecTime_pattern.match(line)
            sysIOTime_match = sysIOTime_pattern.match(line)
            max_resident_set_match = max_resident_set_pattern.match(line)

            # if user_time_match:
            #     challenger['user_time'] = user_time_match.group(1)
            # elif system_time_match:
            #     challenger['system_time'] = system_time_match.group(1)
            # elif elapsed_time_match:
            #     challenger['elapsed_time'] = time_to_seconds(elapsed_time_match.group(1))
            # elif max_resident_set_match:
            #     challenger['max_resident_set'] = max_resident_set_match.group(1)

            if elapsed_time_match:
                elapsed_time = time_to_seconds(elapsed_time_match.group(1))
                challenger[challengerID]["nonSysIOTime"] = challenger[challengerID]["nonSysIOTime"] or elapsed_time
            elif nonSysIOTime_match:
                nonSysIOTime = nonSysIOTime_match.group(1)
                challenger[challengerID]["nonSysIOTime"] = nonSysIOTime
            elif vmIOTime_match:
                vmIOTime = vmIOTime_match.group(1)
                challenger[challengerID]["vmIOTime"] = vmIOTime
            elif vmExecTime_match:
                vmExecTime = vmExecTime_match.group(1)
                challenger[challengerID]["vmExecTime"] = vmExecTime
            elif sysIOTime_match:
                sysIOTime = sysIOTime_match.group(1)
                challenger[challengerID]["sysIOTime"] = sysIOTime
            
            elif max_resident_set_match:
                max_resident_set = max_resident_set_match.group(1)
                challenger[challengerID]["max_resident_set"] = max_resident_set

        # Write the last step
        if current_step is not None:
            # csv_writer.writerow([
            #     current_step, layer_num, searching_step,
            #     challenger0['user_time'], challenger0['system_time'], challenger0['elapsed_time'], challenger0['max_resident_set'],
            #     challenger1['user_time'], challenger1['system_time'], challenger1['elapsed_time'], challenger1['max_resident_set']
            # ])
            csv_writer.writerow([
                current_step, layer_num, searching_step,
                challenger[0]["nonSysIOTime"], challenger[0]["vmIOTime"], challenger[0]["vmExecTime"], challenger[0]["sysIOTime"], challenger[0]["max_resident_set"],
                challenger[1]["nonSysIOTime"], challenger[1]["vmIOTime"], challenger[1]["vmExecTime"], challenger[1]["sysIOTime"], challenger[1]["max_resident_set"],
            ])

    print(f"Converted {log_file} to {output_file}")


# # Define input and output files
# log_file = 'logs/challenge_llama_layered.log'  # Replace with your actual log file name
# # log_file = 'logs/test.log'  # Replace with your actual log file name
# output_file = 'logs/challenge_llama_layered.csv'  # Replace with your desired output CSV file name

# Define the folder path
folder_path = 'logs/'

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    
    # Check if it's a file (not a directory)
    if os.path.isfile(filepath) and filename.endswith('.log'):
        convert_log(filepath, filepath+'.csv')
# convert_log(log_file, output_file)