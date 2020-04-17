#!/bin/env python
# Created on April 17, 2020
#  by Tao Huang (huan1441)
#
# This script serves as the solution set for assignment-11
# on generating summary figures to present analysis results for a dataset.
#

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')

    # remove the negative streamflow values
    DataDF = DataDF[~(DataDF['Discharge']<0)]
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""

    # clips the given time series dataframe to a given range of dates
    DataDF = DataDF[startDate:endDate]
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""

    # open and read the file
    DataDF = pd.read_csv(fileName, parse_dates=[0])
    DataDF = DataDF.set_index('Date')    
    
    return( DataDF )

def GetMonthlyAverages(MoDataDF):
    """This function calculates annual average monthly values for all 
    statistics and metrics.  The routine returns an array of mean values 
    for each metric in the original dataframe."""

    # group by month and calculate the mean value for each month
    Mo_index=lambda x:x.month
    MonthlyAverages = MoDataDF.groupby(Mo_index).mean()
    MonthlyAverages.index.name = 'Date'    
    
    return( MonthlyAverages )


# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }

    # define a dictionary to store the names of original files
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }

    # define a dictionary to store the names of Annual and Monthly metric CSV files
    metricsName = {"Annual":"Annual_Metrics.csv",
                "Monthly":"Monthly_Metrics.csv" }

    # define a blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    MetricsDF = {}
    MonthlyAverages = {}
    PeakFlow = {}

    # process input datasets

    for file in metricsName.keys():

        MetricsDF[file] = ReadMetrics(metricsName[file])
        
    for file in fileName.keys():
        
        DataDF[file], _ = ReadData(fileName[file])
        MonthlyAverages[file] = GetMonthlyAverages(MetricsDF['Monthly'].loc[MetricsDF['Monthly']['Station']==file])
        PeakFlow[file] = MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']==file]['Peak Flow'].sort_values(ascending=False)
        
        # clip to consistent period
        DataDF[file], _ = ClipData( DataDF[file], '2014-10-01', '2019-09-30' )

    # create the plot of the daily flow for both streams for the last 5 years of the record
    
    DataDF['Wildcat']['Discharge'].plot(figsize=(16,9),style='r')
    DataDF['Tippe']['Discharge'].plot(style='b')
    plt.legend([riverName['Wildcat'],riverName['Tippe']], loc='best',edgecolor='k',fontsize=20)
    plt.title("Daily Flow (2015-2019)",fontsize=20)
    plt.xlabel("Date",fontsize=20)
    plt.ylabel("Discharge (cfs)",fontsize=20)
    # save the plot as PNG with a resolution of 96 dpi
    plt.savefig("Daily Flow (2015-2019).png",dpi=96)
    plt.close()

    # create the plot of annual coefficient of variation for both streams
    
    MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']=="Wildcat"]['Coeff Var'].plot(figsize=(16,9),style='ro')
    MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']=="Tippe"]['Coeff Var'].plot(style='b^')
    plt.legend([riverName['Wildcat'],riverName['Tippe']], loc='best',edgecolor='k',fontsize=20)
    plt.title("Annual Coefficient of Variation (1970-2019)",fontsize=20)
    plt.xlabel("Date (year)",fontsize=20)
    plt.ylabel("Coefficient of Variation",fontsize=20)
    # save the plot as PNG with a resolution of 96 dpi
    plt.savefig("Annual Coefficient of Variation (1970-2019).png",dpi=96)
    plt.close()

    # create the plot of annual Tqmean for both streams
    
    MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']=="Wildcat"]['Tqmean'].plot(figsize=(16,9),style='ro')
    MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']=="Tippe"]['Tqmean'].plot(style='b^')
    plt.legend([riverName['Wildcat'],riverName['Tippe']], loc='best',edgecolor='k',fontsize=20)
    plt.title("Annual Tqmean (1970-2019)",fontsize=20)
    plt.xlabel("Date (year)",fontsize=20)
    plt.ylabel("Tqmean",fontsize=20)
    # save the plot as PNG with a resolution of 96 dpi
    plt.savefig("Annual Tqmean (1970-2019).png",dpi=96)
    plt.close()

    # create the plot of R-B index for both streams
    
    MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']=="Wildcat"]['R-B Index'].plot(figsize=(16,9),style='ro')
    MetricsDF['Annual'].loc[MetricsDF['Annual']['Station']=="Tippe"]['R-B Index'].plot(style='b^')
    plt.legend([riverName['Wildcat'],riverName['Tippe']], loc='best',edgecolor='k',fontsize=20)
    plt.title("Annual R-B Index (1970-2019)",fontsize=20)
    plt.xlabel("Date (year)",fontsize=20)
    plt.ylabel("R-B Index",fontsize=20)
    # save the plot as PNG with a resolution of 96 dpi
    plt.savefig("Annual R-B Index (1970-2019).png",dpi=96)
    plt.close()
    
    # create the plot of average annual monthly flow for both streams
    
    MonthlyAverages['Wildcat']['Mean Flow'].plot(figsize=(16,9),style='ro')
    MonthlyAverages['Tippe']['Mean Flow'].plot(style='b^')
    plt.xticks(np.arange(1,13,1))
    plt.legend([riverName['Wildcat'],riverName['Tippe']], loc='best',edgecolor='k',fontsize=20)
    plt.title("Average Annual Monthly Flow (1970-2019)",fontsize=20)
    plt.xlabel("Date (month)",fontsize=20)
    plt.ylabel("Discharge (cfs)",fontsize=20)
    # save the plot as PNG with a resolution of 96 dpi
    plt.savefig("Average Annual Monthly Flow (1970-2019).png",dpi=96)
    plt.close()

    # create a list to store the exceedence probability and set is as the index of 'PeakFlow' dataframe

    for file in fileName.keys():

        E_P =[]
        N = len(PeakFlow[file])
        for i in range(1,N+1):
            E_P.append(i/(N+1))
        
        PeakFlow[file].index = pd.Series(E_P)
        PeakFlow[file].index.name = 'Exceedence Probability'

    # create the plot of return period of annual peak flow events for both streams
    
    PeakFlow['Wildcat'].plot(figsize=(16,9),style='ro')
    PeakFlow['Tippe'].plot(style='b^')
    
    # set the range of x-axis ('Exceedence Probability') from 1 to 0
    plt.gca().set_xlim(1,0)
    
    plt.legend([riverName['Wildcat'],riverName['Tippe']], loc='best',edgecolor='k',fontsize=20)
    plt.title("Return Period of Annual Peak Flow Events",fontsize=20)
    plt.xlabel("Exceedence Probability",fontsize=20)
    plt.ylabel("Discharge (cfs)",fontsize=20)
    # save the plot as PNG with a resolution of 96 dpi
    plt.savefig("Return Period of Annual Peak Flow Events.png",dpi=96)
    plt.close()
