"""
Executing this code leads to a comparison of the discussed bidding approaches.
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
import time

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

# Randomly select 5 dates from the date_list without replacement (no duplicates)
date_list = random.sample(date_list, k=5)

#-------------------------
# Parameters
#-------------------------
 
#Time set - 24 hours
Time_set = [i for i in range(24)]

# Define runtime limit of optimization
timelimit = 30*60 #30min

# Bid type under consideration
bid_types = ["ungrouped_MILP", "exclusive_MILP", "exclusive_LP", "self-schedule"]

#--------------------------
# Iterating over case studies
#-------------------------

for case_study in ["thermal generator", "battery", "demand response"]:
    
    # Load parameters for case study   
    case_data = cs.case_data(case_study) 
    
    #----------------------------------
    # Write console output to .txt file
    #----------------------------------
    
    with open('Results_Comparison/log_comparison_' + case_study + '.txt', 'w') as file:
    
        original_stdout = sys.stdout
        sys.stdout = file
    
        #List of result lists
        list_max_utility_lists = []
        list_bid_utility_lists = []
        list_time_lists = []
            
        #----------------------
        # Iterating over bid size
        #-----------------------
        
        for bid_type in bid_types: 
            
            # Set bid size
            if bid_type == "exclusive_MILP": # is irrelevant only pro-forma
                size_bid = 24
                number_scenarios = 30
            elif bid_type == "exclusive_LP":
                size_bid = 24
                number_scenarios = 360
            elif bid_type == "ungrouped_MILP":
                size_bid = 8
                number_scenarios = 30
            elif bid_type == "self-schedule":
                size_bid = 1
                number_scenarios = 360
                
            
            #Initializing bid_set
            Bid_set = [i for i in range(size_bid)] 
            
            #Sub-List of results
            max_utility_list = []
            bid_utility_list = []
            time_list = []
                
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
                # Real price
                #------------------------
                
                real_price = func.real_price(date)
                
                #------------------------
                # Generate bid
                #------------------------
                 
                if bid_type == "exclusive_LP":
                    
                    start_time = time.time() #measure time 
                    bid, lp_runtime = bm.exclusive_linear(case_study, case_data, Time_set, Scenario_set, Bid_set, Prices, Probabilities, timelimit)
                    end_time = time.time() #measure time 
                    bid_bundle, bid_utility = func.bid_outcome(case_study, case_data, Time_set, real_price, bid, "exclusive", Bid_set)
                
                elif bid_type == "exclusive_MILP":
                    
                    start_time = time.time() #measure time 
                    bid = bm.exclusive_milp(case_study, case_data, Time_set, Scenario_set, Bid_set, Prices, Probabilities, 0, timelimit)
                    end_time = time.time() #measure time
                    bid_bundle, bid_utility = func.bid_outcome(case_study, case_data, Time_set, real_price, bid, "exclusive", Bid_set)
                
                elif bid_type == "ungrouped_MILP":
                    
                    start_time = time.time() #measure time
                    bid = bm.ungrouped_milp(case_study, case_data, Time_set, Scenario_set, Bid_set, Prices, Probabilities, timelimit)
                    end_time = time.time() #measure time
                    bid_bundle, bid_utility = func.bid_outcome(case_study, case_data, Time_set, real_price, bid, "ungrouped", Bid_set)
                
                elif bid_type == "self-schedule":
                    
                    start_time = time.time() #measure time
                    bid_bundle, bid_utility = bm.self_schedule(case_study, case_data, Time_set, Scenario_set, Prices, Probabilities, timelimit, real_price)
                    end_time = time.time() #measure time
                    bid = bid_bundle
                    
                #--------------------------
                # Output
                #---------------------------
                    
                #Perfect information result
                best_bundle, max_utility = func.perfect_information_bid(case_study, case_data, Time_set, real_price)
                
                print("----------------------------------")
                print("Day: ", date)
                print("Bid size: ", size_bid)
                print("Utility bid: ", bid_utility // 1)
                print("Bundle bid: ", [int(i) for i in bid_bundle])
                print("Maximal Utility: ", max_utility // 1)
                print("Optimal bundle: ", [int(i) for i in best_bundle])
                print("----------------------------------")
                
                print("----------------------------------")
                print("Bid: ", bid)
                print("----------------------------------")
    
                max_utility_list.append(max_utility)
                bid_utility_list.append(bid_utility)
                time_list.append(end_time - start_time)
                
            list_max_utility_lists.append(max_utility_list)
            list_bid_utility_lists.append(bid_utility_list)
            list_time_lists.append(time_list)
             
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
    df2.columns = ["Achieved utility, bid type=" + str(bid_type) for bid_type in bid_types]
    
    # Third DataFrame: Computation time
    df3 = pd.DataFrame(list_time_lists).T
    df3.columns = ["Computation time, bid type=" + str(bid_type) for bid_type in bid_types]
    
    # Concatenate the DataFrames vertically
    combined_df = pd.concat([df1, df2, df3], axis=1)
        
    # Write the combined DataFrame to a CSV file
    combined_df.to_csv('Results_Comparison/results_comparison_' + case_study + '.csv', index=False)
            
print("Computation finished")   

