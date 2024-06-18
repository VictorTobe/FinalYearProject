"""
Utility Script for crim_act_hotspots_2019

Usage:
The functions defined in this script work as helper functions in the main
source code notebook (../notebooks/src_code_nb.ipynb)

Original Author: Ramshankar Yadhunath
                  Twitter: @thedatacrack
"""

import pandas as pd

def create_df(filenames):
    """
    Returns a dataframe after aggregating all necessary .csv files together
    
    PARAMETERS:
        filenames : List of .csv files to be aggregated
    """
    # List to store all dataframes
    df_list = []

    for file in filenames:
        print(f"Loading Chicago Crime Dataset file for the year {file[-8:-4]}.")
        df_temp = pd.read_csv(file)
        df_temp = df_temp.iloc[:, :22]  # Ensure to take the first 22 columns
        df_list.append(df_temp)
        print(f"Finished loading Chicago Crime Dataset file for the year {file[-8:-4]}.")

    # Concatenate all dataframes in the list
    main_df = pd.concat(df_list, ignore_index=True)
    print("All data files loaded onto the Main Dataframe.\n\n")
    
    return main_df
