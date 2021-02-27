# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 12:43:41 2020

@author: Shirin
"""

######################################################################
                        # IMPORTING LIBRARIES
######################################################################

from pandas.core.indexing import convert_to_index_sliceable
import pandas as pd
import numpy as np
import requests
import os
import re
import sklearn
import pickle
from flask import Flask, render_template, request, make_response,redirect,url_for,session, jsonify, flash
import string
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from datetime import datetime
import yfinance as yf
import scipy.optimize as optimize
from scipy.stats import norm
from dateutil.relativedelta import relativedelta
from email_validator import validate_email, EmailNotValidError
from flask_mail import Mail, Message
import textwrap

# defining base directory as per the location of app.py file
basedir = os.path.abspath(os.path.dirname(__file__))

# initiating flask here
app = Flask(__name__)
mail= Mail(app)
######################################################################
                        # DEFINING IMP VARIABLES
######################################################################

# assigning secret key for session information
app.secret_key = 'YbpemWvv8DHIteU0eY99DA'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'robofina.advisors@gmail.com'
app.config['MAIL_PASSWORD'] = 'r0b0fina156'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# # updating the app config regarding the upload file folder and dropzone
# app.config.update(
#     SQLALCHEMY_DATABASE_URI ='sqlite:///'+os.path.join(basedir, 'app.db'),
#     SQLALCHEMY_TRACK_MODIFICATIONS=False
# )

############################################
        # SQL DATABASE AND MODELS
############################################

# db = SQLAlchemy(app)
# migrate = Migrate(app,db)

# class questionnaire(db.Model):

#     __tablename__ = 'questionnaire'
    
#     id = db.Column(db.Integer,primary_key = True)
#     user_name = db.Column(db.String(200), nullable=False)
#     user_email = db.Column(db.String(200), nullable=False)
#     date_created = db.Column(db.DateTime, default = datetime.utcnow)

#     def __init__(self,user_name,user_email,date_created):
#         self.user_name = user_name
        
#         self.user_email = user_email
#         self.date_created = date_created

#     def __repr__(self):
#         return f"File name: {self.user_name} {self.date_created} "


######################################################################
                        # RISK SCORE CALCULATOR
######################################################################

print(os.path.join(basedir, 'ML/robo_advisor_model.sav'))
loaded_model = pickle.load(open(os.path.join(basedir, 'ML/robo_advisor_model.sav'), 'rb'))

# taking input of the data
assets_sel = pd.read_csv(os.path.join(basedir, 'ML/data_for_robo.csv'),parse_dates=[0],index_col=0)

def risk_score_calculator(loaded_model=loaded_model):

    risk_tol = []

    ################## PART 1 : Demographic Risk ####################
    AGE07        = session.get('age')
    KIDS07       = session.get('children')
    INCOME07     = session.get('salary')
    NETWORTH07   = session.get('net_income')

    if session.get('education')=='1':
        EDCL07_2 = 0
        EDCL07_3 = 0
        EDCL07_4 = 0
    elif session.get('education')=='2':
        EDCL07_2 = 1
        EDCL07_3 = 0
        EDCL07_4 = 0
    elif session.get('education')=='3':
        EDCL07_2 = 0
        EDCL07_3 = 1
        EDCL07_4 = 0
    else:
        EDCL07_2 = 0
        EDCL07_3 = 0
        EDCL07_4 = 1

    if session.get('work')=='1':
        OCCAT107_2 = 0
        OCCAT107_3 = 0
        OCCAT107_4 = 0
    elif session.get('work')=='2':
        OCCAT107_2 = 1
        OCCAT107_3 = 0
        OCCAT107_4 = 0
    elif session.get('work')=='3':
        OCCAT107_2 = 0
        OCCAT107_3 = 1
        OCCAT107_4 = 0
    else:
        OCCAT107_2 = 0
        OCCAT107_3 = 0
        OCCAT107_4 = 1

    if session.get('risk_cap')=='1':
        RISK07_2 = 0
        RISK07_3 = 0
        RISK07_4 = 1
    elif session.get('risk_cap')=='2':
        RISK07_2 = 0
        RISK07_3 = 1
        RISK07_4 = 0
    elif session.get('risk_cap')=='3':
        RISK07_2 = 1
        RISK07_3 = 0
        RISK07_4 = 0
    else:
        RISK07_2 = 0
        RISK07_3 = 0
        RISK07_4 = 0

    if session.get('marriage')=='1':
        MARRIED07_2 = 0
    else:
        MARRIED07_2 = 1

    feature_list = [[AGE07,KIDS07,INCOME07,NETWORTH07,EDCL07_2,EDCL07_3,EDCL07_4,MARRIED07_2,
                    OCCAT107_2,OCCAT107_3,OCCAT107_4,RISK07_2,RISK07_3,RISK07_4]]

    demo_risk = loaded_model.predict(feature_list)
    risk_tol.append(demo_risk.tolist()[0])

    ################## PART 2 : Behavioral Risk ####################

    behav_risk = ((session.get('primary_goal_risk') + session.get('investment_length')) * 0.5187) + \
                    ((session.get('investment_choice') + session.get('risk_mind')) * 0.2957) + \
                        ((session.get('risk_cap') + session.get('invest_decline') + \
                            session.get('success_plan') + session.get('best_worst')) * 0.1856)

    # Normalizing
    behav_risk = ((behav_risk-2.37)/(9.47-2.47))
    risk_tol.append(behav_risk)
    
    return risk_tol


#Asset allocation given the Return, variance
def get_asset_allocation(riskTolerance):
    
    if 0 <= riskTolerance < 0.2:
        stocks = 0.20
        bonds  = 0.55
        other  = 0.25
    elif 0.2 <= riskTolerance < 0.4:
        stocks = 0.40
        bonds  = 0.50
        other  = 0.10 
    elif 0.4 <= riskTolerance < 0.6:
        stocks = 0.60
        bonds  = 0.35
        other  = 0.05
    elif 0.6 <= riskTolerance < 0.8:
        stocks = 0.70
        bonds  = 0.25
        other  = 0.05  
    else:
        stocks = 0.80
        bonds  = 0.15
        other  = 0.05   
        
    session['stocks'] = stocks
    session['bonds']  = bonds
    session['other']  = other
    ################### For Minimum Variance ######################

    #for minimum variance portfolio based
    def port_alloc(type,asset_list):

        val = assets_sel[asset_list]

        def portfolio_stats(weights):
            # Convert to array in case list was passed instead.
            weights = np.array(weights)
            cov_matrix = val.pct_change().apply(lambda x: np.log(1+x)).cov()
            min_var = np.sqrt(cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum())*np.sqrt(252)
            return min_var

        def minimize_variance(weights):  
            return portfolio_stats(weights)

        constraints = ({'type' : 'eq', 'fun': lambda x: np.sum(x) - type})
        num_assets = len(asset_list)
        bounds = tuple((0,type) for x in range(num_assets))
        initializer = num_assets * [1./num_assets,]

        min_variance=optimize.minimize(minimize_variance,
                                        initializer,
                                        method = 'SLSQP',
                                        bounds = bounds,
                                        constraints = constraints)

        min_variance_weights=min_variance['x'].round(4)
        return list(zip(asset_list,list(min_variance_weights)))


    stock_weights = pd.DataFrame(port_alloc(type=stocks,asset_list=['VTI','VEA','VWO']))
    bond_weights  = pd.DataFrame(port_alloc(type=bonds,asset_list=['EMB','BNDX','MUB']))
    other_weights = pd.DataFrame(port_alloc(type=other,asset_list=['VDE','VNQ','VHT']))
    final_weights = stock_weights.append(bond_weights.append(other_weights))
    final_weights = final_weights.set_index(0)
    
    return final_weights.to_dict()


# function for monte carlo simulation
def monte_simulation(years):
    
    dates = pd.bdate_range(start=datetime.today(),
                            end=datetime.today() + \
                                relativedelta(years=years))
    days  = len(dates)
    
    portfolio     = session.get('portfolio_alloc')
    portfolio_col = list(portfolio['1'].keys())
    # print(portfolio_col)
    
    filter_data   = assets_sel.filter(items=portfolio_col)
    port_data     = filter_data.assign(**portfolio['1']).mul(filter_data).sum(1)
    
    log_return    = np.log(1+ port_data.pct_change())
    
    #Calculate the Drift
    ret   = log_return.mean()
    var   = log_return.var()
    drift = ret - (0.5 * var)

    #Calculate standard deviation of returns
    stddev        = log_return.std()
    daily_returns = np.exp(drift + stddev * norm.ppf(np.random.rand(days,100)))
        
    # Create matrix with same size as daily returns matrix
    price_list   = np.zeros_like(daily_returns)

    # Introduce the last known price for the stock in the first item of every iteration - ie Day 0  for every trial in the simulation
    price_list[0] = port_data.iloc[-1]
    
    # running the simulation
    for t in range(1,days):
        price_list[t] = price_list[t-1]*daily_returns[t]
        
    median_proj = np.median(price_list,axis=1)
    upper_proj  = np.percentile(price_list,75,axis=1)
    lower_proj  = np.percentile(price_list,25,axis=1)
    
    dates       = dates.map(lambda t: +t.strftime('%Y,%m,%d')) 
    
    monte_data  = pd.DataFrame(np.column_stack([dates,
                                                    lower_proj,
                                                        median_proj-lower_proj,
                                                            upper_proj-median_proj,
                                                                lower_proj,
                                                                    median_proj,
                                                                        upper_proj]))
    
    return monte_data
    

######################################################################
                        # DEFINING ROUTES
######################################################################

# this is the basic landing page for 1st set of questions in Robo Advisor
@app.route('/')
def index():
    # rendering landing page for the non-registered users with all parameters
    session.clear()
    print(session)  
    return render_template('index.html')


# this is the 1st page containing basic questions based on the input received from index page
@app.route('/adv_quest1', methods=['POST','GET'])
def adv_quest1():
    try:
        if request.method == "POST":

            session['name']  = request.form['name']
            print("name:",session.get('name'))
            session['email'] = request.form['email']
            print("email:",session.get('email'))

            if "financial_expert" in request.form:
                session['financial_expert'] = 'NO'
            else:
                session['financial_expert'] = 'YES'

            print("financial_expert:",session.get('financial_expert'))
            # rendering the 1st question page for the users
            return render_template('1st_page.html')

    except Exception as e:
        error_content = "Application is unable to process landing page entries."
        return render_template("500.html", error_content = error_content, error = str(e))



# this is the 2nd page containing advanced questions based on the input received from 1st page
@app.route('/adv_quest2', methods=['POST','GET'])
def adv_quest2():
    #return render_template('2nd_page.html')
    try:
        # first extracts the information of the image from the submit form on 'completed' page
        if request.method == "POST":

            # fetching age 
            session['age'] = int(request.form['age_q'])

            # fetching range of income and then taking average
            net_income1 = request.form['net_income1']
            net_income2 = request.form['net_income2']
            session['net_income'] = (int(net_income1) + int(net_income2))/2

            # fetching range of salary and then taking average
            salary1 = request.form['salary1']
            salary2 = request.form['salary2']
            session['salary'] = (int(salary1) + int(salary2))/ 2

            # fetching education category
            session['education'] = request.form['education']

            # fetching marriage category
            session['marriage'] = request.form['marriage']

            #fetching children category
            session['children'] = int(request.form['children'])

            #fetching work category
            session['work'] = request.form['work']

            print("age:",session.get('age'))
            print('net_income:',session.get('net_income'))
            print('salary:',session.get('salary'))
            print('education:',session.get('education'))
            print('marriage:',session.get('marriage'))
            print('children:',session.get('children'))
            print('work:',session.get('work'))

            print(request.form)

            # rendering landing page for the non-registered users with all parameters
            return render_template('2nd_page.html')

    except Exception as e:
        error_content = "Application is unable to process demographic data."
        return render_template("500.html", error_content = error_content, error = str(e))


# this is the 2nd page containing advanced questions based on the input received from 1st page
@app.route('/adv_quest3', methods=['POST','GET'])
def adv_quest3():
    #return render_template('3rd_page.html')
    try:
        # first extracts the information of the image from the submit form on 'completed' page
        if request.method == "POST":
            
            # fetching the amount of risk user can take from
            session['risk_cap'] = int(request.form['risk_cap'])

            # fetching answer for 'how large of a decline in investment will be accepted'
            session['invest_decline'] = int(request.form['invest_decline'])

            # fetching answer for 'what comes in mind when thinking of risk'
            session['risk_mind'] = int(request.form['risk_mind']) 

            # fetching answer for 'likelihood of financial plan's success'
            session['success_plan'] = int(request.form['success_plan'])

            # fetching answer for 'best and worst case of investment choice'
            session['best_worst'] = int(request.form['best_worst'])

            # fetching answer for 'investment choice into bonds, stocks etc'
            session['investment_choice'] = int(request.form['investment_choice'])

            # fetching answer for 'primary goal'
            session['primary_goal_risk'] = int(request.form['primary_goal_risk'])

            # fetching answer for 'length of investment'
            session['investment_length'] = int(request.form['investment_length'])
            
            print('risk_capacity:',session.get('risk_cap'))
            print('invest_decline:',session.get('invest_decline'))
            print('risk_mind:',session.get('risk_mind'))
            print('success_plan:',session.get('success_plan'))
            print('best_worst:',session.get('best_worst'))
            print('investment_choice',session.get('investment_choice'))
            print('primary_goal_risk',session.get('primary_goal_risk'))
            print('investment_length',session.get('investment_length'))
            print(request.form)

            calculated_risk = risk_score_calculator()
            session['demo_risk'] = calculated_risk[0]
            session['beha_risk'] = calculated_risk[1]
            session['avg_risk']  = (session['demo_risk'] + session['beha_risk'])/2
            
            print('demo_risk:',session.get('demo_risk'))
            print('beha_risk:',session.get('beha_risk'))
            print('avg_risk:',session.get('avg_risk'))
            
            session['portfolio_alloc'] = get_asset_allocation(session['avg_risk'])
            print('portfolio_alloc:',session.get('portfolio_alloc'))

            # rendering landing page for the non-registered users with all parameters
            return render_template('3rd_page.html')

    except Exception as e:
        error_content = "Application is unable to process behavioral data."
        return render_template("500.html", error_content = error_content, error = str(e))


# this is the 2nd page containing advanced questions based on the input received from 1st page
@app.route('/portfolio', methods=['POST','GET'])
def portfolio():
    #return render_template('3rd_page.html')
    try:
        # first extracts the information of the image from the submit form on 'completed' page
        if request.method == "POST":
            
            # fetching the amount of risk user can take from
            session['amount'] = int(request.form['investment_amt'])

            # create a dictionary
            dic = {'BNDX': 'Vanguard Total International Bond ETF',
                    'EMB': 'iShares USD Emerging Markets Bond ETF',
                    'MUB': 'iShares National Muni Bond ETF',
                    'VDE': 'Vanguard Energy Index Fund ETF',
                    'VEA': 'Vanguard Developed Markets Index Fund ETF',
                    'VHT': 'Vanguard Health Care Index Fund ETF',
                    'VNQ': 'Vanguard Real Estate Index Fund ETF',
                    'VTI': 'Vanguard Total Stock Market Index Fund ETF',
                    'VWO': 'Vanguard Emerging Markets Index Fund ETF'}
            
            # creating final table
            port_allocation     = session.get('portfolio_alloc')
            final_table         = pd.DataFrame(port_allocation).reset_index()
            final_table.columns = ['ETFs','Weights']
            etf_name            = final_table["ETFs"].map(dic)
            final_table.insert(loc=1, column='Holdings', value=etf_name)
            final_table['Amount ($)']     = round(final_table['Weights']*session.get('amount'),2)
            final_table['Weights'] = final_table['Weights'].apply(lambda x: str(round(100*x,2))+' %')
            final_table                   = final_table.loc[~(final_table['Amount ($)']<1),:]
            
            time_monte = {1 : 5,
                            2 : 10,
                                3 : 20,
                                    4 : 22}
            
            # # calling monte carlo function for simulation
            monte_data = monte_simulation(time_monte[session.get('investment_length')])
            
            start_price = monte_data.iloc[0,1]
            last_price  = monte_data.iloc[-1,5]
            no_of_stock = session.get('amount')/start_price
            project_amt = int(no_of_stock * last_price)
            monte_data.iloc[:,1:] =  np.round(monte_data.iloc[:,1:] * no_of_stock,2)
            
            data = {'Portfolio' : 'ETF distribution', 
                        'Stocks' : session.get('stocks'), 
                            'Bonds' : session.get('bonds'), 
                                'Energy' : port_allocation['1']['VDE'], 
                                    'Real Estates' : port_allocation['1']['VNQ'],
                                        'Health Care' : port_allocation['1']['VHT']}
            
            time_dict = {1 : '0-5 years',
                            2 : '6-10 years',
                                3 : '11-20 years',
                                    4 : '21+ years'}
            
            time_span   = time_dict[session.get('investment_length')]
            
            risk_tol    = str(round(session.get('avg_risk'),2))
            
            amount      = "{:,}".format(session.get('amount')) + ' USD'
            project_amt = "{:,}".format(project_amt) + ' USD'
            
            # rendering landing page for the non-registered users with all parameters
            return render_template('dashboard.html', column_names=final_table.columns.values, 
                                                        row_data=list(final_table.values.tolist()),
                                                            zip=zip, data=data, time_span=time_span,
                                                                risk_tol = risk_tol, amount = amount,
                                                                    projected_amt=project_amt, monte_exp=monte_data)

    except Exception as e:
        error_content = "Application is unable to create dashboard."
        return render_template("500.html", error_content = error_content, error = str(e))
   
# this is the basic landing page for 1st set of questions in Robo Advisor
@app.route('/contact_us', methods=['POST','GET'])
def contact_us():
    try:
        if request.method == 'POST':
                
            # fetching name
            name = request.form['txtName']
            # fetching email
            email = request.form['txtEmail']
            # fetching message
            message = request.form['txtMsg']
            
            try:
                valid_email = validate_email(email)
            except:
                valid_email = False
            
            if valid_email:
                
                msg = Message('r0b0fina advisors - New message from ' + name , 
                                sender='robofina.advisors@gmail.com', 
                                recipients=['robofina.advisors@gmail.com'])
                body_txt = """
                            From: %s <%s>
                            
                            %s
                            
                            """ % (name, email, message)
                msg.body = textwrap.dedent(body_txt)
                mail.send(msg)
                
                msg = Message('Thank you for contacting - robofina advisors', 
                                sender='robofina.advisors@gmail.com', 
                                recipients=[email])
                body_txt = """
                            Dear %s,
                            
                            Thank you for contacting us. We will try to answer your question as soon as possible. 
                            
                            All emails are answered within 24 by our support team.
                            
                            We appreciate your patience,
                            robofina Support Team
                            %s
                            """ % (name, 'robofina.advisors@gmail.com')
                            
                msg.body = textwrap.dedent(body_txt)
                mail.send(msg)
                
                flash('Message has been submitted successfully','success')
                return redirect(url_for('contact_us'))
            
            else:
                
                flash('Please enter correct email details!','error')
                return redirect(url_for('contact_us'))  

        else:
            return render_template('contact_us.html')

    except:
        flash('Something went wrong, please try again later!','error')
        return redirect(url_for('contact_us'))  


@app.route('/healthcheck', methods=['GET'])
def healthCheck():
    return "Robofina is healthy",200
    
# defining a method to handle 404 error by rendering 404.html file
@app.errorhandler(404)
def not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


# running above python script
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)