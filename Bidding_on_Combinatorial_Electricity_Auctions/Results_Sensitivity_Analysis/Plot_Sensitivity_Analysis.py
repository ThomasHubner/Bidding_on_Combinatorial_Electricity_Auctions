"""
Reads results from csv and creates plots regarding bid and scenario number.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.ticker as mtick

colour = [y/255 for y in (16,78,139)]

#---------------------------------------
# Read data from csv for each case study
#--------------------------------------

case_studies = ["thermal generator", "battery", "demand response"]
bid_sizes = [10, 20, 30, 40, 50, 60, 70, 80] 
scenario_numbers = [120, 160, 200, 240, 280, 320, 360, 400]

# Iterate over method
for case_study in case_studies:
    
    # Read the CSV file into a DataFrame
    df_size = pd.read_csv('results_bidsize_'+case_study+'_exclusive.csv')
    
    # Read the CSV file into a DataFrame
    df_scenarios = pd.read_csv('results_scenarios_'+case_study+'_exclusive.csv')
    
    # Initialize lists of shares gained for different bids sizes
    share_gained_size = []
    share_gained_scenarios = []
    
    #---------------------------------
    # Loop through bid size lists
    #---------------------------------
    for i,size in enumerate(bid_sizes):
        
        max_utilities = df_size.iloc[:, 0].values.tolist()
        bid_utilities = df_size.iloc[:, i+1].values.tolist()
        
        # Calculate the sum of maximal utility and utility gained for all days
        # Calculate the division of sums for all days
        share = sum(bid_utilities) / sum(max_utilities) 
    
        # Append results to respective lists
        share_gained_size.append(share * 100)

    #---------------------------------
    # Loop through scenario  number lists
    #---------------------------------
    for i,number in enumerate(scenario_numbers):
        
        max_utilities = df_scenarios.iloc[:, 0].values.tolist()
        bid_utilities = df_scenarios.iloc[:, i+1].values.tolist()
        
        # Calculate the sum of maximal utility and utility gained for all days
        # Calculate the division of sums for all days
        share = sum(bid_utilities) / sum(max_utilities) 
    
        # Append results to respective lists
        share_gained_scenarios.append(share * 100)


    #------------------------------------------------------
    # Plot Case Study
    #------------------------------------------------------
    
    # Creating figure and axes objects
    fig, ax1 = plt.subplots(figsize=(10, 7))
    
    # Creating the first plot with its own x-axis
    ax1.plot(bid_sizes, share_gained_size, label = "Number of bids", marker='o', linestyle='-', linewidth=2, color=colour)
    ax1.set_xlabel('Number of bids', color='black', fontsize=18)
    ax1.set_ylabel('Realised share of max. utility (%)', color='black', fontsize=18)
    
    # Creating a second set of axes that shares the same y-axis with the first plot
    ax2 = ax1.twiny()
    ax2.plot(scenario_numbers, share_gained_scenarios, label = "Number of scenarios", marker='o', linestyle='--', linewidth=2, color=[y/255 for y in (120,10,10)])
    ax2.set_xlabel('Number of scenarios', color='black', fontsize=18)
    
    # Combining legends from both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    lines = lines_1 + lines_2
    labels = labels_1 + labels_2
    ax1.legend(lines, labels, fontsize=18,loc='lower right', bbox_to_anchor=(1, 0.2)) 
    
    
    # Increasing the size of the y-axis tick labels
    ax1.tick_params(axis='y', labelsize=16)
    ax1.tick_params(axis='x', labelsize=16) 
    ax2.tick_params(axis='x', labelsize=16) 
    ax1.set_xticks(bid_sizes)
    ax2.set_xticks(scenario_numbers)
    
    # Show the plot
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('double_'+case_study+'.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('double_'+case_study+'.svg', format='svg', bbox_inches='tight')
    plt.show()

