# Bidding on Combinatorial Electricity Auctions
Decision-support algorithms for bid determination on combinatorial electricity markets.

This repository is an accompaniment to the paper titled *Bidding on Combinatorial Electricity Auctions* by Thomas Hübner and Gabriela Hug.
It contains the code used to conduct computational experiments. 
Details and results can be found in the above-mentioned paper.

The code can be found in the folder *Bidding_on_Combinatorial_Electricity_Auctions*. The files
  - Auxiliary_Functions.py
  - Case_Study_Models.py
  - Optimization_Models.py
    
contain the optimization models and case studies presented in the paper as well as auxiliary functions necessary to run the experiments.

The files

 - main_Analysis_Bid_Number.py
 - main_Analysis_Scenario_Number.py
 - main_Analysis_Self_Schedule.py
 - main_Analysis_Forecast.py
   
can be executed to run the respective experiments. The results are written into the folders

- Results_Analysis_Forecast
- Results_Sensitivity_Analysis
  
which contains the following functions to generate the plots presented in the paper:

- Plot_Analysis_Forecast.py
- Plot_Sensitivity_Analysis.py
  
The code to generate the illustrative figures presented in the article can be found in the folder

- Figures
  - Plot_Block_Bids.py
  - Plot_Data.py
  - Plot_Theorem1.py
    
The csv files

- Real_DE.csv
- Forecast_DE.csv
  
contain the real and forecasted electricity prices used in the experiments. Those files were generated using

- Point_Forecast
    - Point_Forecast.py
