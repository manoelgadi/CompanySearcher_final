# A very simple Flask Hello World app for you to get started with...

from flask import Flask,render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

if False: # Put it True if MySQL in pythonanywhere
    # Create a connection to the MySQL database
    import mysql.connector
    conn = mysql.connector.connect(
        host='your_hostname',
        user='your_username',
        password='your_password',  # replace with your password
        database='your_data$base'
    )
else:
    import sqlite3
    conn = sqlite3.connect('./database/company_balancesheet_database.db')

pd.set_option('display.float_format', lambda x: '%.3f' % x)
df = pd.read_sql("""SELECT * FROM cuentas_anuales;""", conn)

df.drop('id',inplace=True,axis=1)

df.columns = ['NIF', 'Name', 'CNAE', 'Total Assets - 2017', 'Total Assets - 2016', 'Total Assets - 2015', 'Own Resources - 2017', 'Own Resources - 2016', 'Own Resources - 2015', 'Short Debt - 2017', 'Short Debt - 2016', 'Short Debt - 2015', 'Long Debt - 2017', 'Long Debt - 2016', 'Long Debt - 2015', 'Income - 2017', 'Income - 2016', 'Income - 2015', 'Amortization - 2017', 'Amortization - 2014', 'Amortization - 2015', 'Profit - 2017', 'Profit - 2016', 'Profit - 2015', 'Status']


@app.route("/")
def index():
    return render_template("index.html", df = df, ids = list(range(len(df))))

from joblib import load
model = load('Rating_RandomForestClassifier.joblib')

@app.route("/probdefaultfixed")
def probdefaultfixed():
    """ Probability of Default Harded Coded """
    # dictionary with list object in values
    data = {
        'ebitda_income' : [0.3],
        'debt_ebitda' : [20],
        'rraa_rrpp' : [0.5],
        'log_operating_income' : [2000]
    }

    # creating a Dataframe object
    data_df = pd.DataFrame(data)
    X = data_df[['ebitda_income','debt_ebitda','rraa_rrpp','log_operating_income']]

    # predict
    prob_default = model.predict_proba(X)[:,1]

    return "Probability of default: {}".format(prob_default)


@app.route("/probdefault")
def probdefault():
    """ Probability of Default Harded Coded """
    # dictionary with list object in values
    data = {
        'ebitda_income' : [request.args["ebitda_income"]],
        'debt_ebitda' : [request.args["debt_ebitda"]],
        'rraa_rrpp' : [request.args["rraa_rrpp"]],
        'log_operating_income' : [request.args["log_operating_income"]]
    }

    # creating a Dataframe object
    data_df = pd.DataFrame(data)
    X = data_df[['ebitda_income','debt_ebitda','rraa_rrpp','log_operating_income']]

    # predict
    prob_default = model.predict_proba(X)[:,1]

    return "Probability of default: {}".format(prob_default)


@app.route("/cs")
def cs():
    """ Company Searcher """
    data=df[df['NIF']==request.args['nif']].head(1)
    if 'model' in request.args:
        data['ebitda_income']=(data['Profit - 2017']+data['Amortization - 2017'])/data['Income - 2017']
        data['debt_ebitda']=(data['Short Debt - 2017']+data['Long Debt - 2017'])/(data['Profit - 2017']+data['Amortization - 2017'])
        data['rraa_rrpp']=(data['Total Assets - 2017']-data['Own Resources - 2017'])/data['Own Resources - 2017']
        data['log_operating_income']=np.log(data['Income - 2017'])
        data=data.replace([np.inf, -np.inf], np.nan).fillna(0)
        X = data[['ebitda_income','debt_ebitda','rraa_rrpp','log_operating_income']]
        data['probabilidad_default']=model.predict_proba(X)[:,1]
    if 'JSON' in request.args:
        return data.to_json(orient='records')
    else:
        return render_template("index.html", df = df, ids = list(range(len(df))), result = 1, data = data.T.to_html())


if __name__ == '__main__': # This only runs if
  app.run()
