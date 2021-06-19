# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 16:36:20 2021

@author: samuel
"""
import os
import json
import datetime
import pickle
import pandas as pd
import shap
import base64

## importing custom packages
import errorhandling
import databaseutil
dbu = databaseutil.databaseConnect()

with open("config.json", "r") as fp:
    configData = json.load(fp)
    

"""
    model prediction explaniabilty operations are done here.
    used shap as tool to explain models prediction.
"""
class explainable():
    
    def __init__(self):
        pass
    
    def readdatafiles(self, filepath):
        try:
            if filepath.split(".")[-1] == "csv":
                filedata = pd.read_csv(filepath)
            
            elif filepath.split(".")[-1] == "json":
                filedata = pd.read_json(filepath)
            
            return filedata, 0 
        except Exception as err_msg:
            errorhandling.catchError(custom_message=configData["errorID"]["302"])
            return None, -1
        

    def loadmodel(self, modelpath):
        """
            reading pickle file of model
        """
        try:
            with open(modelpath, "rb") as mp:
                model = pickle.load(mp)
            return model, 0
        except Exception as err_msg:
            errorhandling.catchError(custom_message=configData["errorID"]["303"])
            return None, -1
        
                
    def createExplainableEnv(self, modelmetadata):
        """
            this method will creat model explainable kernel on the model upload time and saves it in pickle.
            so, that from prediction time it can used for explaining the prediction.

            NOTE : this requires x_training_features, 
                   so while uploading the model to monitoring system make sure you have x_train data and 
                   configured it with correct name in "modelconfig.json" file
        """
        try:
            x_train_filepath = os.path.join(modelmetadata["model_savepath"], modelmetadata["x_train_filename"])
            x_train, data_flag = self.readdatafiles(x_train_filepath)
        
            model_filepath= os.path.join(modelmetadata["model_savepath"], modelmetadata["modelname"])
            trainned_model, model_flag = self.loadmodel(model_filepath)
            
            ## checking the condition for x_training data and uploaded model read correctly. if not than model explainable will not be created.
            ## and in db-collection (uploadedmodels) "explainable_environment" status will be "false".

            if (data_flag == 0) and (model_flag == 0):
                
                x_train_summary = shap.kmeans(x_train,k=len(x_train.columns))
                exp = shap.KernelExplainer(model=trainned_model.predict, data=x_train_summary)        
                    
                with open(os.path.join(modelmetadata["model_savepath"], "modelexplainable.pkl"), "wb") as mp:
                    pickle.dump(exp, mp)
                
            return 0
        except Exception as err_msg:
            errorhandling.catchError(custom_message=configData["errorID"]["304"])
            return -1
        
    def explainPrediction(self, predict_metadata):

        """
            if explainable_environment value is "true", than this method is called to make explaination using shap values.
            NOTE : 
                    currently linear and classification model explainable kernel is used.
                    in new coming version rest other kernels will be added
        """
        try:
            with open(os.path.join(predict_metadata["model_save_path"], "modelexplainable.pkl"), "rb") as fp:
                trainedexplainer = pickle.load(fp)
            
            shap_figure_path = os.path.join(predict_metadata["model_save_path"], predict_metadata["predictionID"] + ".png")
            x_features = pd.Series(predict_metadata["x_features"])
            shap_values = trainedexplainer.shap_values(x_features)
            
            self.shap_feature_values = {}
            for shap_fea_value, fea_name in zip(shap_values, x_features.index):
                self.shap_feature_values[fea_name] = shap_fea_value
                
            self.expected_value = trainedexplainer.expected_value
            shap.force_plot(self.expected_value, 
                            shap_values, 
                            x_features,
                            show=False, 
                            matplotlib=True).savefig(shap_figure_path, 
                                                     format = "png",
                                                     dpi = 200,
                                                     bbox_inches = 'tight')
    
            with open(shap_figure_path, "rb") as image_file:
                self.encoded_shap_plot = base64.b64encode(image_file.read())
                
            return 0
        except Exception as err_msg:
            errorhandling.catchError(custom_message=configData["errorID"]["307"])
            return -1
        