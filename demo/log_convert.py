import csv
import re
import os

def convert_log(log_file, output_file):
    # Regular expressions to match patterns in the log
    user_time_pattern = re.compile(r'User time \(seconds\): (\d+\.\d+)')
    system_time_pattern = re.compile(r'System time \(seconds\): (\d+\.\d+)')
    max_resident_set_pattern = re.compile(r'Maximum resident set size \(kbytes\): (\d+)')
    step_pattern = re.compile(r'--- STEP (\d+)')


    # Read and process the log
    with open(log_file, 'r') as f, open(output_file, 'w', newline='') as csvfile:
        
        csv_writer = csv.writer(csvfile)
        # Write the header row
        csv_writer.writerow([
            'STEP number', 'layer num', 'searching step',
            'Challenger 0 User time (seconds)', 'Challenger 0 System time (seconds)', 'Challenger 0 Maximum resident set size (kb)',
            'Challenger 1 User time (seconds)', 'Challenger 1 System time (seconds)', 'Challenger 1 Maximum resident set size (kb)'
        ])

        current_step = None
        layer_num = None
        searching_step = None
        challenger0 = {'user_time': None, 'system_time': None, 'max_resident_set': None}
        challenger1 = {'user_time': None, 'system_time': None, 'max_resident_set': None}

        for line in f:
            line=line.strip()
            step_match = step_pattern.match(line)
            if step_match:
                if current_step is not None:# and len(challenge_data) == 2:
                    # Write the row for the previous step
                    csv_writer.writerow([
                        current_step, layer_num, searching_step,
                        challenger0['user_time'], challenger0['system_time'], challenger0['max_resident_set'],
                        challenger1['user_time'], challenger1['system_time'], challenger1['max_resident_set']
                    ])
                # Reset for the next step
                current_step = step_match.group(1)
                challenger0 = {'user_time': None, 'system_time': None, 'max_resident_set': None}
                challenger1 = {'user_time': None, 'system_time': None, 'max_resident_set': None}
                continue
            
            if 'current layer:' in line:
                layer_num = line.split(':')[-1].strip()
            if 'searching step:' in line:
                searching_step = line.split(':')[-1].strip()
            
            # Identify Challenger 0 and Challenger 1
            # line = 'isChallenger: true'
            # line = 'isChallenger:  true'
            if 'isChallenger:  true' in line:
                challenger = challenger1
            elif 'isChallenger:  false' in line:
                challenger = challenger0

            # Match the performance data
            user_time_match = user_time_pattern.match(line)
            system_time_match = system_time_pattern.match(line)
            max_resident_set_match = max_resident_set_pattern.match(line)

            if user_time_match:
                challenger['user_time'] = user_time_match.group(1)
            elif system_time_match:
                challenger['system_time'] = system_time_match.group(1)
            elif max_resident_set_match:
                challenger['max_resident_set'] = max_resident_set_match.group(1)

        # Write the last step
        if current_step is not None:
            csv_writer.writerow([
                current_step, layer_num, searching_step,
                challenger0['user_time'], challenger0['system_time'], challenger0['max_resident_set'],
                challenger1['user_time'], challenger1['system_time'], challenger1['max_resident_set']
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