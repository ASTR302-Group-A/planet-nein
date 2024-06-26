# imports
import pandas as pd
import numpy as np
import sqlite3
from astropy.time import Time

def single_planet_detect(obs_df, my_objID,
                    min_detections=5, max_timewindow=14):
    '''Determines if planet would be detected based on Rubin algorithm
    
    Rubin will detect a moving object in these not-quite-near-Earth-orbits
    if there are FIVE detections within TWO WEEKS.
    
    WARNING: this will sort the observation dataframe by dates IN PLACE
    
    PARAMETERS:
    obs_df : pandas dataframe 
        the output of a Sorcha run, in a pandas database. Must include
        columns: ObjID, FieldMJD_TAI
    obsID : int or string, must match values in obs_df['ObjId']
        the ID of the object that we're asking about
    min_detections : int, Default=5
        the minimum number of observations that will trigger a detection,
        default is 5
    max_timewindow : int or float, units in days, Default=14
        the maximum number of days that can elapse between observation i
        and observation i+min_detections-1
    
    RETURNS:
    detections : pandas dataframe
        a subset of the given obs_df dataframe with just the observations
        that would trigger a detection
    '''
    # sort by obs date, shoudl be superfluous but just in case
    obs_df.sort_values(by=['FieldMJD_TAI'], inplace=True);
    
    
    # look at only observations of this object
    my_obs = obs_df.loc[obs_df['ObjID']==my_objID];
    my_dates=my_obs['FieldMJD_TAI'];
    
    
    # for the ENTIRE DATE COLUMN:
    # subtract the date of the observation 4 rows before it (this will give 
    # us the time elapsed between observation i and observation i-4)
    elapsed_time = my_dates.diff(periods= min_detections-1);
    
    # return all observations that trigger detections
    detections = my_obs.loc[elapsed_time<max_timewindow];
    return detections;



def planet_detections(sorcha_output_filename):
    '''
    One-stop shop to get the initial detections of all objects from
    our Sorcha output file. Returns a dataframe of all unique object IDs
    and their initial detection dates (in MJD_TAI).
    
    PARAMETERS:
    sorcha_output_filename: string
        full filename (including path if necessary) of the output from 
        Sorcha.
    
    RETURNS:
    unique_objects: Pandas dataframe
        a dataframe with two fields- 'ObjID' and 'detectedMJD_TAI', with 
        one row for each unique object ID from the Sorcha output file.
        Dataframe has been sorted by ascending detection date, with 99999.9
        as a null-value.
    
    '''
    # load observation data
    obs_df = pd.read_csv(sorcha_output_filename);
    
    # for each unique object ID, find detection date
    unique_objects = pd.DataFrame(obs_df['ObjID'].unique(), columns=['ObjID']);
    unique_objects['detectedMJD_TAI'] = 99999.9; # null value date

    for objID in unique_objects['ObjID']:
        # find detection dates
        detections = single_planet_detect(obs_df, my_objID=objID);
        # isolate dates as numpy array
        detection_dates = detections['FieldMJD_TAI'].to_numpy();
        # update the detection date for all rows with this ID
        if len(detection_dates)>0:
            unique_objects.loc[
                unique_objects['ObjID']==objID, 
                'detectedMJD_TAI'] = detection_dates[0];
            
    unique_objects.sort_values(by=['detectedMJD_TAI'], inplace=True);
    
    # return dataframe of each unique object and it's detection date     
    return unique_objects;


def orbits_detectable_by(detections, dateMJD):
    '''
    Takes the detections file from planet_detections and a date, returns the
    subset of unique orbits that would have been detected by that date
    
    PARAMETERS:
    detections : pandas database
        Assumed to be the output of planet_detections(). Must have columns
        ObjID and date_detectedMJD_TAI, with one entry for each unique object
    dateMJD : float
        the date (in MJD, TAI) to limit further detections at
        
    RETURNS:
    detectable_IDs : list
        list of orbit IDs that would be detected by the morning of the given
        date. Format is in MJD_TAI
    candidate_IDs : list
        list of orbit IDs that are still potential candidates
    '''
    detectable_IDs = detections.loc[
                        detections['detectedMJD_TAI']<=dateMJD,
                        'ObjID'];
    candidate_IDs = detections.loc[
                        detections['detectedMJD_TAI']>dateMJD,
                        'ObjID'];
    return [detectable_IDs.to_list(), candidate_IDs.to_list()];



def get_obsdates(pointing_db_file):
    '''
    Returns a list of strings representing each unique date with planned
    observations, based on the pointing database
    
    PARAMETERS:
    pointing_db_file : string
        file location of the pointing database
    
    RETURNS:
    obs_dates : list
        list of all unique dates that have a planned observation,
        sorted from earliest to latest, each represented as a string
        in format 'YYYY-MM-DD'
    '''
    # read in all observation start dates
    con = sqlite3.connect(pointing_db_file);
    result = pd.read_sql("""
        SELECT
            DISTINCT(observationStartMJD)
        FROM
            observations
        """, con)
    con.close();
    
    # get just the unique dates (all time components set to midnight)
    full_dates = list(set(np.floor(result['observationStartMJD'])));
    
    # convert from mjd format to iso format for human readability
    full_dates = Time(full_dates, format='mjd')
    full_dates.format = 'iso';
    
    # pull just the date from the datetime string
    obs_dates = [iso_date[0:10] for iso_date in full_dates.value];
    
    return obs_dates;



def test(troubleshoot_mode=False):
    '''
    Test suite for validating that the planet_detected is running 
    properly. Requires access to the file "test_planet_detection_data.csv"
    
    PARAMETERS:
    troubleshoot_mode: boolean, default False
        optional argument that prints out a more detailed summary of
        the tests for troubleshooting.
    '''
    
    # load test suite data
    print('Running tests on planet detection . . . ', end="");
    test_detection_filename = "test_suites/test_detections.csv";
    obs_df = pd.read_csv(test_detection_filename);
    obs_df['detected']=False; # for tracking overall detections
    obs_df['triggered']=False; # for tracking the initial detections

    # TEST individual planet detection
    for objID in obs_df['ObjID'].unique():
        detections = planet_detected(obs_df, my_objID=objID);
        obs_df.loc[detections.index, ['detected']]=True;
        if troubleshoot_mode:
            print(f'OBJECT:\t{objID}');
            display(obs_df.loc[detections.index]);
    # evaluate results
    errors=obs_df.loc[obs_df['should_detect']!=obs_df['detected']];
    if len(errors)==0: 
        print('PASS')
    else: 
        print('FAIL: see failed rows below'); 
        display(errors)

    # TEST multi-planet detection
    print('Running test on multi-planet detection . . . ', end="");
    multidetect= planet_detections_multi(test_detection_filename);
    for i, row in multidetect.iterrows(): # this is slow, but the test suite is small
        objID= row['ObjID'];
        date= row['detectedMJD_TAI'];
        obs_df.loc[(obs_df['ObjID']==objID) & 
                   (obs_df['FieldMJD_TAI']==date), 
                   'triggered']=True;
    # evaluate results
    errors=obs_df.loc[obs_df['should_trigger']!=obs_df['triggered']];
    if len(errors)==0: 
        print('PASS')
    else: 
        print('FAIL: see failed rows below'); 
        display(errors)
    
    return;

