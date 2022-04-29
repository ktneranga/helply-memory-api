from flask import Flask, request, jsonify
import joblib
from keras.layers import Dense,Dropout
from keras.models import Sequential
import keras.backend as K

#creating the tables using sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import datetime

#serialize and deserialize data
from flask_marshmallow import Marshmallow

scaler_x = joblib.load('scaler_x.pkl')
scaler_y = joblib.load('scaler_y.pkl')

app=Flask(__name__)

def load_dyslexia_model():

    K.clear_session()
    model=Sequential() #model is an empty NN
    #1st hidden layer (dense type-fully connected)
    model.add(Dense(64,input_dim=7,activation='relu'))
    model.add(Dropout(0.5))
    #2nd Hidden layer
    model.add(Dense(128,activation='relu',kernel_initializer='normal'))
    model.add(Dropout(0.5))
    model.add(Dense(64,activation='relu',kernel_initializer='normal'))
    model.add(Dropout(0.5))
    model.add(Dense(7,activation='relu',kernel_initializer='normal'))
    #final layer
    model.add(Dense(1,input_dim=7,activation='linear'))

    model.compile(loss='mse',optimizer='adam')
    model.load_weights('model-569.model')
    
    return model

@app.route('/get_level', methods=['POST','GET'])

def get_level():

    # User_json=request.json
    Q1 =int(request.args.get('q1'))
    Q2 =int(request.args.get('q2'))
    Q3 =int(request.args.get('q3'))
    Q4 =int(request.args.get('q4'))
    Q5 =int(request.args.get('q5'))
    Q6 =int(request.args.get('q6'))
    TD =float(request.args.get('time'))

    test_data=[Q1,Q2,Q3,Q4,Q5,Q6,TD]
    print(test_data)
    
    model = load_dyslexia_model()
    result=model.predict([test_data])
    result=scaler_y.inverse_transform(result)[0][0]

    results=[{"level":float(result)}]
    return (jsonify(results=results))

# userpass = 'mysql://root:''@'
# basedir = '127.0.0.1'
# dbname = '/helply'
# socket = '?unix_socket=/opt/lampp/var/mysql/mysql.sock'
# dbname = dbname + socket

# app.config['SQLALCHEMY_DATABASE_URI'] = userpass + basedir + dbname
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql5488870:UylH12yrME@sql5.freesqldatabase.com/sql5488870'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#DB Connection

db = SQLAlchemy(app)
#crate a object of marshmallow
ma = Marshmallow(app)

#creating the table
class MemoryResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    age = db.Column(db.String(10))
    game_level = db.Column(db.String(50))
    time_duration = db.Column(db.Float())
    result = db.Column(db.String(20))
    date = db.Column(db.DateTime, default = datetime.datetime.now)

    def __init__(self, name, age, game_level, time_duration, result):
        self.name = name
        self.age = age
        self.game_level = game_level
        self.time_duration = time_duration
        self.result = result

#for serializing and deserializing , create the schema
#create Results schema
class ResultsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'age', 'game_level', 'time_duration', 'result', 'date') # fields to serialize 

result_schema = ResultsSchema()               
results_schema = ResultsSchema(many=True)

#add results => POST method
@app.route('/add', methods = ['POST'])
def add_result():
    # title = request.json['title']
    # body = request.json['body']
    name = request.json['name']
    age = request.json['age']
    game_level = request.json['game_level']
    time_duration = request.json['time_duration']
    result = request.json['result']

    #object of class table
    results = MemoryResults(name, age, game_level, time_duration, result)
    #add to the db
    db.session.add(results)
    #commit to the db
    db.session.commit()
    return result_schema.jsonify(results)

#run the flask file
if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
