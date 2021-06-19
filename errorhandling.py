# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 07:54:51 2021

@author: samuel
"""

import sys
import traceback
import datetime
from inspect import currentframe, getframeinfo, stack

import databaseutil
dbu = databaseutil.databaseConnect()

def catchError(custom_message = ""):
    """
        general method used to catch all excetions and data will be pushed to database collection named "toolLogs".

        NOTE : "custome_message" is used to add more tool related information into error logs.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    traceback_details = {
                             'filename': exc_traceback.tb_frame.f_code.co_filename,
                             'lineno'  : exc_traceback.tb_lineno,
                             'name'    : exc_traceback.tb_frame.f_code.co_name,
                             'error_type'    : exc_type.__name__,
                             'logtype' : "error",
                             'custom_message' : custom_message,
                             'message' : str(exc_value), # or see traceback._some_str()
                             'datetime' : str(datetime.datetime.now())
                            }
    del(exc_type, exc_value, exc_traceback) # So we don't leave our local labels/objects dangling
    #print(traceback_details)
    query = {"collection_name" : "toolLogs", "data":traceback_details}
    dbu.insertData(query)

    
def catchWarning(custom_message=""):
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    traceback_details = {
                             'filename': exc_traceback.tb_frame.f_code.co_filename,
                             'lineno'  : exc_traceback.tb_lineno,
                             'name'    : exc_traceback.tb_frame.f_code.co_name,
                             'error_type'    : "None",
                             'logtype' : "warning",
                             'custom_message' : custom_message,
                             'message' : str(exc_value), # or see traceback._some_str()
                             'datetime' : str(datetime.datetime.now())
                            }
    del(exc_type, exc_value, exc_traceback) # So we don't leave our local labels/objects dangling
    #print(traceback_details)
    query = {"collection_name" : "toolLogs", "data":traceback_details}
    dbu.insertData(query)
    
