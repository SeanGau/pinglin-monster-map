import flask, os, json, hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from os import walk
from sassutils.wsgi import SassMiddleware

app = flask.Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['GLOBAL_TITLE'] = "坪林尋怪地圖"
app.jinja_env.globals['GLOBAL_VERSION'] = datetime.now().timestamp()
db = SQLAlchemy(app)

app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'app': {
        'sass_path': 'static/sass',
        'css_path': 'static/css',
        'strip_extension': True,
    }
})

def gethashed(data):
	data = data+app.config['SECRET_KEY']
	s = hashlib.sha256()
	s.update(data.encode("UTF-8"))
	h = s.hexdigest()
	return h

def alert(message, redir): #alert then redirect
	return f'''<script type="text/javascript">
						alert("{message}");
						window.location.href = "{redir}";
						</script>'''

@app.route('/')
def index():
    login_data = flask.session.get('login_data', None)
    if login_data is not None:
        login_data = json.loads(login_data)
    return flask.render_template('index.html', login_data = login_data)

@app.route('/portal', methods = ['GET', 'POST'])
def portal():
    login_data = flask.session.get('login_data', None)
    if login_data is None:
        return alert('尚未登入！', flask.url_for('login'))
    login_data = json.loads(login_data)

    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        if _data['email'] != login_data['email']:
            return "error"
        else:
            db.session.begin()
            if len(_data['password'])>=8 and len(_data['password'])<=20:
                db.session.execute(f"UPDATE public.users SET password='{gethashed(_data['password'])}' WHERE email='{_data['email']}'")
            if len(_data['username'])>0 and len(_data['username'])<=12:
                db.session.execute(f"UPDATE public.users SET username='{_data['username']}' WHERE email='{_data['email']}'")
                login_data['username'] = _data['username']
                flask.session['login_data'] = json.dumps(login_data)
            db.session.commit()
            return "ok"
    else:        
        return flask.render_template('portal.html', login_data = login_data)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        _data = flask.request.form
        cb = db.session.execute(f"SELECT * FROM public.users WHERE email='{_data['email']}' AND password='{gethashed(_data['password'])}'")
        cb = cb.all()
        if len(cb) > 0:
            cb_data = dict(cb[0])
            flask.session.permanent = False
            flask.session['login_data'] = json.dumps(cb_data)
            return alert("登入成功", "/")
        else:
            return alert("帳號或密碼錯誤！", flask.url_for('login'))
    else:
        return flask.render_template('login.html')

@app.route('/logout')
def logout():
    flask.session.clear()
    return alert("您以登出！", "/")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        cb = db.session.execute(f"SELECT * FROM public.users WHERE email='{_data['email']}'")
        if len(cb.all())==0:
            return "此帳號已被註冊！"
        elif len(_data['username'])>0 and len(_data['username'])<=12 and len(_data['password'])>=8 and len(_data['password'])<=20:
            cb = db.session.execute(f"INSERT INTO public.users (username,email,password) VALUES('{_data['username']}','{_data['email']}','{gethashed(_data['password'])}')")
            db.session.commit()
            return "ok"
        else:
            return "註冊失敗，請聯絡管理員"
    else:
        return flask.render_template('register.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000, debug=True)