"""
Executing this code leads to a sensitivity analysis of the linear program for exclusive groups regarding the number of bids. 
"""

#import packages
import gurobipy as gp #makes all Gurobi functions and classes available
from gurobipy import GRB #makes everything in class GRB available without a prefix (e.g., GRB.OPTIMAL)
import numpy as np
import random
import sys
from datetime import datetime, timedelta
import csv
import pandas as pd

#import functions
import Case_Study_Models as cs
import Optimization_Models as bm
import Auxiliary_Functions as func 


#-------------------------
# Dates for the whole year
#-------------------------

# Define the start and end date for the year 2017
start_date = datetime(2017, 1, 1)
end_date = datetime(2017, 12, 31)

# Initialize an empty list to store the dates
date_list = []

# Loop through the dates and add them to the list
current_date = start_date
while current_date <= end_date:
    date_list.append(current_date.strftime("%d/%m/%Y"))
    current_date += timedelta(days=1)
    
#-------------------------
# Draw N random days
#-------------------------

# Set a seed for the random number generator
random.seed(1)

# Randomly select 100 dates from the date_list without replacement (no duplicates)
date_list = random.sample(date_list, k=100)

#--------------------------
# Computation parameters
#--------------------------

# Number scenarios considered in bid determination
number_scenarios = 180 

# Bid type under consideration
bid_type = "exclusive" 

# Define runtime limit of optimization in seconds
timelimit = 10*60 

#Time set - 24 hours
Time_set = [i for i in range(24)]

# Bid sizes
bid_sizes = [10, 20, 30, 40, 50, 60, 70, 80] 

#---------------------------
# Iterating over case studies
#---------------------------

for case_study in ["thermal generator", "battery", "demand response"]:
    
    # Load parameters for case study   
    case_data = cs.case_data(case_study) 
    
    #----------------------------------
    # Write console output to .txt file
    #----------------------------------
    
    with open('Results_Sensitivity_Analysis/results_bidsize_' + case_study + "_" + bid_type + '.txt', 'w') as file:
    
        original_stdout = sys.stdout
        sys.stdout = file
    
        #List of result lists
        list_max_utility_lists = []
        list_bid_utility_lists = []
            
        #----------------------
        # Iterating over bid size
        #-----------------------
        
        for size_bid in bid_sizes:
            
            #Initializing bid_set
            Bid_set = [i for i in range(size_bid)] 
            
            #Sub-List of results
            max_utility_list = []
            bid_utility_list = []
                
            #--------------------------
            # Iterating over days
            #---------------------------
            
            for date in date_list:
                
                #----------------
                # Load forecast
                #-----------------
                
                Scenario_set = [i for i in range(number_scenarios)]
                Prices = func.scenario_generation(date, number_scenarios)
                Probabilities = [1/number_scenarios for i in Scenario_set]
                
                #------------------------
                # Generate bid
                #------------------------
                    
                bid, lp_runtime = bm.exclusive_linear(case_study, case_data, Time_set, Scenario_set, Bid_set, Prices, Probabilities, timelimit)
                
                #----------------------------
                # Evaluating bid on real price
                #----------------------------
                
                # Getting real price that day
                real_price = func.real_price(date)
                
                # Determine traded bundle - exclusive: the most profitable one
                bid_bundle, bid_utility = func.bid_outcome(case_study, case_data, Time_set, real_price, bid, bid_type, Bid_set)
                 
                # Determine the demand of an agent and its maximal possible utility
                best_bundle, max_utility = func.perfect_information_bid(case_study, case_data, Time_set, real_price)
             
                #----------------------------
                # Output results in .txt file
                #----------------------------
                
                print("----------------------------------")
                print("Day: ", date)
                print("Bid size: ", size_bid)
                print("Utility bid: ", bid_utility // 1)
                print("Bundle bid: ", [int(i) for i in bid_bundle])
                print("Maximal Utility: ", max_utility // 1)
                print("Optimal bundle: ", [int(i) for i in best_bundle])
                print("----------------------------------")
    
                #----------------------------
                # Append results to lists
                #----------------------------   
    
                max_utility_list.append(max_utility)
                bid_utility_list.append(bid_utility)
                    
            list_max_utility_lists.append(max_utility_list)
            list_bid_utility_lists.append(bid_utility_list)
                        
        print("Computation finished")       
        
        # Restore the original stdout
        sys.stdout = original_stdout     

    #----------------------------------
    # Write results to .csv file
    #----------------------------------
    
    # First DataFrame: Maximal attainable utility
    df1 = pd.DataFrame(list_max_utility_lists[0])
    df1.columns = ["Maximal attainable utility"]
    
    # Second DataFrame: Achieved utility by bids
    df2 = pd.DataFrame(list_bid_utility_lists).T
    df2.columns = ["Achieved utility, bid size =" + str(size) for size in bid_sizes]
    
    # Concatenate the DataFrames vertically
    combined_df = pd.concat([df1, df2], axis=1)
        
    # Write the combined DataFrame to a CSV file
    combined_df.to_csv('Results_Sensitivity_Analysis/results_bidsize_' + case_study + "_" + bid_type + '.csv', index=False)
            
print("Computation finished")     