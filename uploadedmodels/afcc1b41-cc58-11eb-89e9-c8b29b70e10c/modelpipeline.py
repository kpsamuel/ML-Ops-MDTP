# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 13:19:57 2021

@author: samuel
"""
import json
from pandas import Series
from numpy import array
import pickle
from sklearn.pipeline import Pipeline


with open("modelconfig.json", "r") as fp:
    modelconfig = json.load(fp)
    
modelpath = modelconfig["modelname"]
trained_feature_scaler = modelconfig["trained_feature_scaler"]

## helper function to un-pickle the files
def loadTrainedObjects(filepath):
    with open(filepath, "rb") as fp:
        trained_object = pickle.load(fp)
        return trained_object
    
## prediction function
def prediction(x_feature):
    
    x_feature = array(Series(x_feature)).reshape(1, -1)
    linear_model = loadTrainedObjects(modelpath)
    featureScaler = loadTrainedObjects(trained_feature_scaler)
    
    model_pipeline = Pipeline(steps=[('feature_transformation', featureScaler),
                                     ('linear_model', linear_model)])

    predicted_result = model_pipeline.predict(X=x_feature)
    return predicted_result[0]

if __name__ == "__main__":
    with open(modelconfig["input_file_to_refer"], "r") as fp:
        input_features = json.load(fp)
    
    predicted_result = prediction(input_features)
    
    with open(modelconfig["predicted_file_to_refer"], "w") as fp:
        json.dump({"predicted_result":predicted_result}, fp)
        


