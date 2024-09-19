import matplotlib.pyplot as plt
import pandas as pd
import os

def safe_float(a):
    return float(a) if a != '' else 0
def safe_int(a):
    return int(a) if a != '' else 0

def plot_1(csv_file, output_file, node_ids=None):

    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)

    p1_time = df[df['Node ID'].isin(node_ids)]['Phase 1 NonSysIO time (sec)'].values if node_ids else df['Phase 1 NonSysIO time (sec)']
    p2_time = df[df['Node ID'].isin(node_ids)]['Phase 2 NonSysIO time (sec)'].values if node_ids else df['Phase 2 NonSysIO time (sec)']

    indices = range(1, len(node_ids) + 1) if node_ids else df['Node ID']

    # Plot 1: NodeID vs. Mips Steps
    plt.figure(figsize=(8, 5))
    # plt.plot(df['Node ID'], df['Mips Steps'], marker='o', color='blue', label='Mips Steps')
    plt.plot(indices, p1_time, marker='o', color='blue', label='Phase 1 Time')
    plt.plot(indices, p2_time, marker='o', color='pink', label='Phase 2 Time')
    # plt.plot(df['Node ID'], df['Phase 1 Peak Mem (kb)'], marker='o', color='green', label='Phase 1 Peak Mem Usage')
    # plt.plot(df['Node ID'], df['Phase 2 Peak Mem (kb)'], marker='o', color='orange', label='Phase 2 Peak Mem Usage')
    plt.xticks(indices, node_ids)  # Custom x-ticks with the selected Node IDs
    plt.xlabel('Tensor ID')
    # plt.ylabel('Mips Steps')
    plt.ylabel('Execution Time (sec)')
    plt.title('Time Cost per NodeID')
    plt.grid(True)
    plt.legend()
    plt.show()
    plt.savefig(output_file)  # Save as PNG file

    print(f"Plot {csv_file} and saved to {output_file}")

def plot_2(csv_file, output_file, node_ids):

    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Plot 2: Custom NodeID Series vs Mips Steps
    mips_steps = df[df['Node ID'].isin(node_ids)]['Mips Steps'].values
    # p1_time = df[df['Node ID'].isin(node_ids)]['Phase 1 NonIO time (sec)'].values
    # p2_time = df[df['Node ID'].isin(node_ids)]['Phase 2 NonIO time (sec)'].values

    # Index of custom Node IDs
    indices = range(1, len(node_ids) + 1)

    plt.figure(figsize=(8, 5))
    plt.plot(indices, mips_steps, marker='o', color='black', label='Mips Steps for Selected Nodes')
    # plt.plot(indices, p1_time, marker='o', color='blue', label='Phase 1 time for Selected Nodes')
    # plt.plot(indices, p2_time, marker='o', color='red', label='Phase 2 time for Selected Nodes')
    plt.xticks(indices, node_ids)  # Custom x-ticks with the selected Node IDs
    plt.xlabel('Tensor ID')
    plt.ylabel('Mips Execution Steps')
    # plt.ylabel('Phase 1&2 NonIO time (sec)')
    
    plt.title(f'Mips Execution Steps per TensorID: {node_ids}')
    plt.grid(True)
    plt.legend()

    # plt.tight_layout()
    plt.savefig(output_file)  # Save as PNG file
    plt.close()
    
    print(f"Plot {csv_file} and saved to {output_file}")

def plot_2(csv_file, output_file, node_ids):

    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Plot 2: Custom NodeID Series vs Mips Steps
    # mips_steps = df[df['Node ID'].isin(node_ids)]['Mips Steps'].values
    p1_mem = df[df['Node ID'].isin(node_ids)]['Phase 1 Peak Mem (kb)'].values
    p2_mem = df[df['Node ID'].isin(node_ids)]['Phase 2 Peak Mem (kb)'].values

    # Index of custom Node IDs
    indices = range(1, len(node_ids) + 1)

    plt.figure(figsize=(8, 5))
    # plt.plot(indices, mips_steps, marker='o', color='black', label='Mips Steps for Selected Nodes')
    plt.plot(indices, p1_mem, marker='o', color='blue', label='Phase 1 Peak Memory Usage')
    plt.plot(indices, p2_mem, marker='o', color='red', label='Phase 2 Peak Memory Usage')
    plt.xticks(indices, node_ids)  # Custom x-ticks with the selected Node IDs
    plt.xlabel('Tensor ID')
    plt.ylabel('Peak Memory Usage (Mb)')
    # plt.ylabel('Phase 1&2 NonIO time (sec)')
    
    plt.title(f'Peak Memory Usage per TensorID: {node_ids}')
    plt.grid(True)
    plt.legend()

    # plt.tight_layout()
    plt.savefig(output_file)  # Save as PNG file
    plt.close()
    
    print(f"Plot {csv_file} and saved to {output_file}")

# Define the folder path
folder_path = 'logs/stats'

node_ids = {
#   "MNIST": [3, 4, 5],
#   "LLAMA": [627, 940, 1097, 1175, 1214, 1234, 1244, 1249, 1251,1252,1253]
  
  "MNIST": [0,1,3,4,5],
  "LLAMA": [508, 600, 700]
#   "LLAMA": [1,2,3]
}

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    
    # Check if it's a file (not a directory)
    if os.path.isfile(filepath) and filename.endswith('.csv'):
        model_name = filename.split('-')[0]
        # print ('model_name', model_name, node_ids[model_name])
        plot_1(filepath, filepath + '.time_round.png', node_ids[model_name])
        plot_2(filepath, filepath + '.mem_round.png', node_ids[model_name])

# filepath = 'logs/challenge_llama_layered.log.csv'
# plot_csv(filepath, filepath+'.png')