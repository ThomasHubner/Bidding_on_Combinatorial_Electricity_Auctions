"""
Generating three files by using the point forecast function:
    - Downloads train data and saves in file "DE.csv"
    - Writes point forecasts for "begin_test_date" to "end_test_date" in a csv-file named "Forecast_DE.csv"
    - Extracts real price data from "DE.csv" for "begin_test_date" to "end_test_date" in a csv-file named "Real_DE.csv"
"""

#Import
import pandas as pd
import numpy as np
import os

from epftoolbox.data import read_data
from epftoolbox.evaluation import MAE, sMAPE
from epftoolbox.models import LEAR

#External forecast parameters
dataset = "DE"
begin_test_date = "01/01/2015"
end_test_date = "31/12/2017"
calibration_window = 4*364
years_test = 3

def point_forecast(dataset, years_test, calibration_window, begin_test_date, end_test_date):
    """
    Using LEAR model from EPFLtoolbox for point forecasting prices with daily recalibration.

    Parameters
    ----------
    dataset : type=str, default='PJM'
        Market under study. If it not one of the standard ones, the file name' + 'has to be provided, where the file has to be a csv file.
    years_test:  type=int, default=2, 
        Number of years (a year is 364 days) in the test dataset. Used if ' + ' begin_test_date and end_test_date are not provided.
    calibration_window : type=int, default=4 * 364,
        Number of days used in the training dataset for recalibration.
    begin_test_date : type=str, default=None, 
        Optional parameter to select the test dataset. Used in combination with ' +'end_test_date. If either of them is not provided, test dataset is built ' + 'using the years_test parameter. 
        It should either be  a string with the ' + ' following format d/m/Y H:M').
    end_test_date : type=str, default=None,
        Optional parameter to select the test dataset. Used in combination with ' +'begin_test_date. If either of them is not provided, test dataset is built ' + 'using the years_test parameter. 
        It should either be  a string with the ' + ' following format d/m/Y H:M')..

    Returns
    -------
    None. 
    - Downloads train data and saves in file "DE.csv"
    - Writes point forecasts for "begin_test_date" to "end_test_date" in a csv-file named "Forecast_DE.csv"
    - Extracts real price data from "DE.csv" for "begin_test_date" to "end_test_date" in a csv-file named "Real_DE.csv"

    """
    
    ##########################################################################################
    # ------- Defining Test and Train data and training the model---------------------#
    ##########################################################################################
    
    
    #Creating paths to store test&train data and generated forecasts
    path_datasets_folder = os.path.join('.', '')
    #path_recalibration_folder = os.path.join('.', 'Forecasts')
        
        
    # Defining train and testing data
    df_train, df_test = read_data(dataset=dataset, years_test=years_test, path=path_datasets_folder,
                                  begin_test_date=begin_test_date, end_test_date=end_test_date)
    
    # Defining unique name to save the forecast
    forecast_file_name = 'Forecast' + '_' + str(dataset) + '.csv'
    
    #forecast_file_path = os.path.join(path_recalibration_folder, forecast_file_name)
    
    
    # Defining empty forecast array and the real values to be predicted in a more friendly format
    forecast = pd.DataFrame(index=df_test.index[::24], columns=['h' + str(k) for k in range(24)])
    real_values = df_test.loc[:, ['Price']].values.reshape(-1, 24)
    real_values = pd.DataFrame(real_values, index=forecast.index, columns=forecast.columns)
    
    forecast_dates = forecast.index
    
    
    #Training the model on the calibration window / training data
    model = LEAR(calibration_window=calibration_window)
    
    
    ##########################################################################################
    # ------- Generating point forecasts by iterating over the testing days -----------------#
    ##########################################################################################
    
    
    # For loop over the recalibration dates
    for date in forecast_dates:
    
        # For simulation purposes, we assume that the available data is
        # the data up to current date where the prices of current date are not known
        data_available = pd.concat([df_train, df_test.loc[:date + pd.Timedelta(hours=23), :]], axis=0)
    
        # We set the real prices for current date to NaN in the dataframe of available data
        data_available.loc[date:date + pd.Timedelta(hours=23), 'Price'] = np.NaN
    
        # Recalibrating the model with the most up-to-date available data and making a prediction
        # for the next day
        Yp = model.recalibrate_and_forecast_next_day(df=data_available, next_day_date=date, 
                                                     calibration_window=calibration_window)
        # Saving the current prediction
        forecast.loc[date, :] = Yp
    
        # Computing metrics up-to-current-date
        mae = np.mean(MAE(forecast.loc[:date].values.squeeze(), real_values.loc[:date].values)) 
        smape = np.mean(sMAPE(forecast.loc[:date].values.squeeze(), real_values.loc[:date].values)) * 100
    
        # Printing information
        print('{} - sMAPE: {:.2f}%  |  MAE: {:.3f}'.format(str(date)[:10], smape, mae))
    
        # Saving forecast
        forecast.to_csv(forecast_file_name)
        
        
    ##########################################################################################
    # ---------------- Reformatting csv file with real prices  ------------------------------#
    ##########################################################################################
    
    #Get real prices
    real_price_data = pd.read_csv( dataset+'.csv')
    
    #Row number of begin test date in real_price_data
    date = begin_test_date[6:] + "-" + begin_test_date[3:5] + "-" + begin_test_date[0:2] + " 00:00:00" #converting format
    row_num = real_price_data[ real_price_data.iloc[:,0] == date ].index[0] 
    
    #Formulate new csv in different format
    new_csv = pd.DataFrame(index=df_test.index[::24], columns=['h' + str(k) for k in range(24)])
    
    #Iterating over all days
    for i in range(len(new_csv.index)) :
        
        #Extracting prices from real_price_data and writing to new_csv
        for f in range(24):
            new_csv.iloc[i,f] = real_price_data.iloc[f + i*24 + row_num,1]
            
    #Saving csv
    new_csv.to_csv("Real"+ '_' + str(dataset) + '.csv')  
    
    return

#Run point forecast
point_forecast(dataset, years_test, calibration_window, begin_test_date, end_test_date)