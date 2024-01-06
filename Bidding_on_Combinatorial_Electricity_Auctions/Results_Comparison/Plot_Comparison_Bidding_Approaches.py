"""
Plots the histogram for comparison of the bidding approaches.
"""

import matplotlib.pyplot as plt

colour = [y/255 for y in (16,78,139)]

# Data for the histogram
# Manually read in from the csv files
data_battery = [96.6, 87.3, 77.6, 93.8]
data_generator = [99.9, 99.6, 89.9, 96.1]
data_utility = [99.4, 98.5, 98.8, 98.2]

adjustment = {"battery": 0.95, "generator": 0.975, "utility": 0.99}
    
for case_study in ["battery", "generator", "utility"]:

    data = globals()["data_" + case_study]
    
    # Labels for the bars
    labels = ['Exclusive \n Group: LP', 'Exclusive \n Group: MILP', 'Ungrouped \n Bids', 'Self \n Schedule']
    
    # Colors for each bar
    colors = [colour, 'royalblue', 'firebrick', 'teal']
    
    # Adjusting y-axis
    min_value = min(data)
    plt.ylim(min_value * adjustment[case_study], 100)
    
    # Creating the histogram with specified colors
    plt.bar(labels, data, color=colors)
    
    # Adding title and labels
    plt.ylabel('Realised share of max. utility (%)')
    
    # Hide the top and right spines to remove the surrounding box
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Show the plot
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('histogram_'+case_study+'.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('histogram_'+case_study+'.svg', format='svg', bbox_inches='tight')
    plt.show()