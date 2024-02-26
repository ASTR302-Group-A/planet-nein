#!/usr/bin/env python3

import numpy as np
import pandas as pd
from pandas import DataFrame as df

def change_orbit_format(filename):
    """
    
    This function will change the format of the orbital file to one that is is needed for Sorcha to run properly.
    In order to do so, I need to only keep the following columns: a, e, inc, Omega, varpi, M.
    Omega must be renamed to 'node', varpi to 'argPeri', and M to 'ma'. There are also spaces included before every
    column name, so the spaces must be deleted through the renaming process.
    The rest of the columns must be dropped from the table, since sorcha won't recognize them.
    
    Sorcha also needs information about the simulated object's ID,  format type, and epoch MJD. 
    
    Parameters:
        df_orbit = Converted the inputted csv file into a dataframe
        objID = Array of object ID names that will be added to the orbital table
        mjd = Converting from julian date to modern julian date by subtracting JD by 2400000.5 days
    
    Column names:
        objID = Names of all of the simulated objects (string)
        FORMAT = Orbit format string (Keplerian ('KEP') in this case)
        a = Semimajor axis (AU)
        e = Eccentricity
        inc = Inclination (degrees)
        node = Longitude of the ascending node (degrees)
        argPeri = Argument of perihelion (degrees)
        ma = Mean anomaly (degrees)
        epochMJD_TBD = Epoch (MJD) (JD=2458270.0 in this case)
    
    In order to determine the object's ID, we must add one whole integer to the object name every time we loop
    through a row. For Keplerian formats, we need to use the object ID of t(some integer). For example if we go
    through index 1, then the object ID will be 't1'. Each of the object IDs will be stored in an array that will
    be inserted at the beginning of the table. 
    
    Since the MJD and format type doesn't change, we don't need to create a loop. Instead, we can just insert the
    FORMAT column as the second column with the only value of 'KEP'. The MJD column can be added to the end of the
    table with the only MJD value of June 1, 2018, since that is the day when the simulation was completed.
    
    """
    
    df_orbit = pd.read_csv(filename,
                 skiprows = [0,1,2,3], #Skips the rows with the comments about the specific columns
                 index_col = ["index"])
    
    df_orbit = df_orbit.rename(columns = {' Omega':'node',' varpi':'argPeri',' M':'ma',
                                          ' a':'a', ' e':'e', ' inc':'inc'}) #Renames columns to sorcha names
    
    df_orbit = df_orbit.drop(columns = [' mass',' ra', ' dec', ' R', ' rad', ' albedo', ' V',
                  ' ZTF', ' DES', ' PS1']) #Drops unneeded columns
    
    #Creating simulated object names
    objID = []
    mjd = 2458270.0 - 2400000.5

    for i in range(len(df_orbit)):
        objID.append('t' + str(i)) #Creates name of object and adds to array that will be included in table
        
        
    df_orbit.insert(0,"objID", objID) #Inserts object ID into first column of table
    df_orbit.insert(1, "FORMAT", 'KEP') #Inserts the keplerian format into second column of table
    df_orbit["epochMJD_TBD"] = mjd #Adds the same MJD for all objects to end of table
    
    return df_orbit