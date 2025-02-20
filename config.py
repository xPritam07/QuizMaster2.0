from dotenv import load_dotenv
import os
load_dotenv()

from quiz import app

app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATION']=os.getenv('SQLALCHEMY_TRACK_MODIFICATION')