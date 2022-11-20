from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
from flask_mail import Mail, Message
import re
app = Flask(__name__)
mail = Mail(app) # instantiate the mail class
   
# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'karpagamboothanathan@gmail.com'
app.config['MAIL_PASSWORD'] = 'nmydiidhksvvojid'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=hnl10309;PWD=4q2SvdOKme6RC7Zr",'','')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST'and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        stmt = ibm_db.prepare(conn,'SELECT * FROM donor WHERE username = ? AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)        
        ibm_db.execute(stmt)
        account = ibm_db.fetch_tuple(stmt)
        stmt = ibm_db.prepare(conn,'SELECT * FROM recipient WHERE username = ? AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)        
        ibm_db.execute(stmt)
        account = ibm_db.fetch_tuple(stmt)
        if account:
            session['loggedin'] = True
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', a = msg)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile',methods=["POST","GET"])
def profile():
    if 'username' in session:
        id = session['username']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM donor WHERE username = ?')
        ibm_db.bind_param(stmt, 1, id)    
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)   

        stmt = ibm_db.prepare(conn, 'SELECT * FROM recipient WHERE username = ?')
        ibm_db.bind_param(stmt, 1, id)    
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)        
        return render_template('profile.html', username=acc[1],age=acc[2],bloodgroup=acc[3],gender=acc[4],phone=acc[5],address=acc[6],email=acc[7],passsword=acc[8],confirmpassword=acc[9],height=acc[10],weight=acc[11])
    return render_template('profile.html')




@app.route('/send_email', methods = ['POST'])
def send():     
    if 'bloodgroup' in request.form:
        type = request.form['bloodgroup']
        remail=request.form['email1']
        stmt = ibm_db.prepare(conn, 'SELECT email FROM donor WHERE bloodgroup = ?')
        ibm_db.bind_param(stmt,1,type)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)
        
        mails = []
        while acc != False:
            mails.append(acc[0])
            acc = ibm_db.fetch_tuple(stmt)
        msg = Message('Blood Request', sender='karpagamboothanathan@gmail.com', recipients=mails)
        msg.body = "I need " + request.form['bloodgroup'] + " Blood(plasma).  "  + remail + " - contact this email to donate"
        mail.send(msg)
        return render_template('display.html', state="SENT")
    
    return 'Please Provide Blood in Form'

@app.route('/display',methods=["POST","GET"])
def display():
    if request.method == 'POST' :
        alert = ''
        if 'name' in session:
            id = session['username']
            bloodgroup = request.form['bloodgroup']
            sqlselect = "SELECT * FROM recipient WHERE bloodgroup = ? order by id asc"
            stmt = ibm_db.prepare(conn,sqlselect)
            ibm_db.bind_param(stmt, 1, bloodgroup)
            ibm_db.execute(stmt)
            acc = ibm_db.fetch_tuple(stmt)  
            
        return render_template('display.html',m=alert)
    return render_template('display.html')
      
    
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        age = request.form['age']
        bloodgroup = request.form['bloodgroup']
        lastdonatedate= request.form['lastdonatedate']
        gender = request.form['gender']
        phone= request.form['phone']
        address= request.form['address']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        height= request.form['height']
        weight = request.form['weight']
        sql = "SELECT * FROM donor WHERE username = ? "
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msgg = Message(
                'Hello',
                sender ='karpagamboothanathangmail.com',
                recipients = [email]
               )
        msgg.body = ' Thank you...You are successfully registered in plasma donor application.'
        mail.send(msgg) 
         
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not username:
            msg = 'Please fill out the form !'
        else:
            insert_sql = "INSERT INTO donor(username,age,bloodgroup,lastdonatedate,gender,phone,address,email,password,confirmpassword,height,weight) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"
            stmt = ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(stmt, 1, username )
            ibm_db.bind_param(stmt, 2, age)
            ibm_db.bind_param(stmt, 3, bloodgroup)
            ibm_db.bind_param(stmt, 4, lastdonatedate )
            ibm_db.bind_param(stmt, 5, gender )
            ibm_db.bind_param(stmt, 6, phone )
            ibm_db.bind_param(stmt, 7, address )
            ibm_db.bind_param(stmt, 8, email )
            ibm_db.bind_param(stmt, 9, password )
            ibm_db.bind_param(stmt, 10, confirmpassword )
            ibm_db.bind_param(stmt, 11, height)
            ibm_db.bind_param(stmt, 12, weight )
            ibm_db.execute(stmt)
            msg = 'You have successfully registered !'
    return render_template('donor.html', msg = msg)

@app.route('/registers', methods =['GET', 'POST'])
def registers():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        age = request.form['age']
        bloodgroup = request.form['bloodgroup']
        gender = request.form['gender']
        phone= request.form['phone']
        address= request.form['address']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        height= request.form['height']
        weight = request.form['weight']
        sql = "SELECT * FROM recipient WHERE username = ? "
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msgg = Message(
                'Hello',
                sender ='karpagamboothanathangmail.com',
                recipients = [email]
               )
        msgg.body = ' Thank you...You are successfully registered in plasma donor application.  '
        mail.send(msgg)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not username:
            msg = 'Please fill out the form !'
        else:
            insert_sql = "INSERT INTO recipient(username,age,bloodgroup,gender,phone,address,email,password,confirmpassword,height,weight) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            stmt = ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(stmt, 1, username )
            ibm_db.bind_param(stmt, 2, age)
            ibm_db.bind_param(stmt, 3, bloodgroup)
            ibm_db.bind_param(stmt, 4, gender )
            ibm_db.bind_param(stmt, 5, phone )
            ibm_db.bind_param(stmt, 6, address )
            ibm_db.bind_param(stmt, 7, email )
            ibm_db.bind_param(stmt, 8, password )
            ibm_db.bind_param(stmt, 9, confirmpassword )
            ibm_db.bind_param(stmt, 10, height)
            ibm_db.bind_param(stmt, 11, weight )
            ibm_db.execute(stmt)
            msg = 'You have successfully registered !'     
    return render_template('recipient.html', msg = msg)

if __name__ == '__main__':
    app.run(debug = True)

