import os
from flask import Flask, request, render_template, redirect
import sqlite3
from flask import g
from FileAnalysis import prop_get
from FileAnalysis import db_data_prop

stuff_name = 'page_user'
db_file = prop_get.this_dir + os.sep + 'SisTmp/' + 'db_info_' + stuff_name

DATABASE = db_file

p_db = db_data_prop.OperaDataBase(stuff_name)
app = Flask(__name__)
# Create app
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-random-salt'


class operate_user(object):
    def __init__(self, name=None, passwd=None, message=None):
        self.name = name
        self.passwd = passwd
        self.message = message

    def get_db_info(self, name=None):
        """get name info from db"""
        if not name:
            name = self.name
        db_info = p_db.db_query(**{name:[]})
        return db_info[0]

    def get_db_all_name(self):
        """get all name from db name"""
        exc_sql = """SELECT request_id FROM {} """.format(p_db.get_table_name())
        sql_info = p_db.sql_code_zip(exc_sql)
        return sql_info['code_group']

    def check_name_in_db(self, name=None, passwd=None):
        """check user passwd if equal db item code"""
        if not name:
            name = self.name
        if name in self.get_db_all_name():
            return passwd == op_user.get_db_info(name)[3]

    @app.teardown_appcontext
    def close_connection(self, exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    def _if_db_exist(self):
        pass

    def _insert_db(self):
        pass

    def _update_login_times(self):
        pass


@app.route('/')
def start_page():
    if render_template('index.html'):
        return render_template('index.html')
    else:
        return '127.0.0.1:38080'


@app.route('/__webpack_hmr')
def npm():
    return redirect('http://localhost:5000/__webpack_hmr')


def do_the_login():
    return "PASS"


def show_the_login_form():
    return "PLEASE INPUT NAME AND PASSWD"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()


if __name__ == '__main__':
    print("db name:{}".format(p_db.get_table_name()))
    """["request_id",  user_name
        "times": login_times 
        "message": email
        "code":  passwd]"""
    # p_db.db_insert(info={"Frank": ["0", "Frank@123.com", "123456"]})
    op_user = operate_user(name='Frank', passwd='123456')
    print('123456' in op_user.get_db_info('Lucy'))
    print('Lucy' in op_user.get_db_all_name())
    print(op_user.check_name_in_db(name='Jack', passwd='123456'))
    print(op_user.check_name_in_db(passwd='Frank'))
