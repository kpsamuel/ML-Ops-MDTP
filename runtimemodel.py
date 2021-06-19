# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 14:47:38 2021

@author: samuel
"""
import time
import os
import json
import uuid
import datetime
import subprocess

## importing custome packages
import errorhandling
import modelexplainable
import databaseutil
dbu = databaseutil.databaseConnect()
        
with open("config.json", "r") as fp:
    configData = json.load(fp)
    
    
"""
    this class is used to load models and run the model's pipeline operation.
    when prediction request comes, this class loads model in memory based on "mmid" given and executes all steps in modelpiple.
    after prediction response is sent back to api and same predictions explainable, input data and predicted data in saved to db-collection "predictions".
"""
class runVirtualModel():
    
    def __init__(self, inputdata):
        self.inputdata = inputdata
        
        mmid_validation_flag = self.validateModelID()
        x_features_flag = self.prepareModel()
            
        if (mmid_validation_flag == True) & (x_features_flag == True):
            prediction_status = self.predict()
            
            if prediction_status == True:
                self.getpredictionExplaintion()
        
        
    def validateModelID(self):
        """
            validating the "mmid" sent in prediction payload for validation in monitoring system
        """
        mmid_validation_flag = False
        try:
            query = {"collection_name" : "uploadedmodels", "select_query":{"mmid":self.inputdata["mmid"]}}
            data, data_validation_flag = dbu.getData(query)
            if data_validation_flag == 0:
                self.mmid = self.inputdata["mmid"]
                self.model_metadata = data[0]
                self.model_saved_path = os.path.join(configData["modelssavedpath"], self.inputdata["mmid"])
                with open(os.path.join(self.model_saved_path, "modelconfig.json"), "r") as fp:
                    self.modelconfig = json.load(fp)
                mmid_validation_flag = True
            else:
                print("[ * ] invalid mmid or model is removed from monitoring system")
                mmid_validation_flag = False
        except:
             errorhandling.catchError(custom_message=configData["errorID"]["305"])
             mmid_validation_flag = False
             
        return mmid_validation_flag
             
             
    def prepareModel(self):
        loaded_x_features = False
        try:
            with open(os.path.join(self.model_saved_path, self.modelconfig["input_file_to_refer"]), "w") as fp:
                json.dump(self.inputdata["x_features"], fp)
            loaded_x_features = True
        except:
            errorhandling.catchError(custom_message=configData["errorID"]["309"])
            
        return loaded_x_features
        
    def predict(self):
        """
            executing the modelpiple.py file
        """
        prediction_status = False
        try:
            self.prediction_datetime = str(datetime.datetime.now())
            self.prediction_result = -99999999999999
            self.err_msg = "None"
            self.predictionID = str(uuid.uuid1())
            script_working_dir = os.getcwd()
            os.chdir(self.model_saved_path)
            
            exection_cmd = "python {}".format("modelpipeline.py")
            p = subprocess.Popen(exection_cmd, stdout=subprocess.PIPE, shell=True)
            out, err = p.communicate() 
            time.sleep(1)
            with open(self.modelconfig["predicted_file_to_refer"], "r") as fp:
                self.prediction_result = json.load(fp)
                
            with open(self.modelconfig["input_file_to_refer"], "r") as fp:
                self.x_features = json.load(fp)
                
            os.chdir(script_working_dir)
            prediction_status = True
        except Exception as err_msg:
            ecp_msg = {"logtype":"error", "message" : configData["errorID"]["306"] +" : "+str(err_msg), "datetime":datetime.datetime.now()}
            self.err_msg = ecp_msg
            errorhandling.catchError(custom_message=configData["errorID"]["306"])
            os.chdir(script_working_dir)
        
        return prediction_status            
            
    def getpredictionExplaintion(self):
        """
            calling the model explainable and saving the input, output and explainable data into db-collection "predictions".
        """
        try:
            prediction_metadata = {"model_save_path" : self.model_saved_path,
                                   "x_features" : self.x_features,
                                   "predictionID" : self.predictionID,
                                   "prediction_datetime" : self.prediction_datetime}
            if self.model_metadata["explainable_environment"] == True:
                mdex = modelexplainable.explainable()
                mdex.explainPrediction(prediction_metadata)
                
                expected_value = mdex.expected_value
                shap_feature_values = mdex.shap_feature_values
                encoded_shap_plot = mdex.encoded_shap_plot
            else:
                expected_value = None
                shap_feature_values = None
                encoded_shap_plot = None
                
            prediction_metadata["mmid"] = self.mmid
            prediction_metadata["expected_value"] = expected_value
            prediction_metadata["shap_feature_values"] = shap_feature_values
            prediction_metadata["shap_plot"] = encoded_shap_plot
            prediction_metadata["predicted_result"] = self.prediction_result
            prediction_metadata.pop("model_save_path")
            query = {"collection_name" : "predictions", "data" : prediction_metadata}
            dbu.insertData(query)
        except:
             errorhandling.catchError(custom_message=configData["errorID"]["308"])
            

        
        