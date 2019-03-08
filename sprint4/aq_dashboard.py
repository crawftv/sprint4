from flask import Flask, request, render_template
import requests
import openaq

from flask_sqlalchemy import SQLAlchemy
from .models import DB, Record

api=openaq.OpenAQ()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB.init_app(app)
    
    
    @app.route('/')
    def root():
        status, body = api.measurements(city="Los Angeles",parameter = 'pm25')
        la_25 = []
        for i in range(0,len(body['results'])):
            la_25.append((body['results'][i]['date']['utc'],body['results'][i]['value']))
        

        risks = DB.session.query(Record).filter(Record.value>10).all()
        records = Record.query.all()
        return render_template("root.html",risks=risks,records=records,la_25=la_25)
    
    @app.route('/refresh',methods = ['POST','GET'])
    def refresh():
        DB.drop_all()
        DB.create_all()
        status, body = api.measurements(city="Los Angeles",parameter = 'pm25')

        
        if request.method == 'GET':
            for i in range(0,len(body['results'])):
                DB.session.add(
                    Record(
                        datetime = body['results'][i]['date']['utc'],
                        value = body['results'][i]['value']
                        )
                )
        DB.session.commit()
        records = Record.query.all()
        return render_template('refresh1.html',records = records)

    @app.route('/dashboard',methods=['GET'])
    def dashboard():
        risks = DB.session.query(Record).filter(Record.value>10).all()
        records = Record.query.all()
        return render_template("dashboard.html",risks=risks,records=records)
    return app
