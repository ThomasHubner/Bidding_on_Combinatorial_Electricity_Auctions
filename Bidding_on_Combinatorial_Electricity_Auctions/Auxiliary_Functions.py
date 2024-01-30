"""
Contains multiple auxiliary functions.

List of functions:
    - scenario_generation (generates a number of m price scenarios based on a point forecast)
    - real_price (reads the real price of a given date from the csv)
    - perfect_information_bid (computes the optimal dispatch and maximal utility which can be obtained, which equals a bid under perfect information)
    - bid_outcome (given a bid and the real price, it computes the market clearing outcome assuming a duality gap of zero of the market clearing program)
    
    
List of functions to explore impact of the probabilistic forecast:
    - scenario_generation_improved_information (generates scenarios as in "scenario_generation" but tightens the scenarios closer
                                                 to the real price afterwards to simulate improved information)
    - wasserstein_distance (computes the wasserstein distance between two discrete probability measures)
    - wasserstein_year (computes the wasserstein distances for a whole year)
    
"""

#import packages and data
import gurobipy as gp #makes all Gurobi functions and classes available
from gurobipy import GRB #makes everything in class GRB available without a prefix (e.g., GRB.OPTIMAL)
import numpy as np
import Case_Study_Models as cs
import pandas as pd
import ot
import random
from datetime import datetime, timedelta
import csv
import pandas as pd

##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def scenario_generation(forecast_date, number_scenarios):
    """
    Generates price scenarios by adding residuals of previous point forecasts
    to the point forecast of the next day. 

    Parameters
    ----------
    forecast_date : String in the form of "12/01/2017" 
        Date for which a probabilistic forecast is generated
    number_scenarios : int >0
        Number of scenarios in the discrete probability distribution

    Returns
    -------
    List of price scenarios of length n= number_scenarios

    """
    
    #Read csv with forecasts and real prices into pandas dataframe
    forecasts = pd.read_csv('Forecast_DE.csv')
    prices = pd.read_csv('Real_DE.csv')
    
    #Determine row number of forecast_date
    row_number = forecasts[ forecasts['Date'] == forecast_date ].index[0]
    
    #Get point forecast 
    point_forecast = forecasts.loc[row_number, "h0":].values.flatten().tolist()
    
    #Initalize scenario list with point forecast
    scenarios = [point_forecast]
    
    #Generate n-1 additional scenarios where n=number_scenarios
    
    #Iterate over past n-1 days and add residuals to point forecast
    for i in range(number_scenarios-1):
        
        #Get real and forecasted price of past i day 
        real_price = prices.loc[row_number-i-1, "h0":].values.flatten().tolist()
        forecast_price = forecasts.loc[row_number-i-1, "h0":].values.flatten().tolist()
        
        #Compute residual and add to point forecast
        residual = np.array(forecast_price) - np.array(real_price)
        scenario = np.array(point_forecast) - residual
        
        #Add scenario to list
        scenarios.append(scenario.tolist())
        
    return scenarios


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################

def real_price(date):
    """
    Reads the real price of date from csv.
    """
    
    #Read csv with forecasts and real prices into pandas dataframe
    prices = pd.read_csv('Real_DE.csv')
    
    #Determine row number of forecast_date
    row_number = prices[ prices['Date'] == date ].index[0]
    
    #Get real price
    real_price = prices.loc[row_number, "h0":].values.flatten().tolist()
    
    return real_price


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def perfect_information_bid(case_study, case_data, Time_set, real_price):
    """
    Computes the dispatch and profit under perfect price information.

    Parameters
    ----------
    ccase_study : String 
        Selects the case study which is run. Possible values: "thermal generator"
    case_data : List
        List of parameters necessary to specify the case study. 
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    real_price : list of float
        Real prices for all hours.

    Returns
    -------
    bundle : list
        List of buy and sell quantities for hours in Time_set.
    utility : float
       Utility gained by bundle given real_price (equals indirect utility).

    """
    
    
    #Setting Scenarios to perfect information
    Scenario_set = [0]
    Probabilities = [1]
    Prices = [real_price]
    
    #----------------------------------------
    # Loading case study model
    #----------------------------------------
 
    if case_study == "thermal generator":
        
        #Read unit characteristics from "case_data"
        No_load_cost, Marginal_costs, Startup_cost, Shutdown_cost, Rampup_rate, Rampdown_rate, Min_stable_generation, Max_production_limit, Max_production_block, Min_up_time, Min_down_time, Initial_operating_state, Initial_off_hours, Initial_on_hours = case_data
        
        #Load model
        m = cs.thermal_generator(Time_set, Scenario_set, Prices, Probabilities, No_load_cost, Marginal_costs, Startup_cost, Shutdown_cost, Rampup_rate, Rampdown_rate, Min_stable_generation, Max_production_limit, Max_production_block, Min_up_time, Min_down_time, Initial_operating_state, Initial_off_hours, Initial_on_hours)
        m.update()
        
    elif case_study == "battery":
        
        #Read unit characteristics from "case_data"
        Max_charging, Max_discharging, charging_efficiency, discharging_efficiency, Min_StateofCharge, Max_StateofCharge, Initial_StateofCharge = case_data
        
        #Load model
        m = cs.battery(Time_set, Scenario_set, Prices, Probabilities, Max_charging, Max_discharging, charging_efficiency, discharging_efficiency, Min_StateofCharge, Max_StateofCharge, Initial_StateofCharge)
        m.update()      
        
    elif case_study == "demand response":
        
        #Read unit characteristics from "case_data"
        Efficiency_Heat_Pump, Efficiency_Gas_Boiler, Loss_coefficient, Heat_Load, Cost_Gas, Load_serving_price, Capacity_Storage, Max_charging_storage, Max_discharging_storage, Capacity_Heat_Pump, Capacity_Gas_Boiler, Initial_StateofCharge, Daily_Fixed_cost = case_data
        
        #Load model
        m = cs.demand_response(Time_set, Scenario_set, Prices, Probabilities, Efficiency_Heat_Pump, Efficiency_Gas_Boiler, Loss_coefficient, Heat_Load, Cost_Gas, Load_serving_price, Capacity_Storage, Max_charging_storage, Max_discharging_storage, Capacity_Heat_Pump, Capacity_Gas_Boiler, Initial_StateofCharge, Daily_Fixed_cost)
        m.update()   
        
    else:
        print("Case study not known.")
        return
    
    #-----------------------------------
    # Solve case study and retrieve dispatches and valuations
    #-----------------------------------
    m.Params.LogToConsole = 0
    m.optimize()
    
    #Retrieve dispatches and profit
    bundle = [ m.getVarByName("x_tilde"+"["+str(0)+","+str(t)+"]").X for t in Time_set ] 
    utility = m.ObjVal
    
    return bundle, utility


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def bid_outcome(case_study, case_data, Time_set, real_price, bid, bid_type, Bid_set):
    """
    Given a bid and the real price, it computes the market clearing outcome.
    That is, it retruns the resulting traded bundle and the utility gained by this bid.

    Parameters
    ----------
    case_study : String 
        Selects the case study which is run. Possible values: "thermal generator"
    case_data : List
        List of parameters necessary to specify the case study. 
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    real_price : list of floats
        Real prices for all hours.
    bid : dictionary
        Contains all atomic bids (x,p) pairs
    bid_type : string
        Exclusive group or self-schedule?
    Bid_set : list of integers 0,1,2,3, .... B
        List of bid indices.

    Returns
    -------
    bundle : list
        List of buy and sell quantities for hours in Time_set.
    utility : float
       Utility gained by bundle given real_price.

    """
    
    #----------------------------------------
    # Determining traded bundle
    #----------------------------------------
    
    #List of profits of the single atomic bids 
    profits = np.array( [ ( bid["p"+str(b)] - sum( real_price[t] * bid["x"+str(b)][t] for t in Time_set) ) for b in Bid_set ] )
    
    #Determine bundle for exclusive group
    if bid_type == "exclusive":
        
        if max(profits) >= 0:
            b_opt = np.argmax(profits)
            bundle = bid["x"+str(b_opt)]
        else:
            bundle = np.zeros(len(Time_set))
                

    #----------------------------------------
    # Determine utility gained by traded bundle
    #----------------------------------------
    
    #Setting Scenarios to perfect information
    Scenario_set = [0]
    Probabilities = [1]
    Prices = [real_price]
 
    #Load case study model
    if case_study == "thermal generator":
        
        #Read unit characteristics from "case_data"
        No_load_cost, Marginal_costs, Startup_cost, Shutdown_cost, Rampup_rate, Rampdown_rate, Min_stable_generation, Max_production_limit, Max_production_block, Min_up_time, Min_down_time, Initial_operating_state, Initial_off_hours, Initial_on_hours = case_data
        
        #Load model
        m = cs.thermal_generator(Time_set, Scenario_set, Prices, Probabilities, No_load_cost, Marginal_costs, Startup_cost, Shutdown_cost, Rampup_rate, Rampdown_rate, Min_stable_generation, Max_production_limit, Max_production_block, Min_up_time, Min_down_time, Initial_operating_state, Initial_off_hours, Initial_on_hours)
        m.update()
        
    elif case_study == "battery":
        
        #Read unit characteristics from "case_data"
        Max_charging, Max_discharging, charging_efficiency, discharging_efficiency, Min_StateofCharge, Max_StateofCharge, Initial_StateofCharge = case_data
        
        #Load model
        m = cs.battery(Time_set, Scenario_set, Prices, Probabilities, Max_charging, Max_discharging, charging_efficiency, discharging_efficiency, Min_StateofCharge, Max_StateofCharge, Initial_StateofCharge)
        m.update()  
        
    elif case_study == "demand response":
        
        #Read unit characteristics from "case_data"
        Efficiency_Heat_Pump, Efficiency_Gas_Boiler, Loss_coefficient, Heat_Load, Cost_Gas, Load_serving_price, Capacity_Storage, Max_charging_storage, Max_discharging_storage, Capacity_Heat_Pump, Capacity_Gas_Boiler, Initial_StateofCharge, Daily_Fixed_cost = case_data
        
        #Load model
        m = cs.demand_response(Time_set, Scenario_set, Prices, Probabilities, Efficiency_Heat_Pump, Efficiency_Gas_Boiler, Loss_coefficient, Heat_Load, Cost_Gas, Load_serving_price, Capacity_Storage, Max_charging_storage, Max_discharging_storage, Capacity_Heat_Pump, Capacity_Gas_Boiler, Initial_StateofCharge, Daily_Fixed_cost)
        m.update()    
        
    else:
        print("Case study not known.")
        return
    
    #Fix bundle to certain value
    m.addConstrs( m.getVarByName("x_tilde"+"["+str(s)+","+str(t)+"]") == bundle[t]  for t in Time_set for s in Scenario_set )
    
    #Solve model and retrieve utility
    
    m.Params.LogToConsole = 0
    m.optimize()

    if m.SolCount > 0: #model has found a solution - bundle is feasible
        utility = m.ObjVal  
        
    else: #model has found no solution - bundle is infeasible
        utility = -1
        print("Bundle infeasible")
        
    
    return bundle, utility

##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def scenario_generation_improved_information(forecast_date, number_scenarios, improvement_scalar):
    """
    Generates price scenarios by adding residuals of previous point forecasts
    to the point forecast of the next day.
    Tightens the scenarios closer to the real price afterwards to simulate improved information.
    
    Parameters
    ----------
    forecast_date : String in the form of "12/01/2017" 
        Date for which a probabilistic forecast is generated
    number_scenarios : int >0
        Number of scenarios in the discrete probability distribution
    improvement_scalar : float in [0,1]
        Tightens the scenario closer to real price. If 1 then scenarios equal the real price. If 0 the scenarios are normal.

    Returns
    -------
    List of price scenarios of length n= number_scenarios

    """
    
    #Read csv with forecasts and real prices into pandas dataframe
    forecasts = pd.read_csv('Forecast_DE.csv')
    prices = pd.read_csv('Real_DE.csv')
    
    #Determine row number of forecast_date
    row_number = forecasts[ forecasts['Date'] == forecast_date ].index[0]
    
    #Get point forecast 
    point_forecast = forecasts.loc[row_number, "h0":].values.flatten()
    
    #Initalize scenario list with point forecast
    #Tighten point forecast - improve it
    real_price_next_day = prices.loc[row_number, "h0":].values.flatten()
    difference = point_forecast - real_price_next_day
    improved_point_forecast = point_forecast - improvement_scalar * difference # if improvement_scalar==1 then improved_scenario==real price
    scenarios = [improved_point_forecast.tolist()]
    
    #Generate n-1 additional scenarios where n=number_scenarios
    #Iterate over past n-1 days and add residuals to point forecast
    for i in range(number_scenarios-1):
        
        #Get real and forecasted price of past i day 
        real_price = prices.loc[row_number-i-1, "h0":].values.flatten().tolist()
        forecast_price = forecasts.loc[row_number-i-1, "h0":].values.flatten().tolist()
        
        #Compute residual and add to point forecast
        residual = np.array(forecast_price) - np.array(real_price)
        scenario = np.array(point_forecast) - residual
        
        #Tighten scenario - improve it
        difference = scenario - real_price_next_day
        improved_scenario = scenario - improvement_scalar * difference # if improvement_scalar==1 then improved_scenario==real price
        
        #Add scenario to list
        scenarios.append(improved_scenario.tolist())
        
    return scenarios


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def wasserstein_distance(P_scenarios, P_probs, Q_scenarios, Q_probs):
    """
    Computes the Wasserstein distance between two discrete probability distributions P and Q.
    """
    
    # Convert scenarios and probabilities to numpy arrays
    P_samples = np.array(P_scenarios)
    Q_samples = np.array(Q_scenarios)

    # Compute the distance matrix
    distance_matrix = np.linalg.norm(P_samples[:, np.newaxis] - Q_samples, axis=2)

    # Calculate the 1-Wasserstein distance using Earth Mover's Distance (EMD)
    wasserstein_distance = ot.emd2(P_probs, Q_probs, distance_matrix)
    
    return wasserstein_distance


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def wasserstein_year():
    """
    Computes the wasserstein distances between the probability distribution obtained by the scenario generation method above 
    and the degenerate distribution given by the real price for a whole year and write its to a csv.
    """
    
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
        
    #Time set - 24 hours
    Time_set = [i for i in range(24)]
    
    #List of wasserstein distances
    list_wass1 = []
    list_wass2 = []
    
    #Iterate over days
    for date in date_list:
        
        #Get forecast
        scenarios1 = scenario_generation_improved_information(date, 180)
        scenarios2 = scenario_generation(date, 180)
        Probabilities = [1/180 for i in range(180)]
        
        #Real price
        realprice = [real_price(date)]
        
        #Distributions
        wass1 = wasserstein_distance(realprice, [1], scenarios1, Probabilities)
        wass2 = wasserstein_distance(realprice, [1], scenarios2, Probabilities)
        
        #Add to list
        list_wass1.append(wass1)
        list_wass2.append(wass2)
        
        
    # Create DataFrames from the lists
    df = pd.DataFrame( [list_wass1, list_wass2] ).T
    
    # Set the headers for the columns
    df.columns = ["Wasserstein improved forecast", "Wasserstein real forecast"]

    # Write the combined DataFrame to a CSV file
    df.to_csv('Wasserstein_distances.csv', index=False)
    
    return

