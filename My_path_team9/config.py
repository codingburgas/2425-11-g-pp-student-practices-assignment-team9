import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://CloudSAd5c2a932:Viktoriq21@mypath.database.windows.net/mypath?driver=ODBC+Driver+17+for+SQL+Server'


    SQLALCHEMY_TRACK_MODIFICATIONS = False
