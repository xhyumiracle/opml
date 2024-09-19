import matplotlib.pyplot as plt
import pandas as pd
import os

# Function to generate and save the stacked area plot with filled colors
def plot_stacked_lines(csv_file, output_file, phase_num):
    # Load CSV data into a pandas DataFrame
    data = pd.read_csv(csv_file)

    # Extract the relevant columns
    node_ids = data['Node ID']
    vm_io = data['Phase '+str(phase_num)+' vmIOTime']
    vm_exec = data['Phase '+str(phase_num)+' vmExecTime']
    total = data['Phase '+str(phase_num)+' NonSysIO time (sec)']

    # Calculate 'others' as the difference between 'total' and the sum of 'vm-io' and 'vm-exec'
    others = total - vm_io - vm_exec

    # Cumulative sum for stacking lines
    stack_order = [vm_exec, others, vm_io]
    lable_order = ['vm-exec', 'others', 'vm-io']
    color_order = ['green', 'skyblue', 'orange']

    _stacked = [
        stack_order[0], 
        stack_order[0] + stack_order[1], 
        stack_order[0] + stack_order[1] + stack_order[2]
        ]

    # Create the plot
    plt.figure(figsize=(10, 6))

    # Fill the regions between the lines
    plt.fill_between(node_ids, 0, _stacked[0], label=lable_order[0], color=color_order[0], alpha=0.5)
    plt.fill_between(node_ids, _stacked[0], _stacked[1], label=lable_order[1], color=color_order[1], alpha=0.5)
    plt.fill_between(node_ids, _stacked[1], _stacked[2], label=lable_order[2], color=color_order[2], alpha=0.5)

    # Plot the lines on top of the filled regions
    plt.plot(node_ids, _stacked[0], color=color_order[0], marker='o')
    plt.plot(node_ids, _stacked[1], color=color_order[1], marker='o')
    plt.plot(node_ids, _stacked[2], color=color_order[2], marker='o')

    # Add labels, title, and legend
    plt.xlabel('Tensor ID')
    plt.ylabel('Time Cost')
    plt.title('Phase ' + str(phase_num) + ' Time Cost Analysis per Tensor ID')
    plt.legend()

    # Save the plot to the output file
    plt.savefig(output_file)

# Example usage
if __name__ == "__main__":
    folder_path = 'logs/stats'
    # csv_file = 'logs/stats/LLAMA-2024-09-19T00:29+08:00.csv'  # Replace with your CSV filename
    # output_file = 'logs/stats/LLAMA-2024-09-19T00:29+08:00.csv.stacked_area_plot.png'  # Output file
    # plot_stacked_lines(csv_file, output_file)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(filepath) and filename.endswith('.csv'):
            model_name = filename.split('-')[0]
            # print ('model_name', model_name, node_ids[model_name])
            # plot_1(filepath, filepath + '.allnodes.png', node_ids[model_name])
            plot_stacked_lines(filepath, filepath + '.stacked_time_p1.png', 1)
            plot_stacked_lines(filepath, filepath + '.stacked_time_p2.png', 2)
