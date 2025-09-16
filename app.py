from flask import Flask, request, redirect, url_for, render_template, make_response
import os, flask_login
import flask
from werkzeug.utils import secure_filename
from datetime import timedelta
from sh import bash



app = Flask(__name__)
app.secret_key = 'asdasd'  # Change this!
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)  # 设置session超时为30分钟


login_manager = flask_login.LoginManager() # 初始化一个 LoginManager 类对象

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'

login_manager.init_app(app) # 配置该对象

users = {'syspfm_up': {'password': '123456'}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@app.route('/mini/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    email = flask.request.form['email']
    if email in users and flask.request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        resp = make_response("Cookie 已设置")
        # 带过期时间（24小时）
        # resp.set_cookie('session', max_age=100)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('login.html', error=True)


# 限制文件上传类型，Size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

UPLOAD_FOLDER = '/opt/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/mini/index')
@flask_login.login_required
def index():
    return flask.render_template('index.html', error=True)

@app.route('/mini/upload', methods=['GET','POST'])
@flask_login.login_required
def upload_file():
    if flask.request.method == 'GET':
        return render_template('index.html')
    
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully!'
    
    return redirect(request.url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000,debug=True)





