import matplotlib.pyplot as plt
import csv
import os


def safe_float(a):
    return float(a) if a != '' else 0
def safe_int(a):
    return int(a) if a != '' else 0

def plot_csv(csv_file, output_file):
    # Data arrays for Challenger 0 and Challenger 1
    step_numbers = []
    user_time_0 = []
    user_time_1 = []
    max_res_size_0 = []
    max_res_size_1 = []

    # Read data from the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
              step_numbers.append(safe_int(row['STEP number']))
              user_time_0.append(safe_float(row['Challenger 0 User time (seconds)']))
              user_time_1.append(safe_float(row['Challenger 1 User time (seconds)']))
              max_res_size_0.append(safe_int(row['Challenger 0 Maximum resident set size (kb)']))
              max_res_size_1.append(safe_int(row['Challenger 1 Maximum resident set size (kb)']))
            except Exception as e:
              print(row)
              raise e

    # Plot User Time
    plt.figure(figsize=(10, 6))

    print('step_numbers', step_numbers)
    print('user_time_0', user_time_0)
    print('user_time_1', user_time_1)

    plt.subplot(2, 1, 1)  # Create a subplot for User time
    plt.plot(step_numbers, user_time_0, label='Challenger 0 User time', color='blue', marker='o')
    plt.plot(step_numbers, user_time_1, label='Challenger 1 User time', color='orange', marker='o')
    plt.title('User time (seconds) for Challenger 0 and 1')
    plt.xlabel('STEP number')
    plt.ylabel('User time (seconds)')
    plt.legend()

    # Plot Maximum Resident Set Size
    plt.subplot(2, 1, 2)  # Create a subplot for Maximum resident set size
    plt.plot(step_numbers, max_res_size_0, label='Challenger 0 Max resident set size', color='green', marker='o')
    plt.plot(step_numbers, max_res_size_1, label='Challenger 1 Max resident set size', color='red', marker='o')
    plt.title('Maximum resident set size (kb) for Challenger 0 and 1')
    plt.xlabel('STEP number')
    plt.ylabel('Maximum resident set size (kb)')
    plt.legend()

    # Show the plot
    plt.tight_layout()
    # plt.show()
    plt.savefig(output_file)  # Save as PNG file
    plt.close()
    
    print(f"Plot {csv_file} and saved to {output_file}")

# Define the folder path
folder_path = 'logs/'

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    
    # Check if it's a file (not a directory)
    if os.path.isfile(filepath) and filename.endswith('.csv'):
        plot_csv(filepath, filepath+'.png')

# filepath = 'logs/challenge_llama_layered.log.csv'
# plot_csv(filepath, filepath+'.png')