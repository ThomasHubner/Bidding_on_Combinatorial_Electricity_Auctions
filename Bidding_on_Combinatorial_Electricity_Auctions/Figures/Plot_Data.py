"""
Plot some of the data involved in the paper:
    - heat load data
    - price and price forecast data
"""

import matplotlib.pyplot as plt
import numpy as np

colour = [y/255 for y in (16,78,139)]

#----------------
# Heat load plot
#----------------

# Generate sample data for 24 hours
hours = np.arange(1, 25)
heat_load = np.array([19, 20, 20, 21, 24, 32, 38, 36, 36, 35, 33, 32, 31, 31, 31, 32, 33, 33, 33, 33, 32, 29, 23, 20])

plt.figure(figsize=(10, 7))
plt.plot(hours, heat_load, label='Heat load', marker='o', linestyle='-', linewidth=2, color=colour)

# Increase font size for x and y-axis labels
plt.xlabel('Hours', fontsize=18)
plt.ylabel('Heat load (MWh)', fontsize=18)

# Add title
#plt.title('Heat Load Profile for a Day', fontsize=20)


# Set x-axis ticks to show every second hour
plt.xticks(hours[::2])

# Set font size for x-axis tick labels
plt.xticks(fontsize=16)

# Set font size for y-axis tick labels
plt.yticks(fontsize=16)

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(False)
plt.savefig('heat_load_profile.pdf', format='pdf', bbox_inches='tight')
plt.savefig('heat_load_profile.svg', format='svg', bbox_inches='tight')
#plt.show()


#----------------
# Price plot
#----------------

# Price data for 24 hours (taken from csvs)
hours = np.arange(1, 25)
real_price = [26.91, 24.77, 24.45, 23.05, 23.45, 27.24,	33.09, 37.95, 38.99, 37.97, 35.93, 33.32, 30.02, 28.09,	27.63, 28.29, 28.36, 30.43, 34.67, 38.98, 39.96, 37.91, 35.95, 32.02]
price_forecast = [26.17, 24.87, 23.73, 22.96, 24.31, 25.90,	34.56, 40.88, 42.43, 37.08, 33.56, 30.44, 27.54, 25.10, 23.75, 24.15, 25.26, 28.51, 33.60, 38.09, 38.53, 34.31, 32.51, 29.39]


plt.figure(figsize=(10, 7))
plt.plot(hours, real_price, label='Real price', marker='o', linestyle='-', linewidth=2, color="black")
plt.plot(hours, price_forecast, label='Price forecast', marker='o', linestyle='-', linewidth=2, color="royalblue")

# Increase font size for x and y-axis labels
plt.xlabel('Hours', fontname='Arial', fontsize=18)
plt.ylabel('Price (€/MWh)', fontname='Arial', fontsize=18)

# Add title
#plt.title('Real Price vs Price Forecast for 31/03/2017', fontsize=20)


# Add legend
plt.legend(fontsize=18, loc='upper center', bbox_to_anchor=(0.6, 1))

# Set x-axis ticks to show every second hour
plt.xticks(hours[::2])

# Set font size for x-axis tick labels
plt.xticks(fontsize=16)

# Set font size for y-axis tick labels
plt.yticks(fontsize=16)

# Hide the top and right spines to remove the surrounding box
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Show the plot
plt.grid(False)
plt.savefig('real_forecasted_price.pdf', format='pdf', bbox_inches='tight')
plt.savefig('real_forecasted_price.svg', format='svg', bbox_inches='tight')
plt.show()


