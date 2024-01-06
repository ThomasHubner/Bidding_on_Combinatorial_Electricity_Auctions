"""
Reads results from csv and creates plots showing the sensitivity regarding the probabilistic forecast.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.ticker as mtick


#---------------------------------------
# Read data from csv for each case study
#--------------------------------------

case_studies = ["thermal generator", "battery", "demand response"]

# Forecast improvment steps
scalars = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

# Initalize list containing results for all case studies
share_gained_all_case_studies = []
wasserstein_all_case_studies = []

# Iterate over method
for case_study in case_studies:
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv('results_wasserstein_'+case_study+'_exclusive.csv')
    
    # Initialize lists of shares gained and wasserstein distances for different forecast qualitites
    share_gained = []
    wasserstein_distances = []
    
    #---------------------------------
    # Loop through forecast levels
    #---------------------------------
    for i,size in enumerate(scalars):
        
        max_utilities = df.iloc[:, 0].values.tolist()
        bid_utilities = df.iloc[:, i+1].values.tolist()
        wasserstein = df.iloc[:, i+1+len(scalars)].values.tolist()
        
        # Calculate the sum of maximal utility and utility gained for all days
        # Calculate the division of sums for all days
        share = sum(bid_utilities) / sum(max_utilities) 
        
        # Calculate average wasserstein distance
        wasserstein_avg = sum(wasserstein) / len(wasserstein)
    
        # Append results to respective lists
        share_gained.append(share * 100)
        wasserstein_distances.append(wasserstein_avg)

    share_gained_all_case_studies.append(share_gained)
    wasserstein_all_case_studies.append(wasserstein_distances)
    
#################################################################################################################################

#------------------------------------------------------
# Plot Realised utility - generator and demand response
#------------------------------------------------------

# Data
x_values = wasserstein_all_case_studies[0] # wasserstein distacnes of the forecast are the same for all case studies
y1 = share_gained_all_case_studies[0] # thermal generator
y2 = share_gained_all_case_studies[1] # battery
y3 = share_gained_all_case_studies[2] # demand response

# Plot lines
plt.figure(figsize=(10, 7))

# Plot lines
plt.plot(x_values, y1, label= "Thermal generator" , marker='o', linestyle='-', linewidth=2, color="royalblue")
plt.plot(x_values, y2, label= "Battery storage", marker='o', linestyle='-', linewidth=2, color="teal")
plt.plot(x_values, y3, label= "Heating utility", marker='o', linestyle='-', linewidth=2, color="firebrick")

# Increase font size for x and y-axis labels
plt.xlabel('Wasserstein distance', fontname='Arial', fontsize=18)
plt.ylabel('Realised share of max. utility (%)', fontname='Arial', fontsize=18)

# Add legend
plt.legend(fontsize=18,loc='lower right', bbox_to_anchor=(1, 0.2))

# Customize y-axis tick positions and labels
plt.yticks(fontsize=16)

# Customize x-axis tick positions and labels
#x_strings = [str(round(x))+" (" + str(z) +")" for x,z in zip(x_values,scalars)]
x_strings = [str(round(x))for x in x_values]
plt.xticks(x_values, x_strings, fontsize=16)

# Invert the x-axis
plt.gca().invert_xaxis()

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('profit_wasserstein.pdf', format='pdf', bbox_inches='tight')
plt.savefig('profit_wasserstein.svg', format='svg', bbox_inches='tight')
plt.show()


#------------------------------------------------------
# Plot Realised utility - battery
#------------------------------------------------------

# Data
x_values = wasserstein_all_case_studies[0] # wasserstein distacnes of the forecast are the same for all case studies
y1 = share_gained_all_case_studies[0] # thermal generator
y2 = share_gained_all_case_studies[1] # battery
y3 = share_gained_all_case_studies[2] # demand response

# Plot lines
plt.figure(figsize=(10, 7))

# Plot lines
plt.plot(x_values, y2, label= "Battery storage", marker='o', linestyle='-', linewidth=2, color="teal")

# Increase font size for x and y-axis labels
plt.xlabel('Wasserstein distance', fontname='Arial', fontsize=18)
plt.ylabel('Realised share of max. utility (%)', fontname='Arial', fontsize=18)

# Add legend
plt.legend(fontsize=18,loc='lower right', bbox_to_anchor=(1, 0.2))

# Customize y-axis tick positions and labels
plt.yticks(fontsize=16)

# Customize x-axis tick positions and labels
#x_strings = [str(round(x))+" (" + str(z) +")" for x,z in zip(x_values,scalars)]
x_strings = [str(round(x))for x in x_values]
plt.xticks(x_values, x_strings, fontsize=16)

# Invert the x-axis
plt.gca().invert_xaxis()

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('profit_wasserstein_battery.pdf', format='pdf', bbox_inches='tight')
plt.savefig('profit_wasserstein_battery.svg', format='svg', bbox_inches='tight')
plt.show()


