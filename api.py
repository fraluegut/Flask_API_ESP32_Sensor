from flask import Flask, request, jsonify
from flask_restplus import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import datetime

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'DATABASE'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


db = SQLAlchemy(app)
ma = Marshmallow(app)

parser_task = reqparse.RequestParser()
parser_task.add_argument('title', type=str, required=True)
parser_task.add_argument('description', type=str, required=False)

parser_sensor = reqparse.RequestParser()
parser_sensor.add_argument('lux', type=float, required=False)
parser_sensor.add_argument('temperature', type=float, required=False)
parser_sensor.add_argument('pressure', type=float, required=False)
parser_sensor.add_argument('altitude', type=float, required=False)
parser_sensor.add_argument('humidity', type=float, required=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), unique=True)
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description


# db.create_all()
class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lux = db.Column(db.Float, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    pressure = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, lux, temperature, pressure, altitude, humidity, registered):
        self.lux = lux
        self.temperature = temperature
        self.pressure = pressure
        self.altitude = altitude
        self.humidity = humidity
        self.registered = registered

class SensorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'lux', 'temperature', 'pressure', 'altitude', 'humidity', 'registered')

sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)

@api.route('/tasks', methods=['POST', 'GET'])
class Tasks(Resource):
    @api.expect(parser_task, validate=True)
    def post(self):
        db.session.close()
        data = parser_task.parse_args()
        title = str(data.get('title'))
        description = str(data.get('description'))

        new_task = Task(title, description)
        db.session.add(new_task)
        db.session.commit()
        return task_schema.jsonify(new_task)

    def get(self):
        all_tasks = Task.query.all()
        result = tasks_schema.dump(all_tasks)
        return jsonify(result)

@api.route('/sensor', methods=['POST', 'GET'])
class Sensors(Resource):
    @api.expect(parser_sensor, validate=True)
    def post(self):
        data = parser_sensor.parse_args()
        lux = float(data.get('lux'))
        temperature = float(data.get('temperature'))
        pressure = float(data.get('pressure'))
        altitude = float(data.get('altitude'))
        humidity = float(data.get('humidity'))
        registered = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        new_sensor = Sensor(lux, temperature, pressure, altitude, humidity, registered)
        db.session.add(new_sensor)
        db.session.commit()
        # db.session.close()
        return sensor_schema.jsonify(new_sensor)

    def get(self):
        all_sensors = Sensor.query.all()
        result = sensors_schema.dump(all_sensors)
        # db.session.close()
        return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
