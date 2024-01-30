"""
Contains functions that define and run the optimization models for bid determination.

List of functions:
    - exclusive_lp (LP with pre-selection of bids to determine exclusive group)
    - self_schedule (optimization model to determine optimal self-schedule)
"""

#import packages and data
import gurobipy as gp #makes all Gurobi functions and classes available
from gurobipy import GRB #makes everything in class GRB available without a prefix (e.g., GRB.OPTIMAL)
import numpy as np
import Case_Study_Models as cs

##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################

def exclusive_linear(case_study, case_data, Time_set, Scenario_set, Bid_set, Prices, Probabilities, timelimit):
    """
    Determines an exclusive bid by linear program.

    Parameters
    ----------
    case_study : String 
        Selects the case study which is run. Possible values: "thermal generator"
    case_data : List
        List of parameters necessary to specify the case study. 
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    Scenario_set : list of integers 0,1,2,3, .... S
        List of scenario indices.
    Bid_set : list of integers 0,1,2,3, .... B
        List of bid indices.
    Prices : list of list
        List of prices (length: Time_set) for each scenario in Scenario_set 
    Probabilities : list of floats
        List of probability for each scenario in Scenario_set
    timelimit : float
        Sets the runtime limit of gurobi

    Returns
    -------
    exclusive_bid : dictionary
        Dictionary of atomic bids (quantity and price)

    """
    
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
    
    #-----------------------------------------------------
    # Solve case study and retrieve bundles and valuations
    #-----------------------------------------------------
    m.Params.LogToConsole = 0 #gurobi log output: 0(no), 1(yes) 
    m.optimize()
    
    bundles = []
    valuations = []
    
    for s in Scenario_set :
        bundles.append( [ m.getVarByName("x_tilde"+"["+str(s)+","+str(t)+"]").X for t in Time_set ] )
        valuations.append( m.getVarByName("v"+"["+str(s)+"]").X )

    #-------------------------------------------
    # Create optimization model
    #-------------------------------------------

    #Create a new model 
    m = gp.Model("exclusive - linear") 
    
    # 1) Create binary variables
    delta = m.addVars(Scenario_set, vtype = GRB.BINARY, name = "delta") 
    gamma = m.addVars(Scenario_set, Scenario_set, vtype = GRB.BINARY, name = "gamma") 
    
    # Binaries could be relaxed to continuous with [0,1] bounds - we let integer program be solved at root node of branch&bound
    # This ensures that always a vertex solution is chosen and not, if the LP has infinitely many solutions, one in between two vertices.
    
    # 2) Create constraints
    m.addConstrs( sum (gamma[b,s] for b in Scenario_set)  <= 1 for s in Scenario_set)
    m.addConstrs( gamma[b,s] <= delta[b] for s in Scenario_set for b in Scenario_set)
    m.addConstr( sum( delta[b] for b in Scenario_set) == len(Bid_set) )
    
    # 3) Set objective
    m.setObjective( sum(Probabilities[s] * sum ( (valuations[b] - sum(Prices[s][t] * bundles[b][t] for t in Time_set)) * gamma[b,s] for b in Scenario_set)  for s in Scenario_set), GRB.MAXIMIZE)
    
    #------------------------
    # Determine atomic bids
    #------------------------
    m.Params.LogToConsole = 1 #gurobi log output: 0(no), 1(yes) 
    m.setParam('TimeLimit', timelimit) 
    m.setParam('NodeLimit', 1) #avoid starting branch-and-bound due to numerical inaccuracies, go with the found solution.
    m.optimize()
    
    #--------------------------
    # Convert solution to bids
    #-------------------------

    exclusive_bid = {}
    b = 0
    for s in Scenario_set:
        if delta[s].X < 1.01 and delta[s].X > 0.99 : #bid selected? - account for numerical rounding errors - 1 is not always 1 but sometimes 0.9995 or so
            exclusive_bid.update( {"x"+str(b) : bundles[s]} )
            exclusive_bid.update( {"p"+str(b) : valuations[s]} )
            b = b+1   
    
    return exclusive_bid, m.Runtime


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################

def self_schedule(case_study, case_data, Time_set, Scenario_set, Prices, Probabilities, timelimit, real_price):
    """
    Determines a self-schedule.

    Parameters
    ----------
    case_study : String 
        Selects the case study which is run. Possible values: "thermal generator"
    case_data : List
        List of parameters necessary to specify the case study. 
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    Scenario_set : list of integers 0,1,2,3, .... S
        List of scenario indices.
    Prices : list of list
        List of prices (length: Time_set) for each scenario in Scenario_set 
    Probabilities : list of floats
        List of probability for each scenario in Scenario_set
    timelimit : float
        Sets the runtime limit of gurobi
    real_price : list
        Real ex post electrcity price

    Returns
    -------
    self schedule : list
        A bundle of power bough/sold
    utility : float
        Utility of that bundle

    """
    
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


    #-------------------------------------------
    # Add Scenario coupling constraint
    #-------------------------------------------
    
    m.addConstrs( m.getVarByName("x_tilde"+"["+str(s1)+","+str(t)+"]") == m.getVarByName("x_tilde"+"["+str(s2)+","+str(t)+"]") for t in Time_set for s1 in Scenario_set for s2 in Scenario_set)
    
    #------------------------
    # Determine schedule
    #------------------------
    m.Params.LogToConsole = 1 #gurobi log output: 0(no), 1(yes) 
    m.setParam('TimeLimit', timelimit) 
    m.optimize()
    
    self_dispatch = [m.getVarByName("x_tilde"+"["+str(1)+","+str(t)+"]").X for t in Time_set]
        
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
    m.addConstrs( m.getVarByName("x_tilde"+"["+str(s)+","+str(t)+"]") == self_dispatch[t]  for t in Time_set for s in Scenario_set )
    
    #Solve model and retrieve utility
    
    m.Params.LogToConsole = 0
    m.optimize()

    if m.SolCount > 0: #model has found a solution - bundle is feasible
        utility = m.ObjVal  
    
    return self_dispatch, utility