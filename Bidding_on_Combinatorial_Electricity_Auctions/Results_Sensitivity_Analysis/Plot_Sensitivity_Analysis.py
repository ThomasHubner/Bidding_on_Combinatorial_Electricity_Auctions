"""
Reads results from csv and creates plots regarding bid and scenario number.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.ticker as mtick
from brokenaxes import brokenaxes
import math

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
    
    # Read the CSV file into a DataFrame
    df_self_schedule = pd.read_csv('results_self-schedule_'+case_study+'.csv')
    
    # Initialize lists of shares gained for different bids sizes and scenarios
    share_gained_size = []
    share_gained_scenarios = []
    share_gained_self_schedule = []
    time_exclusive_group = []
    time_self_schedule = []
    
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
        run_times = df_scenarios.iloc[:, i+1+len(scenario_numbers)].values.tolist()
        
        # Calculate the sum of maximal utility and utility gained for all days
        # Calculate the division of sums for all days
        share = sum(bid_utilities) / sum(max_utilities) 
        
        # Append results to respective lists
        share_gained_scenarios.append(share * 100)
    
        # Calculate average runtime
        avg_time = sum(run_times) / len(run_times)

        # Append results to respective lists
        time_exclusive_group.append(avg_time)
        
    #-----------------------------------------------------
    # Loop through scenario  number lists for self schedule
    #------------------------------------------------------
    for i,number in enumerate(scenario_numbers):
        
        max_utilities = df_self_schedule.iloc[:, 0].values.tolist()
        bid_utilities = df_self_schedule.iloc[:, i+1].values.tolist()
        run_times = df_self_schedule.iloc[:, i+1+len(scenario_numbers)].values.tolist()
        
        # Calculate the sum of maximal utility and utility gained for all days
        # Calculate the division of sums for all days
        share = sum(bid_utilities) / sum(max_utilities) 
    
        # Append results to respective lists
        share_gained_self_schedule.append(share * 100)
        
        # Calculate average runtime
        avg_time = sum(run_times) / len(run_times)
        
        # Append results to respective lists
        time_self_schedule.append(avg_time)


    #------------------------------------------------------
    # Plot Case Study - share gained
    #------------------------------------------------------
    
    # Get Limits
    y0 = min(share_gained_self_schedule)
    y1 = max(share_gained_self_schedule)
    y2 = min(share_gained_scenarios + share_gained_size)
    y3 = max(share_gained_scenarios + share_gained_size)
    
    if case_study == "battery":
        y0 = int(y0)
        y1 = math.ceil(y1)
        y2 = int(y2)
        y3 = math.ceil(y3)
        
    else:
        y0 = int(y0*10)/10
        y1 = math.ceil(10*y1)/10
        y2 = int(y2*10)/10
        y3 = math.ceil(10*y3)/10
        
    
    # Create broke y-axis to remove white area between self-schedule and exclusive group
    bax = brokenaxes(ylims=((y0, y1), (y2, y3)), hspace=0.5)
    
    # Plotting the data
    bax.plot(bid_sizes, share_gained_size, label = "Sensitivity: Bids", marker='o', linestyle='-', linewidth=2, color=colour)
    bax.plot(bid_sizes, share_gained_scenarios, label = "Sensitivity: Scenarios", marker='o', linestyle='--', linewidth=2, color=[y/255 for y in (120,10,10)])
    bax.plot(bid_sizes, share_gained_self_schedule, label = "Self-Schedule", marker='o', linestyle=':', linewidth=2, color="teal")
    
    # Creating labels
    bax.set_xlabel('Number of bids',labelpad=25)
    if case_study == "battery":
        bax.set_ylabel('Realised share of max. utility (%)',labelpad=25)
    else:
        bax.set_ylabel('Realised share of max. utility (%)',labelpad=35)

    # Creating the second x-axis at the top
    functions = (lambda x: 4*(x+20), lambda x: x/4 -20)
    secax = bax.secondary_xaxis(functions, label="Number of scenarios")
    
    # Combining legends from both axes
    if case_study == "battery":
        bax.legend(loc='lower right',bbox_to_anchor=(1, 0.3))
    else:
        bax.legend(loc='lower right',bbox_to_anchor=(1, 0.35))
    
    # Show the plot
    #plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('double_'+case_study+'.pdf', format='pdf', bbox_inches='tight')
    #plt.savefig('double_'+case_study+'.svg', format='svg', bbox_inches='tight')
    plt.show()



    #------------------------------------------------------
    # Plot Case Study - computation time
    #------------------------------------------------------

    # Plot lines
    plt.figure()
    
    # Plot lines
    plt.plot(scenario_numbers, time_exclusive_group, label= "Exclusive Group" , marker='o', linestyle='-', linewidth=2, color=colour)
    plt.plot(scenario_numbers, time_self_schedule, label= "Self-Schedule" , marker='o', linestyle='--', linewidth=2, color=[y/255 for y in (120,10,10)])
    
    # Increase font size for x and y-axis labels
    plt.xlabel('Number of scenarios')#, fontname='Arial', fontsize=18)
    plt.ylabel('Avg. total runtime (s)')#, fontname='Arial', fontsize=18)
    
    # Add legend
    plt.legend()#fontsize=18) #,loc='lower right', bbox_to_anchor=(1, 0.2))
    
    # Customize y-axis tick positions and labels
    #plt.yticks()#fontsize=16)
    
    # Customize x-axis tick positions and labels
    #plt.xticks(number_scenarios)#, fontsize=16)
    
    # Hide the top and right spines to remove the surrounding box
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Show the plot
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('time_'+case_study+'.pdf', format='pdf', bbox_inches='tight')
    #plt.savefig('time_scenarios.svg', format='svg', bbox_inches='tight')
    plt.show()



