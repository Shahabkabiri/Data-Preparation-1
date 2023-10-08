import os
import pandas as pd
import pickle
import MetaTrader5 as mt5
from datetime import timedelta, datetime
import pytz

# Specify your folder paths and filenames
folder_path =
output_file = 'history_data.xlsx'
output_path = os.path.join(folder_path, output_file)
symbol = "NQ100_m"

# Initialize MetaTrader5 (mt5)
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Read the detected levels data from a CSV file
AllLevels = pd.read_csv('NQ DetectedLevels.txt', sep=',') 

def LevelFilter(AllLevels, MinimumVolume, MaximumVolume, MetaFilterDate, RemoveEntranceVolumes,
                 RemoveMovingOutVolumes):
    # Filter by Volume
    AllLevels = AllLevels[(AllLevels['Total Volume'] > MinimumVolume) & (AllLevels['Total Volume'] < MaximumVolume)]

    # Filter by Date
    AllLevels['Start Time'] = pd.to_datetime(AllLevels['Start Time'], format="%Y-%m-%d %H:%M:%S.%f")
    AllLevels = AllLevels[(AllLevels['Start Time'] > MetaFilterDate)]

    # Sorting based on Time
    AllLevels['Start Time'] = AllLevels['Start Time'] + timedelta(hours=3)
    AllLevels['End Time'] = AllLevels['End Time'] + timedelta(hours=3)
    AllLevels.sort_values(by=['Start Time'], inplace=True, ascending=False)

    # Remove unwanted Times based on conditions
    if RemoveEntranceVolumes:
        AllLevels = AllLevels.between_time('16:50:00', '16:25:00')
    if RemoveMovingOutVolumes:
        AllLevels = AllLevels.between_time('23:00:00', '22:25:00')

    AllLevels.reset_index(drop=True, inplace=True)
    return AllLevels

# Filter the levels data
FilteredLevels = LevelFilter(AllLevels=AllLevels,
                             MinimumVolume=100,
                             MaximumVolume=102,
                             MetaFilterDate=datetime(2022, 3, 20, 0, 0, 0),
                             RemoveEntranceVolumes=False,
                             RemoveMovingOutVolumes=False)

# Desired number of levels to include for feature engineering
DesiredNumberOfLevelsToInclude = 5
AvailableDataSize = FilteredLevels.shape[0] - DesiredNumberOfLevelsToInclude + 1

# Columns to include for feature engineering
ColumnsToInclude = ['Max Price in Movement', 'Min Price in Movement', 'Total Volume', 'Direction']
Times = FilteredLevels.loc[:, 'Start Time']
FilteredLevels = FilteredLevels[ColumnsToInclude]

# Create a DataFrame for feature engineering
DataForNN = pd.DataFrame()
for i in range(AvailableDataSize):
    DataForNN.loc[i, 'Start Time'] = Times[i]
    BaseTime = Times[i]
    for j in range(DesiredNumberOfLevelsToInclude):
        TimeDistNumber = 'TimeDifference' + str(j)
        DataForNN.loc[i, TimeDistNumber] = (BaseTime - Times[i+j]).total_seconds() / 60
        for k in range(FilteredLevels.shape[1]):
            VarNumber = FilteredLevels.columns[k] + str(j)
            DataForNN.loc[i, VarNumber] = FilteredLevels.iloc[i+j, k]

# Adding Previous prices
PrevCandlesToInclude = 20
PrevCandleTimeFrameToUse = 10
for i in range(DataForNN.shape[0]):
    rates = pd.DataFrame(mt5.copy_rates_from(symbol,
                                             mt5.TIMEFRAME_M10,
                                             DataForNN.loc[i, 'Start Time'],
                                             PrevCandlesToInclude))
    rates = rates.reindex(index=rates.index[::-1])
    rates.reset_index(drop=True, inplace=True)
    rates['time'] = pd.to_datetime(rates['time'], unit='s')
    for j in range(1, PrevCandlesToInclude):
        VarNameHigh = 'PreviousHigh_' + str(j)
        VarNameLow = 'PreviousLow_' + str(j)
        DataForNN.loc[i, VarNameHigh] = rates.loc[j, 'high']
        DataForNN.loc[i, VarNameLow] = rates.loc[j, 'low']

# Adding Future prices
FutureCandlesToInclude = 20
FutureCandleTimeFrameToUse = 10
for i in range(DataForNN.shape[0]):
    rates = pd.DataFrame(mt5.copy_rates_from(symbol,
                                             mt5.TIMEFRAME_M10,
                                             DataForNN.loc[i, 'Start Time'] + timedelta(minutes=FutureCandlesToInclude * FutureCandleTimeFrameToUse),
                                             FutureCandlesToInclude))
    rates['time'] = pd.to_datetime(rates['time'], unit='s')
    for j in range(FutureCandlesToInclude):
        VarNameHigh = 'FutureHigh_' + str(j + 1)
        VarNameLow = 'FutureLow_' + str(j + 1)
        DataForNN.loc[i, VarNameHigh] = rates.loc[j, 'high']
        DataForNN.loc[i, VarNameLow] = rates.loc[j, 'low']
