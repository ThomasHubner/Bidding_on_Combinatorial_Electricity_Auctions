"""
Contains functions that describe the valuations v and feasible sets M of the generator, load and storage system. 

List of functions:
    - case_data (contains and returns the parameters of the case studies)
    - thermal_generator (returns an optimization model defining the thermal generator)
    - battery (returns an optimization model defining the battery)
    - demand_response (returns an optimization model defining the flexible load)
"""

#import packages and data
import gurobipy as gp #makes all Gurobi functions and classes available
from gurobipy import GRB #makes everything in class GRB available without a prefix (e.g., GRB.OPTIMAL)
import numpy as np


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def case_data(case_study):
    """
    Contains the parameters for the case studies. Returns them in a list format.

    Parameters
    ----------
    case_study : string
        Which case study is considered (e.g. thermal generator)

    Returns
    -------
    case_data : list
        List of parameters needed to define the case study model.
    """
    
    if case_study == "thermal generator":
        
        No_load_cost = 2000
        Marginal_costs = [20, 25, 40]
        Startup_cost = 2000
        Shutdown_cost = 500
        Rampup_rate = 200
        Rampdown_rate = 200
        Min_stable_generation = 100
        Max_production_limit = 600
        Max_production_block = [200,200,200]
        Min_up_time = 4
        Min_down_time = 4
        Initial_operating_state = 0
        Initial_off_hours = 0
        Initial_on_hours = 0
        
        case_data = [No_load_cost, Marginal_costs, Startup_cost, Shutdown_cost, Rampup_rate, Rampdown_rate, Min_stable_generation, Max_production_limit, Max_production_block, Min_up_time, Min_down_time, Initial_operating_state, Initial_off_hours, Initial_on_hours]
        
        return case_data
    
    elif case_study == "battery":
        
        Max_charging = 10
        Max_discharging = 10
        charging_efficiency = 0.9
        discharging_efficiency = 0.9
        Min_StateofCharge = 0
        Max_StateofCharge = 20
        Initial_StateofCharge = 10
        
        case_data = [Max_charging, Max_discharging, charging_efficiency, discharging_efficiency, Min_StateofCharge, Max_StateofCharge, Initial_StateofCharge]
        
        return case_data
    
    elif case_study == "demand response":
        
        Efficiency_Heat_Pump = 1
        Efficiency_Gas_Boiler = 0.9
        Loss_coefficient = 0.01 
        Heat_Load = [19, 20, 20, 21, 24, 32, 38, 36, 36, 35, 33, 32, 31, 31, 31, 32, 33, 33, 33, 33, 32, 29, 23, 20]
        Cost_Gas = 20
        Load_serving_price = 40
        Capacity_Storage = 40 
        Max_charging_storage = 20 
        Max_discharging_storage = 20 
        Capacity_Heat_Pump = 30
        Capacity_Gas_Boiler = 10
        Initial_StateofCharge = 0
        Daily_Fixed_cost = 0
        
        case_data = [Efficiency_Heat_Pump, Efficiency_Gas_Boiler, Loss_coefficient, Heat_Load, Cost_Gas, Load_serving_price, Capacity_Storage, Max_charging_storage, Max_discharging_storage, Capacity_Heat_Pump, Capacity_Gas_Boiler, Initial_StateofCharge, Daily_Fixed_cost]
        
        return case_data
    
    else:
        
        return 0
    
##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################

def thermal_generator(Time_set, Scenario_set, Prices, Probabilities,
                No_load_cost, Marginal_costs, Startup_cost, Shutdown_cost,
                Rampup_rate, Rampdown_rate, Min_stable_generation, Max_production_limit, 
                Max_production_block, Min_up_time, Min_down_time, 
                Initial_operating_state, Initial_off_hours, Initial_on_hours):
    """
    Optimizaton model of thermal generator. Objective: optimal dispatch for each price scenario in Prices. (separable in scenarios)

    Parameters
    ----------
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    Scenario_set : list of integers 0,1,2,3, .... S
        List of scenario indices.
    Prices : list of list
        List of prices (length: Time_set) for each scenario in Scenario_set 
    Probabilities : list of floats
        List of probability for each scenario in Scenario_set
    No_load_cost : float
        Fixed cost when running.
    Marginal_costs : list of floats
        List of marginal costs defining a piecewise linear cost curve. 
    Startup_cost : float
        Cost for starting up the generator.
    Shutdown_cost : flloat
        Cost for shuting down the generator.
    Rampup_rate : float
        Maximal ramping up.
    Rampdown_rate : float
        Maximal ramping down.
    Min_stable_generation : float
        Minimal generation limit.
    Max_production_limit : float
        Maximal generation limit. 
    Max_production_block : list of floats
        List of maximal power levels per block - levels where marginal cost changes.
    Min_up_time : integer >=1
        Number of time steps generator needs to be up before shutting down again.
    Min_down_time : integer >=1
        Number of time steps generator needs to be down before starting up again.
    Initial_operating_state : float
        Generation level in last hour of previous day (i.e. 23:00-00:00).  
    Initial_off_hours : integer
        Number of hours the producer needs to remain off in the first hours of the day.
    Initial_on_hours : integer
        Number of hours the producer needs to remain on in the first hours of the day.

    Returns
    -------
    gurobi optimization model m

    """
    
    #Preprocessing data
    Set_blocks = [i for i in range(len(Max_production_block))] #Set of blocks with different marginal cost
    Inital_commitment = 0 if Initial_operating_state == 0 else 1 #Initial commitment variable
    
    #Create a new model 
    m = gp.Model("thermal generator") 
    
    
    # 1) Variables
    
    ### 1.1) Market variables
    x_tilde = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = "x_tilde") #power sold/produced
    v = m.addVars( Scenario_set, vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = "v") #auxiliary variable for valuation
    
    ### 1.2) Production variables
    p_block = m.addVars( Scenario_set, Time_set, Set_blocks, vtype = GRB.CONTINUOUS, ub = 0, lb = -GRB.INFINITY, name = "p_block") #power produced in generation block /is negative following convention in paper
    u = m.addVars( Scenario_set, Time_set, vtype = GRB.BINARY, name = "u") #commitment variable: "on" or "off"
    
    ### 1.3) Auxiliary start-up/shut-down cost variables
    c_up = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, name = "c_up") #realized start-up costs
    c_down = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, name = "c_down") #realized shut-down costs
    
    
    # 2) Objective
    
    ### 2.1) Valuation - cost is negative
    m.addConstrs( v[s] == sum( - No_load_cost * u[s,t] - c_up[s,t] - c_down[s,t] + sum(Marginal_costs[q] * p_block[s,t,q] for q in Set_blocks) for t in Time_set ) for s in Scenario_set)
    
    ### 2.2) Objective function
    m.setObjective( sum(Probabilities[s] * (v[s] - sum(Prices[s][t] * x_tilde[s,t] for t in Time_set)) for s in Scenario_set), GRB.MAXIMIZE)
    
    
    # 3) Constraints
    
    ### 3.1) Linking power produced per block to toal power produced
    m.addConstrs( x_tilde[s,t] == sum(p_block[s,t,q] for q in Set_blocks) for t in Time_set for s in Scenario_set )
    
    ### 3.2) Commitment constraints
    m.addConstrs( -p_block[s,t,q] <= u[s,t] * Max_production_block[q]  for q in Set_blocks for t in Time_set for s in Scenario_set )
    m.addConstrs( Min_stable_generation * u[s,t] <= -sum(p_block[s,t,q] for q in Set_blocks) for t in Time_set for s in Scenario_set )
    
    ### 3.3) Ramping constraints
    m.addConstrs( (- x_tilde[s,t] + x_tilde[s,t-1] <= Rampup_rate for t in Time_set[1:] for s in Scenario_set), name="ramping I")
    m.addConstrs( (- x_tilde[s,t] + x_tilde[s,t-1] >= - Rampdown_rate for t in Time_set[1:] for s in Scenario_set), name="ramping II" ) 
    m.addConstrs( (- x_tilde[s,Time_set[0]] - Initial_operating_state <= Rampup_rate for s in Scenario_set), name="ramping III" ) #Initial operating state is >=0 but x_tilde <= 0
    m.addConstrs( (- x_tilde[s,Time_set[0]] - Initial_operating_state >= - Rampdown_rate for s in Scenario_set), name="ramping IV" )     
    
    ### 3.4) Cost constraints
    m.addConstrs( c_up[s,t] >= (u[s,t] - u[s,t-1]) * Startup_cost for t in Time_set[1:] for s in Scenario_set )
    m.addConstrs( c_down[s,t] >= (u[s,t-1] - u[s,t]) * Shutdown_cost for t in Time_set[1:] for s in Scenario_set )
    m.addConstrs( c_up[s,Time_set[0]] >= (u[s,Time_set[0]] - Inital_commitment) * Startup_cost  for s in Scenario_set )
    m.addConstrs( c_down[s,Time_set[0]] >= (Inital_commitment - u[s,Time_set[0]]) * Shutdown_cost  for s in Scenario_set )  
    
    ### 3.5) Inital up- and down time constraints
    m.addConstrs( 0 == sum( u[s,t] for t in Time_set[0:Initial_off_hours]) for s in Scenario_set )
    m.addConstrs( 0 == sum( (1-u[s,t]) for t in Time_set[0:Initial_on_hours]) for s in Scenario_set )
    
    ### 3.6) Minimum-up and -down time constraints
    m.addConstrs( Min_up_time * (u[s,t] - u[s,t-1]) <= sum( u[s,j] for j in Time_set[t : t + Min_up_time]) for s in Scenario_set for t in Time_set[ Initial_on_hours+1 : -Min_up_time ])
    m.addConstrs( -Min_down_time * (u[s,t] - u[s,t-1]) <= sum( (1-u[s,j]) for j in Time_set[t : t + Min_down_time]) for s in Scenario_set for t in Time_set[ Initial_on_hours+1 : -Min_down_time ])   
    if Min_up_time >= 2:
        m.addConstrs( sum( u[s,j] for j in Time_set[t:] ) - (u[s,t] - u[s,t-1]) >= 0 for s in Scenario_set for t in Time_set[ -Min_up_time + 1 : ])
    if Min_down_time >= 2:   
        m.addConstrs( sum( (1-u[s,j]) for j in Time_set[t:] ) - (u[s,t-1] - u[s,t]) >= 0 for s in Scenario_set for t in Time_set[ -Min_down_time + 1 : ])
    
    return m


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def battery(Time_set, Scenario_set, Prices, Probabilities,
                Max_charging, Max_discharging, charging_efficiency, discharging_efficiency, 
                Min_StateofCharge, Max_StateofCharge, Initial_StateofCharge):
    """
    Optimizaton model of battery storage system. Objective: optimal dispatch for each price scenario in Prices. (separable in scenarios)

    Parameters
    ----------
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    Scenario_set : list of integers 0,1,2,3, .... S
        List of scenario indices.
    Prices : list of list
        List of prices (length: Time_set) for each scenario in Scenario_set 
    Probabilities : list of floats
        List of probability for each scenario in Scenario_set
    Max_charging : float
        Maximum charging limit in MW.
    Max_discharging : float
        maximum discharging limit in MW.
    charging_efficiency : float in [0,1]
        Efficiency of charging.
    discharging_efficiency : float in [0,1]
        Efficiency of discharging.
    Min_StateofCharge : float
        Minimum State of Charge level in MWh.
    Max_StateofCharge : float
        Maximum State of Charge level in MWh.
    Initial_StateofCharge : float
        Initial State of Charge level in MWh.
    Returns
    -------
    gurobi optimization model m

    """
    
    #Create a new model 
    m = gp.Model("battery") 
    
    
    # 1) Variables
    
    ### 1.1) Market variables
    x_tilde = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = "x_tilde") #power sold/produced
    v = m.addVars( Scenario_set, vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = "v") #auxiliary variable for valuation
    
    ### 1.2) Charge/discharge and state-of-charge variables
    g = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Max_charging, name = "g") #power charged
    d = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Max_discharging, name = "d") #power discharged
    e = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = Min_StateofCharge, ub = Max_StateofCharge, name = "e") #state-of-charge
    
    ### 1.3) Auxiliary variables indicating charging and discharging
    delta = m.addVars( Scenario_set, Time_set, vtype = GRB.BINARY, name = "delta") 
    
    # 2) Objective

    ### 2.1) Valuation - degradation costs
    m.addConstrs( v[s] == 0 for s in Scenario_set)

    ### 2.2) Objective function
    m.setObjective( sum(Probabilities[s] * (v[s] - sum(Prices[s][t] * x_tilde[s,t] for t in Time_set)) for s in Scenario_set), GRB.MAXIMIZE)
    
    # 3) Constraints
    
    ### 3.1) Linking x_tilde to charging discharging
    m.addConstrs( x_tilde[s,t] == g[s,t] - d[s,t] for t in Time_set for s in Scenario_set )
    
    ### 3.2) State of Charge constraints
    m.addConstrs( e[s,t] == e[s,t-1] + charging_efficiency * g[s,t] - (d[s,t] / discharging_efficiency)  for t in Time_set[1:] for s in Scenario_set )
    m.addConstrs( e[s,0] == Initial_StateofCharge + charging_efficiency * g[s,0] - (d[s,0] / discharging_efficiency)  for s in Scenario_set )
    m.addConstrs( e[s,Time_set[-1]] == Initial_StateofCharge for s in Scenario_set ) #end with the same state-of-charge as started
    
    ### 3.3) Avoid simultaneous charging&discharging
    m.addConstrs( g[s,t] <= Max_charging * delta[s,t]  for t in Time_set for s in Scenario_set )    
    m.addConstrs( d[s,t] <= Max_discharging * (1-delta[s,t])  for t in Time_set for s in Scenario_set )
   
    return m


##############################################################################################################################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################


def demand_response(Time_set, Scenario_set, Prices, Probabilities,
                Efficiency_Heat_Pump, Efficiency_Gas_Boiler, Loss_coefficient, Heat_Load, Cost_Gas, Load_serving_price,
                Capacity_Storage, Max_charging_storage, Max_discharging_storage, Capacity_Heat_Pump, Capacity_Gas_Boiler, Initial_StateofCharge, Daily_Fixed_cost):
    """
    Optimizaton model of utility serving a heat load. Objective: optimal dispatch for each price scenario in Prices. (separable in scenarios)

    Parameters
    ----------
    Time_set : list of integers 0,1,2,3, ... T
        List of time step indices. 
    Scenario_set : list of integers 0,1,2,3, .... S
        List of scenario indices.
    Prices : list of list
        List of prices (length: Time_set) for each scenario in Scenario_set 
    Probabilities : list of floats
        List of probability for each scenario in Scenario_set
    Efficiency_Heat_Pump : float 
        Efficiency of the heat pump.
    Efficiency_Gas_Boiler : float
        Efficiency of the gas boiler.
    Loss_coefficient : float
        Percentage of the stored heat which gets lost from one period to the other.
    Heat_Load : list of loats
        List of heat loads for each t in Time_set
    Cost_Gas : float
        Cost of gas.
    Load_serving_price : float
        Price paid by the consumers for serving 1MWh of load.
    Capacity_Storage : float
        Total capacity of the heat storage in MWh
    Max_charging_storage : float
        Maximum charging limit of the heat storage in MW.
    Max_discharging_storage : float
        Maximum discharging limit of the heat storage in MW.
    Capacity_Heat_Pump : float
        Capacity of the heat pump, i.e. how much electrcity it can take in. In MW
    Capacity_Gas_Boiler : float
        Capacity of the gas boiler, i.e. how much gas it can take in. 
    Initial_StateofCharge : float
        Initial State of Charge level of the heat storage in MWh.
    Daily_Fixed_cost : float
        Daily operation costs    

    Returns
    -------
    gurobi optimization model m

    """

    
    #Create a new model 
    m = gp.Model("demand response") 
    
    
    # 1) Variables
    
    ### 1.1) Market variables
    x_tilde = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Capacity_Heat_Pump, name = "x_tilde") #power consumed by the heat pump
    v = m.addVars( Scenario_set, vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = "v") #auxiliary variable for valuation
    
    ### 1.2) Charge/discharge and state-of-charge variables of the heat storage
    g = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Max_charging_storage, name = "g") #heat charged
    d = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Max_discharging_storage, name = "d") #heat discharged
    e = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Capacity_Storage, name = "e") #state-of-charge
    
    ### 1.3) Gas consumed
    y = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, ub = Capacity_Gas_Boiler, name = "y") 
    
    ### 1.3) Load curtailed
    z = m.addVars( Scenario_set, Time_set, vtype = GRB.CONTINUOUS, lb = 0, name = "z") 
    for s in Scenario_set:
        for t in Time_set:
            z[s,t].ub = Heat_Load[t]
    
    # 2) Objective
    
    ### 2.1) Valuation = revenue by serving load - cost of gas
    m.addConstrs( v[s] == sum( Load_serving_price * (Heat_Load[t] - z[s,t]) - Cost_Gas * y[s,t] for t in Time_set) - Daily_Fixed_cost for s in Scenario_set)
    
    ### 2.2) Objective function
    m.setObjective( sum(Probabilities[s] * (v[s] - sum(Prices[s][t] * x_tilde[s,t] for t in Time_set)) for s in Scenario_set), GRB.MAXIMIZE)
    
    
    # 3) Constraints
    
    ### 3.1) Load serving constraint
    m.addConstrs( Efficiency_Heat_Pump * x_tilde[s,t] + Efficiency_Gas_Boiler * y[s,t] + d[s,t] - g[s,t] == Heat_Load[t] - z[s,t] for t in Time_set for s in Scenario_set )
    
    ### 3.2) State of Charge constraints
    m.addConstrs( e[s,t] == (1-Loss_coefficient) * e[s,t-1] + g[s,t] - d[s,t]  for t in Time_set[1:] for s in Scenario_set )
    m.addConstrs( e[s,0] == (1-Loss_coefficient) * Initial_StateofCharge + g[s,0] - d[s,0]  for s in Scenario_set )
    m.addConstrs( e[s,Time_set[-1]] == Initial_StateofCharge for s in Scenario_set ) #end with the same state-of-charge as started
    
    return m