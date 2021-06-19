# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 06:59:21 2021

@author: samuel
"""

import json
import os
import shutil
import uuid
import datetime
from zipfile import ZipFile
#import py7zr

## custome files
import errorhandling
import modelexplainable
import databaseutil
dbu = databaseutil.databaseConnect()
    
with open("config.json", "r") as file:
    configData = json.load(file)

if configData["modelssavedpath"] not in os.listdir():
    os.mkdir(configData["modelssavedpath"])


"""
    this class is used for all model uploading and deletion operation
"""
class modelManagement():
    
    def __init__(self):
        pass
    
    def uploadModel(self, modeldata):
        """
            method will save the all uploaded files to specific unique folder created, and that folder name will be "mmid".
        """
        try:
            requestID = str(uuid.uuid1())
            model = modeldata["model"]
            
            if requestID not in os.listdir(configData["modelssavedpath"]):
                savepath = os.path.join(configData["modelssavedpath"], requestID)
                os.mkdir(savepath)
                
                if modeldata["attachment_filename"].split("/")[-1].split(".")[-1] == "zip":
                    with ZipFile(model, 'r') as zip:
                        zip.extractall(savepath)
                        
                    source_folder = os.path.join(savepath, modeldata["attachment_filename"].split(".")[0])
                    destination_folder = savepath
                    for file in os.listdir(source_folder):
                        shutil.move(os.path.join(source_folder, file), destination_folder)
                    
                    shutil.rmtree(source_folder)
                    with open(os.path.join(destination_folder, "modelconfig.json"), "r") as fp:
                        modelconfig = json.load(fp)
                        modelconfig["model_savepath"] = destination_folder
                        
                    upload_model_info = {"mmid" : requestID, 
                                         "modelname" : modelconfig["modelname"],
                                         "modeltype" : modelconfig["modeltype"],
                                         "upload_datetime" : str(datetime.datetime.today())
                                         }
                    
                    ## created explainable environment for uploading model
                    mex = modelexplainable.explainable()
                    ex_flag = mex.createExplainableEnv(modelconfig)
                    if ex_flag == 0:
                        upload_model_info["explainable_environment"] = True
                    else:
                        upload_model_info["explainable_environment"] = False
                        
                    query = {"collection_name" : "uploadedmodels", "data":upload_model_info}
                    dbu.insertData(query)
                    
                    return {"message" : "model uploaded successfully. mmid : {}".format(requestID)}
                else:
                    ecp_msg = {"logtype":"warning", "message" : configData["errorID"]["300"], "datetime":datetime.datetime.now()}
                    query = {"collection_name" : "toolLogs", "data":ecp_msg}
                    dbu.insertData(query)
                    return ecp_msg
                
                """
                elif modeldata["attachment_filename"].split("/")[-1].split(".")[-1] == "7z":
                    with py7zr.SevenZipFile(model, mode='r') as z:
                        z.extractall(path=savepath)
                    return {"message" : "model uploaded successfully. MMID : {}".format(requestID)}
                """
                
            else:
                try:
                    raise Exception
                except:
                    errorhandling.catchWarning(custom_message=configData["errorID"]["301"])
                return configData["errorID"]["301"]
            
        except Exception as err_msg:
            shutil.rmtree(savepath)
            errorhandling.catchError(custom_message=configData["errorID"]["-1"])
            return err_msg
        
        

    def deleteModel(self, requestdata):
        """
            this method will delete the model, when "mmid" is given
        """    
        try:
            delete_query = {"collection_name" : "uploadedmodels", "delete_query":{"mmid" : requestdata["mmid"]}}
            dbu.deleteRecords(delete_query)
            model_saved_path = os.path.join(configData["modelssavedpath"], requestdata["mmid"])
            shutil.rmtree(model_saved_path)
            
            try:
                raise Exception
            except:
                errorhandling.catchWarning(custom_message="deleted model : {} from monitoring tools".format(requestdata["mmid"]))
            log = {"logtype" : "critical", "message" : "deleted model : {} from monitoring tools".format(requestdata["mmid"]), "datetime":datetime.datetime.now()}
            return {"message" : log["message"]}
        
        except Exception as err_msg:
            errorhandling.catchError(custom_message=configData["errorID"]["-1"])
            return {"error" : str(err_msg)}
        
            
            
            
        
        
        