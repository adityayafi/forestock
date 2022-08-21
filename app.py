# from prettytable import PrettyTable
import os
from tkinter.tix import Tree
from flask import Flask, flash, jsonify, render_template, request, url_for, redirect, session
# from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import mysql.connector
from werkzeug.utils import secure_filename
import pickle

# import matplotlib
# matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# from pmdarima import auto_arima
import warnings 
warnings.filterwarnings('ignore')
from statsmodels.tsa.arima_model import ARIMA



conn = mysql.connector.connect(
    host="localhost", 
    user="root", 
    password="", 
    database="forecast", 
    autocommit='true')

app = Flask(__name__)
app.secret_key = "skripshit"
app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'forecast'
# mysql = MySQL(app)



@app.route('/register.html', methods=['POST', 'GET'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else :
        fname = request.form['firstname']
        lname = request.form['lastname']
        name = fname+" "+lname
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        confpass = request.form['confpass'].encode('utf-8')

        if password == confpass:
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

            query = "INSERT INTO tb_user (nama,email,password) VALUES (%s,%s,%s)"
            value = (name, email, hash_password)
            cur = conn.cursor()
            cur.execute(query, value)
            # flash('Registered Successfully! \n', 'success')
            return redirect(url_for('login'))
        else :
            print("Password is not same as above! \n")

@app.route('/login.html', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        query = "SELECT * FROM tb_user WHERE email=%s"
        val = (email,)
        # curl.execute("SELECT * FROM tb_user WHERE email=%s",(email,))
        cur = conn.cursor()
        cur.execute(query, val)
        user = cur.fetchone()
        # curl.close()

        if user is not None and len(user) > 0 and user[4] == 'active' :
            if bcrypt.hashpw(password, user[3].encode('utf-8')) == user[3].encode('utf-8'):
                session['nama'] = user [1]
                session['email'] = user[2]
                if user[5] == "admin":
                    return redirect(url_for('admin'))
                else :
                    return redirect(url_for('main'))
            else :
                flash("Gagal, Email dan Password Tidak Cocok")
                return redirect(url_for('login'))
        else :
            flash("Gagal, User Tidak Ditemukan")
            return redirect(url_for('login'))
    else: 
        return render_template("login.html")

@app.route("/inputemiten", methods=['POST', 'GET'])
def inputemiten():
    if request.method == 'GET':
        return render_template('emiten.html')
    else:
        code = request.form['stockscode']
        name = request.form['stocksname']
        
        query = "INSERT INTO tb_emiten (emt_code,emt_name) VALUES (%s,%s)"
        val = (code, name)
        cur = conn.cursor()
        cur.execute (query, val)
        
        return redirect(url_for('emiten'))

@app.route("/emiten")
def emiten():
    query = "SELECT * FROM tb_emiten"
    cur = conn.cursor()
    cur.execute(query)
    emiten = cur.fetchall()    
    return render_template('admin/pages/emiten.html', data = emiten)

# @app.route("/ajaxemt", methods=['POST', 'GET'])
# def ajaxemt():
    
#     if request.method == 'POST':
#         emt_id = request.form['emt_id']
#     sql = "SELECT * FROM tb_emiten WHERE emt_id = %s"
#     val = (emt_id)
#     cur = conn.cursor()
#     cur.execute(sql, val)
#     emtdata = cur.fetchall()
#     return jsonify({'htmlresponse' : render_template('responsemodal.html', emtdata = emtdata)})

### ADMIN : User Page ###

@app.route("/user")
def user():
    # if session == True :
        query = "SELECT * FROM tb_user WHERE level != 'admin'"
        cur = conn.cursor()
        cur.execute(query)
        user = cur.fetchall()    
        return render_template('admin/pages/user.html', data = user)
    
    # else : 
    #     return render_template('login.html')

@app.route("/status", methods=['POST','GET'])
def status():
    query  = "SELECT * FROM tb_user WHERE user_id = %s"
    val = request.args.get('userid')
    cur = conn.cursor()
    cur.execute(query, (val,))
    user = cur.fetchone()
    # print(user[0])
    # return "test"

    if user[4] == 'active' :
        sql = "UPDATE tb_user SET status = 'inactive' WHERE user_id = %s"
        cur.execute(sql, (user[0],))
        
        return redirect(url_for('user'))
    else :
        sql = "UPDATE tb_user SET status = 'active' WHERE user_id = %s"
        cur.execute(sql,  (user[0],))
        return redirect(url_for('user'))


###
@app.route("/inputprice")
def iprice():
    # if session == True :
        sql = "SELECT * FROM tb_emiten"
        cur = conn.cursor()
        cur.execute(sql)
        stock = cur.fetchall()
        return render_template('admin/pages/iprice.html', data = stock)

    # else : 
    #     return render_template('login.html')

@app.route("/upload", methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        emt_id = request.form['emiten']
        f = request.files['file']
        filename = secure_filename(f.filename)
        name = f.filename
        pathh = "D:\\Python\\Forecast\\uploads\\"+name
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        sql = "INSERT INTO tb_uploads (emt_id,filename,path) VALUES (%s,%s,%s)"
        val = (emt_id, name, pathh)
        cur = conn.cursor()
        cur.execute(sql, val)
        # print(pathh)
        return redirect(url_for('iprice'))
    else :
        return render_template('admin/pages/iprice.html')

@app.route("/stock")
def stock():
    sql = "SELECT * FROM tb_emiten"
    cur = conn.cursor()
    cur.execute(sql)
    stock = cur.fetchall()
    return render_template('stock.html', data = stock)

@app.route("/test")
def test():
    # print ("test", file=sys.stderr)
    return "Check your console"

@app.route("/admin", methods=['POST', 'GET'])
def admin():
    return render_template('admin/index.html')

@app.route("/")
def main():
    # if session == True :
        return render_template('index.html')
    # else :
    #     return render_template('login.html')

@app.route("/index.html")
def index():
    # if session == True :  
        return render_template('index.html')
    # else :
    #     return render_template('login.html')

@app.route("/buttons")
def buttons():
    return render_template('buttons.html')

@app.route("/forgot-password.html")
def forgotpass():
    return render_template('forgot-password.html')

@app.route("/charts.html")
def charts():
    return render_template('charts.html')     

@app.route("/ua")
def ua():
    return render_template('utilities-animation.html')

@app.route("/ub")
def ub():
    return render_template('utilities-border.html')

@app.route("/uc")
def uc():
    return render_template('utilities-color.html')                          

@app.route("/huploads", methods=['POST','GET'])
def huploads():
    if request.method == 'GET':
        sql = "SELECT * FROM tb_uploads WHERE emt_id=%s"
        emtid= request.args.get('emtid')
        val = (emtid)
        cur = conn.cursor()
        cur.execute (sql, (val,))
        emt = cur.fetchall()
        return render_template('admin/pages/huploads.html', data = emt)
    else:
        return redirect(url_for('emiten'))

@app.route("/blank.html")
def blank():
    return render_template('blank.html')

@app.route("/conf_arima")
def confarima():
    sql = "SELECT * FROM tb_emiten"
    cur = conn.cursor()
    cur.execute(sql)
    arima = cur.fetchall()
    i = 0

    if i == 0:
        sql1 = "SELECT * FROM tb_uploads"
        cur = conn.cursor()
        cur.execute(sql1)
        dataset = cur.fetchall()

    return render_template('admin/pages/arima.html', data = arima, data1 = dataset)

@app.route("/addconf", methods=['POST', 'GET'])
def addconf():
    if request.method == 'POST' :
        emt_id = request.form['emiten']
        uploads_id = request.form['dataset']
        p = request.form['p']
        d = request.form['d']
        q = request.form['q']

        # print(emt_id, uploads_id, p, d, q)
        sql = "INSERT INTO tb_arima (emt_id, uploads_id, p, d, q) VALUES (%s,%s,%s,%s,%s)"
        val = (emt_id, uploads_id, p, d, q)
        cur = conn.cursor()
        cur.execute(sql, val)


        return redirect(url_for('confarima'))
    else :
        return redirect(url_for('confarima'))

@app.route("/hprice", methods=['POST', 'GET'])
def hprice():
    sql = "SELECT * FROM tb_emiten"
    cur = conn.cursor()
    cur.execute(sql)
    stock = cur.fetchall()

    if request.method == 'POST' :
        emt_id = request.form['emiten']
        sql = "SELECT * FROM tb_uploads WHERE emt_id = %s"
        val = (emt_id)
        cur.execute (sql, (val,))
        emt = cur.fetchone()

        # d = open(emt[2], "r")
        # d = d.readlines()
        # h1 = d[0]
        # h1 = h1.split(',')
        # t = PrettyTable()
        print(emt[2])
        # return render_template('admin/pages/hprice.html')
        with open(emt[3]) as file :
            return render_template('admin/pages/hprice.html', data = stock, data1 = file)         
    else :
        return render_template('admin/pages/hprice.html', data = stock)


@app.route("/history", methods=['POST', 'GET'])
def history():

    if request.method == 'GET':
        sql = "SELECT * FROM tb_uploads WHERE emt_id=%s"
        emtid= request.args.get('emtid')
        val = (emtid)
        cur = conn.cursor()
        cur.execute(sql, (val,))
        emt = cur.fetchone()

        with open(emt[3]) as file:
            return render_template('history.html', data = file)
    else:
        return redirect(url_for('stock'))

@app.route("/forecast", methods=['POST','GET'])
def forecast():
    if request.method == 'GET':
        sql = "SELECT tb_emiten.emt_name, tb_uploads.filename, tb_uploads.path, tb_arima.p, tb_arima.d, tb_arima.q FROM tb_emiten, tb_uploads, tb_arima WHERE tb_emiten.emt_id=tb_uploads.emt_id AND tb_emiten.emt_id=tb_arima.emt_id AND tb_emiten.emt_id=%s"
        emtid = request.args.get('emtid')
        val = (emtid)
        cur = conn.cursor()
        cur.execute(sql, (val,))
        emt = cur.fetchone()
        name = emt[0]
        filename = emt[1]
        path = emt[2]
        p = emt[3]
        d = emt[4]
        q = emt[5]

        # print(p,d,q)

        ###READ DATA###
        df = pd.read_csv(path, index_col='Date', parse_dates=True)
        df = df.dropna()
        # print('Shape of Data', df.shape)
        # df.head()
        # df['Close'].plot(figsize=(12,5))

        ###SPLIT DATA
        train = df.iloc[:-50]
        test = df.iloc[-50:]

        model = ARIMA(train['Close'], order=(p,d,q))
        fitted = model.fit()
        fitted.summary()

        start = len(train)
        end = len(train)+len(test)-1
        if d == 0:
            pred = fitted.predict(start=start, end=end)
        else:
            pred = fitted.predict(start=start, end=end, typ='levels')
        print(pred)

        # Forecast using 95% confidence interval
        fc, se, conf = fitted.forecast(50, alpha=0.05)

        # Make as pandas series
        fc_series = pd.Series(fc, index=test.index)
        lower_series = pd.Series(conf[:, 0], index=test.index)
        upper_series = pd.Series(conf[:, 1], index=test.index)

        # Plot
        plt.figure(figsize=(12,5), dpi=100)
        plt.plot(train['Close'], label='training')
        plt.plot(test['Close'], label='actual')
        plt.plot(fc_series, label='forecast')
        plt.fill_between(lower_series.index, lower_series, upper_series, color='k', alpha=.15)
        plt.title('Forecast vs Actuals : '+ name)
        plt.legend(loc='upper left', fontsize=8)
        # plt.show()
        return render_template('forecast.html', data = pred)
    else:
        return render_template('forecast.html')
    






                    
         
@app.route("/tables.html")
def tables():
    return render_template('tables.html')            
if __name__ == "__main__":
    app.run(debug = True)

