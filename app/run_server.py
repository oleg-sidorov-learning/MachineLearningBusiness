import dill
from datetime import date
from flask import Flask, jsonify, abort, make_response, request, redirect
from flask import render_template
import json
import pandas as pd
import logging
from app.functions import get_process_functions, load_model


# http://127.0.0.1:5000/weather/api/v1.0/getpred


logging.basicConfig(filename='logs/logs.log', level=logging.DEBUG)
dill._dill._reverse_typemap['ClassType'] = type

# creating instance of flask applocation
app = Flask(__name__)

model = load_model()
process = get_process_functions()

targets = ['Sunny', 'Rain']


def get_pred(curr_date, location, minTemp, maxTemp,
             rainFall, evaporation, sunshine, windGustDir,
             windGustSpeed, windDir9am, windDir3pm, windSpeed9am,
             windSpeed3pm, humidity9am, humidity3pm, pressure9am,
             pressure3pm, cloud9am, cloud3pm, temp9am,
             temp3pm, rainToday):
    """Function created to obtain predictions from set of data which was obtained from the request"""

    column_names = ['Date', 'Location', 'MinTemp', 'MaxTemp', 'Rainfall', 'Evaporation', 'Sunshine',
                    'WindGustDir', 'WindGustSpeed', 'WindDir9am', 'WindDir3pm', 'WindSpeed9am', 'WindSpeed3pm',
                    'Humidity9am', 'Humidity3pm', 'Pressure9am', 'Pressure3pm', 'Cloud9am', 'Cloud3pm',
                    'Temp9am', 'Temp3pm', 'RainToday']

    lst = [curr_date, location, minTemp, maxTemp, rainFall, evaporation, sunshine, windGustDir, windGustSpeed,
           windDir9am, windDir3pm, windSpeed9am, windSpeed3pm, humidity9am, humidity3pm,
           pressure9am, pressure3pm, cloud9am, cloud3pm, temp9am, temp3pm, rainToday]

    data_dict = dict(zip(column_names, lst))

    print(data_dict)

    # create dataframe from data above and format according model expectation
    df = pd.DataFrame(data=data_dict,
                      index=[0]
                      )
    df[['MinTemp', 'MaxTemp', 'Rainfall', 'Evaporation', 'Sunshine', 'WindGustSpeed', 'WindSpeed9am',
        'WindSpeed3pm', 'Humidity9am', 'Humidity3pm', 'Pressure9am', 'Pressure3pm', 'Cloud9am',
        'Cloud3pm', 'Temp9am', 'Temp3pm']] = df[['MinTemp', 'MaxTemp', 'Rainfall', 'Evaporation', 'Sunshine',
                                                 'WindGustSpeed', 'WindSpeed9am', 'WindSpeed3pm', 'Humidity9am',
                                                 'Humidity3pm', 'Pressure9am',
                                                 'Pressure3pm', 'Cloud9am', 'Cloud3pm', 'Temp9am', 'Temp3pm']].astype(
        'float64')

    df[['Location', 'WindGustDir', 'WindDir9am', 'WindDir3pm', 'RainToday']] = df[
        ['Location', 'WindGustDir', 'WindDir9am',
         'WindDir3pm', 'RainToday']].astype('object')
    df['Date'] = df[['Date']].astype('datetime64')

    # print(df.info())

    df_procesed = process(df)

    # process dataset
    result = model.predict_proba(df_procesed)

    # returning of data
    predx = ['%.3f' % elem for elem in result[0]]
    preds_concat = pd.concat([pd.Series(targets), pd.Series(predx)], axis=1)
    preds = pd.DataFrame(data=preds_concat)
    preds.columns = ["class", "probability"]
    return preds.reset_index(drop=True)


def launch_task(
        location,
        minTemp,
        maxTemp,
        rainFall,
        evaporation,
        sunshine,
        windGustDir,
        windGustSpeed,
        windDir9am,
        windDir3pm,
        windSpeed9am,
        windSpeed3pm,
        humidity9am,
        humidity3pm,
        pressure9am,
        pressure3pm,
        cloud9am,
        cloud3pm,
        temp9am,
        temp3pm,
        rainToday,
        api='v1.0'):
    """Service function. Returns error if api version is not 1.0.
    Generally needed for supporting of api extensions"""
    current_date = date.today()
    curr_date = current_date.strftime('%Y-%m-%d')  # '2021-08-16'

    pred_model = get_pred(curr_date, location, minTemp, maxTemp, rainFall, evaporation, sunshine,
                          windGustDir, windGustSpeed, windDir9am, windDir3pm, windSpeed9am,
                          windSpeed3pm, humidity9am, humidity3pm, pressure9am, pressure3pm, cloud9am,
                          cloud3pm, temp9am, temp3pm, rainToday)

    if api == 'v1.0':
        res_dict = {'result': json.loads(pd.DataFrame(pred_model).to_json(orient='records'))}
        return res_dict
    else:
        res_dict = {'error': 'API doesnt exist'}
        return res_dict


@app.route('/weather/api/v1.0/getpred', methods=['GET'])
def get_task():
    result = launch_task(request.args.get('location'),
                         request.args.get('minTemp'),
                         request.args.get('maxTemp'),
                         request.args.get('rainFall'),
                         request.args.get('evaporation'),
                         request.args.get('sunshine'),
                         request.args.get('windGustDir'),
                         request.args.get('windGustSpeed'),
                         request.args.get('windDir9am'),
                         request.args.get('windDir3pm'),
                         request.args.get('windSpeed9am'),
                         request.args.get('windSpeed3pm'),
                         request.args.get('humidity9am'),
                         request.args.get('humidity3pm'),
                         request.args.get('pressure9am'),
                         request.args.get('pressure3pm'),
                         request.args.get('cloud9am'),
                         request.args.get('cloud3pm'),
                         request.args.get('temp9am'),
                         request.args.get('temp3pm'),
                         request.args.get('rainToday')
                         )

    return make_response(jsonify(result), 200)


@app.route('/weather/api/v1.0/index', methods=['GET', 'POST'])
def index():
    current_date = date.today()
    formatted_date = current_date.strftime('%d %b %Y')

    if request.method == 'POST':
        req = request.form
        location = req.get("location")
        minTemp = req.get("minTemp")
        maxTemp = req.get("maxTemp")
        rainFall = req.get("rainFall")
        evaporation = req.get("evaporation")
        sunshine = req.get("sunshine")
        windGustDir = req.get("windGustDir")
        windGustSpeed = req.get("windGustSpeed")
        windDir9am = req.get("windDir9am")
        windDir3pm = req.get("windDir3pm")
        windSpeed9am = req.get("windSpeed9am")
        windSpeed3pm = req.get("windSpeed3pm")
        humidity9am = req.get("humidity9am")
        humidity3pm = req.get("humidity3pm")
        pressure9am = req.get("pressure9am")
        pressure3pm = req.get("pressure3pm")
        cloud9am = req.get("cloud9am")
        cloud3pm = req.get("cloud3pm")
        temp9am = req.get("temp9am")
        temp3pm = req.get("temp3pm")
        rainToday = req.get("rainToday")
        print(f'request={req}')
        param_row = f'?location={location}&minTemp={minTemp}&maxTemp={maxTemp}&rainFall={rainFall}&' \
                    f'evaporation={evaporation}&sunshine={sunshine}&windGustDir={windGustDir}&' \
                    f'windGustSpeed={windGustSpeed}&windDir9am={windDir9am}&windDir3pm={windDir3pm}&' \
                    f'windSpeed9am={windSpeed9am}&windSpeed3pm={windSpeed3pm}&humidity9am={humidity9am}&' \
                    f'humidity3pm={humidity3pm}&pressure9am={pressure9am}&pressure3pm={pressure3pm}&' \
                    f'cloud9am={cloud9am}&cloud3pm={cloud3pm}&temp9am={temp9am}&temp3pm={temp3pm}&rainToday={rainToday}'

        return redirect('/weather/api/v1.0/getpred' + param_row)
    return render_template('index.html', current_date=formatted_date)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'code': 'PAGE_NOT_FOUND'}), 404)


@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'code': 'INTERNAL_SERVER_ERROR'}), 500)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
