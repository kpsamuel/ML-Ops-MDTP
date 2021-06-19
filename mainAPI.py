# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 06:49:57 2021

@author: samuel
"""

import json
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api

## importing custome packages
import modelsmanagement
import runtimemodel
import databaseutil
dbu = databaseutil.databaseConnect()


app = Flask(__name__)
api = Api(app)

with open("config.json", "r") as file:
    configData = json.load(file)


## =================================== apis ===================================== ##

"""
    api to check api service is up and running
"""
class appStatus(Resource):
    def get(self):
        return make_response(jsonify({"status":200, "message":"system up and running"}))

"""
    api to manage models i.e., upload models and delete them from monitoring system
"""
class uploadModel(Resource):
    
    def post(self):
        uploadedmodel = request.files.get("model")
        model_info = {
                      "attachment_filename" : uploadedmodel.filename, 
                      "model" : uploadedmodel,
                      }
        
        mm = modelsmanagement.modelManagement()
        response_info = mm.uploadModel(modeldata=model_info)
        return make_response(jsonify({"response" : response_info}))
    
    def delete(self):
        requestdata = request.get_json()
        mm = modelsmanagement.modelManagement()
        response_info = mm.deleteModel(requestdata=requestdata)
        return make_response(jsonify({"response" : response_info}))
    
        
"""
    api to make prediction on uploaded models in monitoring system
"""
class makePrediction(Resource):
    
    def get(self):
        prediction_info = request.get_json()
        rtm = runtimemodel.runVirtualModel(prediction_info)
        prediction_result = rtm.prediction_result
        err_msg = rtm.err_msg
        if prediction_result == -99999999999999:
            return make_response(jsonify({"error" : err_msg}))
        else:
            return make_response(jsonify({"prediction_result" : prediction_result}))
    
"""
    api to get monitored logs of model on each predictions made
"""
class getMMLogs(Resource):
    
    def get(self):
        requestdata = request.get_json()
        query = {"collection_name" : "predictions", "select_query" : {"mmid" : requestdata["mmid"]}}
        model_prediction_data = dbu.getData(query)
        return make_response(jsonify({"model_prediction_tracking_logs" : model_prediction_data}))
        
    
### ==================================== api end points ====================================== ###
api.add_resource(appStatus, "/appstatus")
api.add_resource(uploadModel, "/uploadmodel")
api.add_resource(makePrediction, "/predict")
api.add_resource(getMMLogs, "/mmlogs")



### ======================================= app run ========================================== ###
if __name__ == "__main__":
    app.run(debug=False, host=configData.get("apiHostName"), port=configData.get("apiPortNumber"))