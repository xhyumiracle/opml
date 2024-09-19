import matplotlib.pyplot as plt
import pandas as pd
import os


def safe_float(a):
    return float(a) if a != '' else 0
def safe_int(a):
    return int(a) if a != '' else 0

def plot_csv(csv_file, output_file):
    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)

    round_numbers = df['STEP number']


    # Plot Time
    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)  # Create a subplot for User time
    plt.plot(round_numbers, df['Challenger 0 NonSysIO time (sec)'], label='Defender Proving Time', color='blue', marker='o')
    plt.plot(round_numbers, df['Challenger 1 NonSysIO time (sec)'], label='Challenger Proving Time', color='orange', marker='o')
    plt.title('Proving Time for Defender and Challenger')
    plt.xlabel('Challenge Round Number')
    plt.ylabel('Proving Time (seconds)')
    plt.legend()

    # Plot Maximum Resident Set Size
    plt.subplot(2, 1, 2)  # Create a subplot for Maximum resident set size
    plt.plot(round_numbers, df['Challenger 0 Peak Mem (kb)'] / 1024, label='Defender Peak Memory Usage', color='green', marker='o')
    plt.plot(round_numbers, df['Challenger 1 Peak Mem (kb)'] / 1024, label='Challenger Peak Memory Usage', color='red', marker='o')
    plt.title('Peak Memory Usage for Defender and Challenger')
    plt.xlabel('Challenge Round Number')
    plt.ylabel('Peak Memory Usage (Mb)')
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