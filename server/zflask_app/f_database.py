import sqlite3
import os
from FileAnalysis import prop_get
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

this_dir = os.path.dirname(os.path.realpath(__file__))

db_file_path = this_dir + os.sep + '../tmp/' + 'db_info_flask.db'
print("db file path: {}".format(db_file_path))
sql_cxn = sqlite3.connect(db_file_path)
# sqlite:////tmp/test.db
engine = create_engine('sqlite:////../tmp/db_info_flask.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import f_models
    Base.metadata.create_all(bind=engine)