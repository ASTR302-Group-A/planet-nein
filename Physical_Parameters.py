import pandas as pd
import numpy as np
from pandas import DataFrame as df

# Reading in .csv
phys_para = pd.read_csv('reference_population.csv',
                      skiprows = [0,1,2,3], # Skipping extraneous rows
                      index_col = 'index')

# Copy phys_para to manipulate
para_copy = phys_para[[" V"]].copy()
para_copy = para_copy.rename(columns={' V': 'H_r'})   # Changed variable apparent mag to absolute mag
                                                    # Placeholder until Oorb is working
    
# Changing V mag to H mag column
para_copy["H_r"] -= 20 # Temporary change to change H mag to be detectable
##df["H"] = compute_H_mag(df)
##del df[" V"]

# Adding ObjID column
para_copy["ObjID"] = 't' + para_copy.index.astype(str) # Must change index to a string to add 't'
para_copy = para_copy[["ObjID", "H_r"]]

# Set value for colors
para_copy["u-r"] = 1.72 
para_copy["g-r"] = 0.48 
para_copy["i-r"] = -0.11 
para_copy["z-r"] = -0.12
para_copy["y-r"] = -0.12
para_copy["GS"] = 0.15
# Actual color values will be provided at later date

# Creates .txt file
para_copy.to_csv('phys_param.txt', index=False, sep=' ', float_format='%.2f')