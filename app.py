from flask import Flask, render_template, request

import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn import linear_model
import scipy.stats as stat
from sklearn.feature_selection import chi2

import config

app = Flask(__name__)

reg_pd = pickle.load(open('pd_model_deployment.sav', 'rb'))
score = pd.read_csv("df_scorecard.csv")
features = score.groupby('Original feature name')["Feature name"].apply(list)[1:]
features = features.to_dict()

def country(alpha_name):
    import pycountry
    return pycountry.countries.get(alpha_2=alpha_name).name
def categories(lst):
    return [[cat,",".join(cat.split(":")[1].split("_"))] for cat in lst]
app.jinja_env.globals.update(categories=categories)    
@app.route("/")
def home():
    
    #reg_pd.model.predict_proba(loan_data_inputs_pd_temp)[: ][: , 0]    
    categories = {'manufacturer':[1,2,3],'condition':[1,2,3],
    'fuel':[1,2,3],'size':[1,2,3],'type':[1,2,3],'transmission':[1,2,3],'paint_color':[1,2,3]
    ,'type':[1,2,3],'drive':[1,2,3],'cylinders':[1,2,3]}
    
    return render_template("index.html",form_data={},type=0,data=categories,features=features)

@app.route("/predict",methods=['POST'])
def predict():
    
    ref_categories_pd = config.ref_categories_pd

    df= pd.read_csv("deployment_pd_load_data.csv")
    df.columns = ['Feature','Value']
    df = pd.pivot_table(df, values='Value',columns=['Feature'])
    df = df.reset_index(drop=True)
    df.iloc[0,:]=0
    
    for col in features:     
        value = request.form[col]
        if value not in ref_categories_pd:
            df[value]=1
    probabilty_of_default = reg_pd.predict_proba(df)[: ][: , 0][0]   

    df.insert(0, 'Intercept', 1)
    score = pd.read_csv("df_scorecard.csv")
    scores = score[score["Feature name"].isin(df.columns)]['Score - Final'].values.reshape(df.shape[1], 1)  
    credit_score = df.dot(scores).values[0][0]   
    
    return render_template("index.html",form_data=request.form,type=1,pd=round(probabilty_of_default,2),credit_score=credit_score,features=features)

if __name__ == "__main__":          
    app.run(debug=True)
