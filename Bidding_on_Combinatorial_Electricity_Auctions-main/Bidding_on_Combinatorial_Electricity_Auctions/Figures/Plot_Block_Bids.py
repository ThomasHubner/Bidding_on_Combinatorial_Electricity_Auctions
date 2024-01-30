"""
Plot file for several block bids:
    - plot 1: exposure problem
    - plot 2: a regular block bid
    - plot 3: a profile block bid
    - Plot 4: two ungrouped block bids
    - Plot 5: exclusive group
"""


import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches
import numpy as np
#import tikzplotlib

colour = [y/255 for y in (16,78,139)]

#---------------------------------
# Plot 1: exposure problem
#--------------------------------

# Data for the Lego-like block structure
block1 = (0.6, 1.4)  
block2 = (1.6, 2.4) 
block3 = (2.6, 3.4)  
block4 = (3.6, 4.4) 
block_height = 0.7  

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 4))

# Draw the Lego-like block without black lines
block1_width = block1[1] - block1[0]
rect1 = patches.Rectangle((block1[0], 0), block1_width, block_height, edgecolor='none', facecolor="steelblue")
ax.add_patch(rect1)

block2_width = block2[1] - block2[0]
rect2 = patches.Rectangle((block2[0], 0), block2_width, block_height, edgecolor='none', facecolor="steelblue")
ax.add_patch(rect2)

block3_width = block3[1] - block3[0]
rect3 = patches.Rectangle((block3[0], 0), block3_width, block_height, edgecolor='none', facecolor="steelblue")
ax.add_patch(rect3)

block4_width = block4[1] - block4[0]
rect4 = patches.Rectangle((block4[0], 0), block4_width, block_height, edgecolor='none', facecolor="steelblue")
ax.add_patch(rect4)

# Add lines
x = np.linspace(1.5, 2.5, 100)  # Create an array of 100 points
m = 0.2  # Slope of the line
c = 0 # Intercept of the line
y = m * x + c  # Equation of the line (y = mx + c)
ax.plot(x, y, color='firebrick', linewidth = 5)

x = np.linspace(1.5, 2.5, 100)  # Create an array of 100 points
m = -0.2  # Slope of the line
c = 0.8 # Intercept of the line
y = m * x + c  # Equation of the line (y = mx + c)
ax.plot(x, y, color='firebrick', linewidth = 5)

# Set axis labels and limits
ax.set_xlabel('Hours', fontsize=25) #default: 18
ax.set_ylabel('Power', fontsize=25)
ax.set_xlim(0, 5)  # Adjust the x-axis limits 
ax.set_ylim(0, 1)  # Add some padding for visibility

# Customize the x-axis ticks to show only the hour number
ax.set_xticks(range(1, 6))  # Adjust the tick range
ax.set_xticklabels([f'{hour}' for hour in range(1, 5)] + ["24"], fontsize=17)  # default 14
plt.text(4.5, -0.055, '...', ha='center', va='center', fontsize=22)

# Remove y-axis labels and ticks
ax.set_yticks([])

# Title and grid
plt.grid(True)

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.0)
plt.savefig('exposure_problem'+'.svg', format='svg', bbox_inches='tight')
plt.savefig('exposure_problem'+'.pdf', format='pdf', bbox_inches='tight')
#tikzplotlib.save("ungrouped_bids.tex")
plt.show()


#---------------------------------
# Plot 2: regular block bid
#--------------------------------

# Data for the Lego-like block structure
block1 = (0.6, 4.4)  # Regular block bid
block_height = 0.7  # Volume

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 4))

# Draw the first Lego-like block without black lines
block1_width = block1[1] - block1[0]
rect1 = patches.Rectangle((block1[0], 0), block1_width, block_height, edgecolor='none', facecolor=colour)
ax.add_patch(rect1)

# Set axis labels and limits
ax.set_xlabel('Hours', fontsize=25) #default: 18
ax.set_ylabel('Power', fontsize=25)
ax.set_xlim(0, 5)  # Adjust the x-axis limits 
ax.set_ylim(0, 1)  # Add some padding for visibility

# Customize the x-axis ticks to show only the hour number
ax.set_xticks(range(1, 6))  # Adjust the tick range
ax.set_xticklabels([f'{hour}' for hour in range(1, 5)] + ["24"], fontsize=17)  # default 14
plt.text(4.5, -0.055, '...', ha='center', va='center', fontsize=22)

# Remove y-axis labels and ticks
ax.set_yticks([])

# Title and grid
plt.grid(True)

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.0)
plt.savefig('regular_block_bid'+'.svg', format='svg', bbox_inches='tight')
plt.savefig('regular_block_bid'+'.pdf', format='pdf', bbox_inches='tight')
#tikzplotlib.save("ungrouped_bids.tex")
plt.show()


#---------------------------------
# Plot 3: profile block bid
#--------------------------------

# Data for the Lego-like block structure
blocks = [(0.6,1.5), (1.5,2.5), (2.5,3.5), (3.5,4.4)]  
height = [0.4, 0.6, 0.8, 0.5]  # Volume

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 4))

# Draw the Lego-like blocks
i = 0
for start, end in blocks:
    block_width = end - start
    rect = patches.Rectangle((start, 0), block_width, height[i], linewidth=2, edgecolor='teal', facecolor="teal")
    ax.add_patch(rect)
    i=i+1

# Set axis labels and limits
ax.set_xlabel('Hours', fontsize=25) #default: 18
ax.set_ylabel('Power', fontsize=25)
ax.set_xlim(0, 5)  # Adjust the x-axis limits 
ax.set_ylim(0, 1)  # Add some padding for visibility

# Customize the x-axis ticks to show only the hour number
ax.set_xticks(range(1, 6))  # Adjust the tick range
ax.set_xticklabels([f'{hour}' for hour in range(1, 5)] + ["24"], fontsize=17)  # default 14
plt.text(4.5, -0.055, '...', ha='center', va='center', fontsize=22)

# Remove y-axis labels and ticks
ax.set_yticks([])

# Title and grid
plt.grid(True)

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.0)
plt.savefig('profile_block_bid'+'.svg', format='svg', bbox_inches='tight')
plt.savefig('profile_block_bid'+'.pdf', format='pdf', bbox_inches='tight')
#tikzplotlib.save("ungrouped_bids.tex")
plt.show()

#---------------------------------
# Plot 4: two ungrouped block bids
#--------------------------------

# Data for the Lego-like block structure
block1 = (7, 17)
block2 = (10, 20)  # Overlapping with block1
block_height = 1  # Volume

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 4))

# Draw the first Lego-like block without black lines
block1_width_1 = block2[0] - block1[0]
block1_width_2 = block1[1] - block2[0]
rect1 = patches.Rectangle((block1[0], 0), block1_width_1, block_height, edgecolor='none', facecolor=colour)
rect2 = patches.Rectangle((block2[0], 1), block1_width_2, block_height, edgecolor='none', facecolor=colour)
ax.add_patch(rect1)
ax.add_patch(rect2)

# Draw the second Lego-like block without black lines (stacked on top of the first)
block2_width = block2[1] - block2[0]
rect3 = patches.Rectangle((block2[0], 0), block2_width, block_height, edgecolor='none', facecolor="teal")
ax.add_patch(rect3)

# Set axis labels and limits
ax.set_xlabel('Hours', fontsize=18)
ax.set_ylabel('Power', fontsize=18)
ax.set_xlim(1, 24)  # Adjust the x-axis limits to start from 1
ax.set_ylim(0, block_height * 2.2)  # Add some padding for visibility

# Customize the x-axis ticks to show only the hour number
ax.set_xticks(range(1, 25))  # Adjust the tick range
ax.set_xticklabels([f'{hour}' for hour in range(1, 25)], fontsize=14)  # Display hours from 1 to 24

# Remove y-axis labels and ticks
ax.set_yticks([])

# Add a dotted horizontal line labeled "Self-dispatch" (not in the legend)
plt.plot([1,24], [1,1], linestyle='--', color='black', label='_nolegend_')
plt.text(2, 1.1, 'Maximum power output', ha='left', va='center', fontsize=14, color='black')

# Title and grid
#plt.title('Two accepted block bids', fontsize=20)
plt.grid(True)

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.0)
plt.savefig('ungrouped_bids'+'.svg', format='svg', bbox_inches='tight')
plt.savefig('ungrouped_bids'+'.pdf', format='pdf', bbox_inches='tight')
#tikzplotlib.save("ungrouped_bids.tex")
plt.show()

#########################################################################################################################################

# -------------------------------------------------------------------------------
# Plot 5: exclusive group
#-------------------------------------------------------------------------------------
fig = plt.figure(figsize=(10, 4))
gs = GridSpec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1, 2.5])

#--------------------------------------------
# First axes - arrow
# -----------------------------------------------
ax0 = fig.add_subplot(gs[0, :])

# Remove the plot border
ax0.spines['top'].set_visible(False)
ax0.spines['right'].set_visible(False)
ax0.spines['bottom'].set_visible(False)
ax0.spines['left'].set_visible(False)

# Remove axis labels and ticks
ax0.set_xticks([])
ax0.set_yticks([])

# Set axis limits
ax0.set_xlim(0, 2)
ax0.set_ylim(-1,6)

# Define the arrow properties
head_width = 15
head_length = 15

# Draw the arrow using patches (upside down)
arrow = patches.FancyArrowPatch(
    (0.5, 0),  # Starting point
    (1.5, 0),  # Ending point
    connectionstyle="arc3,rad=-0.3",  # Curvature of the arrow (negative rad)
    arrowstyle='<->, head_width={}, head_length={}'.format(head_width, head_length),
    lw=3,  # Line width
    edgecolor='black'
)

# Add the arrow to the plot
ax0.add_patch(arrow)


#--------------------------------------------------------------------
# Second axes - dispatch 1
# ------------------------------------------------------------------
ax1 = fig.add_subplot(gs[1, 0])

# Data for the Lego-like block structure
block1 = (7, 17)
block_height = 1  # Volume

# Draw the first Lego-like block without black lines
block1_width = block1[1] - block1[0]
rect1 = patches.Rectangle((block1[0], 0), block1_width, block_height, edgecolor='none', facecolor=colour)
ax1.add_patch(rect1)

# Set axis labels and limits
ax1.set_xlabel('Hours', fontsize=18)
ax1.set_ylabel('Power', fontsize=18)
ax1.set_xlim(6, 18)  # Adjust the x-axis limits to start from 1
ax1.set_ylim(0, block_height)  # Add some padding for visibility

# Customize the x-axis ticks to show only the hour number
ax1.set_xticks(range(6, 19))  # Adjust the tick range
ax1.set_xticklabels([f'{hour}' for hour in range(6, 19)], fontsize=14)  # Display hours from 1 to 24

# Remove y-axis labels and ticks
ax1.set_yticks([])

# Hide the top and right spines to remove the surrounding box
ax1 = plt.gca()
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)




#--------------------------------------------------------------------
# Third axes - dispatch 2
# ------------------------------------------------------------------
ax2 = fig.add_subplot(gs[1, 1])

# Data for the Lego-like block structure
block1 = (10, 20)
block_height = 1  # Volume

# Draw the first Lego-like block without black lines
block1_width = block1[1] - block1[0]
rect1 = patches.Rectangle((block1[0], 0), block1_width, block_height, edgecolor='none', facecolor="teal")
ax2.add_patch(rect1)

# Set axis labels and limits
ax2.set_xlabel('Hours', fontsize=18)
ax2.set_ylabel('Power', fontsize=18)
ax2.set_xlim(9, 21)  # Adjust the x-axis limits to start from 1
ax2.set_ylim(0, block_height)  # Add some padding for visibility

# Customize the x-axis ticks to show only the hour number
ax2.set_xticks(range(9, 22))  # Adjust the tick range
ax2.set_xticklabels([f'{hour}' for hour in range(9, 22)], fontsize=14)  # Display hours from 1 to 24

# Remove y-axis labels and ticks
ax2.set_yticks([])

# Hide the top and right spines to remove the surrounding box
ax2 = plt.gca()
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

#--------------------------------------------------------------------
# Show the plot
#--------------------------------------------------------------------

#plt.tight_layout()  # Remove any extra white space
plt.savefig('exclusive_bids'+'.svg', format='svg', bbox_inches='tight')
plt.savefig('exclusive_bids'+'.pdf', format='pdf', bbox_inches='tight')
#tikzplotlib.save("exclusive_bids.tex")
plt.show()