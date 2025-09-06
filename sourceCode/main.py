from flask import Flask, render_template, abort,request,redirect,url_for,flash
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
import driver
import Rainfall
import alerter
 
 
app = Flask(__name__)

app.secret_key='5791628bb0b13ce0c676dfde280ba245' 
#app.config['SECRET_KEY']='5791628bb0b13ce0c676dfde280ba245'
 
# @app.route('/')
# def home():
#     return render_template('main.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/refreshFlood')
def refreshFlood():
    alerter.water_level_predictior()#To refresh the flood warning data
    return redirect(url_for('floodHome'))
@app.route('/about')
def about_team():
    return render_template('about-team.html')

@app.route('/contacts')
def contact():
    return render_template('contact.html')

@app.route('/services')
def service():
    return render_template('service.html')


@app.route('/floodHome')
def floodHome():
    res=alerter.alerting()
    for i in range(len(res)):
        res[i]='Flood ALERT '+res[i]
    return render_template('flood_entry.html',result=res)


@app.route('/rainfallHome')
def rainfallHome():
    return render_template('rain_entry.html')



from datetime import datetime
from dateutil.relativedelta import relativedelta

@app.route('/floodResult', methods=['POST', 'GET'])
def floodResult():
    if request.method == 'POST':
        if len(request.form['DATE']) == 0:
            return redirect(url_for('floodHome'))
        else:
            # Get user input date and modify it by subtracting 8 years
            user_date = request.form['DATE']
            try:
                date_obj = datetime.strptime(user_date, "%Y-%m-%d")
                new_date = date_obj - relativedelta(years=8)
            except ValueError:
                # Handle invalid date formats
                return redirect(url_for('floodHome'))

            # Get selected river from form
            river = request.form['SEL']
            
            # Call driver function with modified date and river
            results_dict = driver.drive(river, new_date)

            # Create a Table to store results
            Table = []
            for key, value in results_dict.items():
                Table.append(value)
            
            # Assuming 'discharge' and 'Mse' are part of the results_dict
            discharge = results_dict.get('discharge', "0")  # Default to "0" if not found
            # mse = results_dict.get('Mse', "1")  # Default to "1" if not found
            
            # Convert discharge and mse to numeric values for comparison
            try:
                discharge = float(discharge)
                # mse = float(mse)
            except ValueError:
                # Handle case where discharge or Mse cannot be converted to numbers
                discharge = 0
                # mse = 1
            
            # Prediction logic: if discharge is above a threshold and MSE is below a threshold
            # mean squre error
            flood_prediction = "Yes" if discharge > 1500  else "No"
            
            # Append prediction to the result Table or pass it separately to the template
            Table.append(flood_prediction)

            # Render the result page with Table and prediction
            return render_template('flood_result.html', result=Table, prediction=flood_prediction)
    else:
        return redirect(url_for('floodHome'))


@app.route('/rainfallResult', methods=['POST', 'GET'])
def rainfallResult():
    if request.method == 'POST':
        if len(request.form['Year']) == 0:
            flash("Please Enter Data!!")
            return redirect(url_for('rainfallHome'))
        else:
            year = request.form['Year']
            try:
                new_year = int(year) - 9
            except ValueError:
                flash("Invalid Year! Please enter a valid number.")
                return redirect(url_for('rainfallHome'))

            region = request.form['SEL']
            print("##3#######", new_year, "#####", region, "#############")

            mae, score = Rainfall.rainfall(new_year, region)

            # Convert mae to a float before comparing
            try:
                mae = float(mae)
            except ValueError:
                flash("Invalid MAE value returned.")
                return redirect(url_for('rainfallHome'))

            # Adding the prediction logic
            if mae < 70:  # Adjust the threshold as needed
                prediction = "Yes"

            else:
                prediction = "No"

            return render_template('rain_result.html', Mae=mae, Score=score, Prediction=prediction)
    else:
        return redirect(url_for('rainfallHome'))


    # return render_template('rainfallResult.html'

if __name__ == '__main__':
    app.run(debug = True)