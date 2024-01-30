import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

colour = [y/255 for y in (16,78,139)]

# Create data points for x-axis
x = np.linspace(-5, 5, 1000)

# Define parameters for multiple Gaussian distributions
peaks = [(-3, 1), (0, 0.5), (2, 0.8), (5, 1.2)]  # Mean and standard deviation for each peak

# Generating the multi-modal distribution
multi_modal = np.zeros_like(x)
for peak in peaks:
    multi_modal += norm.pdf(x, peak[0], peak[1])

# Plotting the multi-modal distribution
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(x, multi_modal, label='Multi-modal Distribution', linewidth = 3, color="black")
ax1.set_xlabel(r'Price $\lambda$ ', fontsize=20)
ax1.set_ylabel('Probability', fontsize=20)

# Define discrete probabilities for two bars
bar_positions = [-3.5, -0.5, 3]  # Positions of the bars on the x-axis
bar_values = [0.3, 0.6, 0.55]  # Probabilities for two bars
ax1.bar(bar_positions, bar_values, width=2, alpha=0.5, label='Discrete Distribution', color=colour)


# Hide ticks on both x-axis and y-axis for both axes
ax1.set_xticks([])
ax1.set_yticks([])

# Hide the top and right spines to remove the surrounding box
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('probability_distribution_high.pdf', format='pdf', bbox_inches='tight')
plt.savefig('probability_distribution_high.svg', format='svg', bbox_inches='tight')
plt.show()

#-------------------------------------------------
# Second plot
#---------------------------------------------

# Create data points for x-axis
x = np.linspace(-5, 5, 1000)

# Define parameters for multiple Gaussian distributions
peaks = [(0, 1.5)]  # Mean and standard deviation for each peak

# Generating the multi-modal distribution
multi_modal = np.zeros_like(x)
for peak in peaks:
    multi_modal += norm.pdf(x, peak[0], peak[1])

# Plotting the multi-modal distribution
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(x, multi_modal, label='Multi-modal Distribution', linewidth = 3, color="black")
ax1.set_xlabel(r'Price $\lambda$ ', fontsize=20)
ax1.set_ylabel('Probability', fontsize=20)

# Define discrete probabilities for two bars
bar_positions = [0]  # Positions of the bars on the x-axis
bar_values = [0.2]  # Probabilities for two bars
ax1.bar(bar_positions, bar_values, width=2, alpha=0.5, label='Discrete Distribution', color=colour)

# Hide ticks on both x-axis and y-axis for both axes
ax1.set_xticks([])
ax1.set_yticks([])

# Hide the top and right spines to remove the surrounding box
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('probability_distribution_low.pdf', format='pdf', bbox_inches='tight')
plt.savefig('probability_distribution_low.svg', format='svg', bbox_inches='tight')
plt.show()
