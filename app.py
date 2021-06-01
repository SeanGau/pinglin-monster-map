import flask, json, hashlib, string, random
from datetime import datetime
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware
#import pypugjs

app = flask.Flask(__name__)
app.config.from_object('config')
#app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
app.jinja_env.globals['GLOBAL_TITLE'] = "坪林尋怪"
app.jinja_env.globals['GLOBAL_VERSION'] = datetime.now().timestamp()
db = SQLAlchemy(app)
mail = Mail(app)

app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'app': {
        'sass_path': 'static/sass',
        'css_path': 'static/css',
        'strip_extension': True,
    }
})
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

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

def send_mail(recevier_array, subject, html_content):
	msg = Message(subject=app.jinja_env.globals['GLOBAL_TITLE']+" - "+subject, recipients=recevier_array, html=html_content)
	mail.send(msg)

#------------------------------------------------------------------------------------------------------------------

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
        login_data['data'] = [
            {
                "name": "醉猴0",
                "slug": "0"
            },
            {
                "name": "醉猴1",
                "slug": "1"
            },
            {
                "name": "醉猴2",
                "slug": "2"
            },
            {
                "name": "醉猴3",
                "slug": "3"
            }
        ]
        return flask.render_template('portal.html', login_data = login_data)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        _data = flask.request.form
        cb = db.session.execute(f"SELECT * FROM public.users WHERE email='{_data['email']}' AND password='{gethashed(_data['password'])}'")
        cb = cb.all()
        if len(cb) > 0:
            cb_data = dict(cb[0])
            session_data = {
                "email": cb_data['email'],
                "username": cb_data['username'],
                "id": cb_data['id']
            }
            flask.session.permanent = False
            flask.session['login_data'] = json.dumps(session_data)
            #send_mail([_data['email']], "login", "<h1>有人登入你的帳號！</h1>")
            return alert("登入成功", "/")
        else:
            return alert("帳號或密碼錯誤！", flask.url_for('login'))
    else:
        return flask.render_template('login.html')

@app.route('/logout')
def logout():
    flask.session.clear()
    return alert("您已登出！", "/")

@app.route('/reset', methods = ['GET', 'POST'])
def reset():
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        cb = db.session.execute(f"SELECT * FROM token_table WHERE token='{_data['token']}'")
        cb = cb.all()
        if len(cb) > 0:
            cb_data = dict(cb[0])
            exp_t = cb_data['token_expire']
            if exp_t.timestamp() > datetime.now().timestamp() and len(_data['password'])>=8 and len(_data['password'])<=20:
                db.session.execute(f"UPDATE public.users SET password='{gethashed(_data['password'])}' WHERE email='{cb_data['email']}'")
                db.session.execute(f"DELETE FROM public.token_table WHERE email='{cb_data['email']}'")
                db.session.commit()
                return "ok"
        return "error"
    else:
        return flask.render_template('reset.html')

@app.route('/forget', methods = ['GET', 'POST'])
def forget():
    if flask.request.method == 'POST':
        _data = flask.request.form
        token = gethashed(str(datetime.now().timestamp())+_data['email'])
        cb = db.session.execute(f"SELECT * FROM public.users WHERE email='{_data['email']}'")
        if len(cb.all())==0:
            return alert("此信箱尚未註冊！", flask.url_for('forget'))
        db.session.execute(f"INSERT INTO public.token_table (email,token,token_expire) VALUES('{_data['email']}','{token}',(NOW() + interval '1 hour'))")
        db.session.commit()
        send_mail([_data['email']],"忘記密碼", f'''
				<div style="font-size: 1.5em; text-align: center;">
				<p>您好，</p>
				<p>坪林巡怪地圖收到<b>重設密碼</b>請求<p>
				<p>請點擊以下連結進行重設</p>
				<p><a href="https://strangepinglin.collective.tw/reset?token={token}" style="padding: 1em; background-color: #666;color: white; border-radius: 5px;">https://strangepinglin.collective.tw/reset?token={token}</a></p>
				<p>若無法點擊，請複製連結貼到​​​您的​​​瀏覽器</p>
				</div>
        ''')
        return alert("請至信箱收信！", flask.url_for('login'))
    else:
        return flask.render_template('forget.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        cb = db.session.execute(f"SELECT * FROM public.users WHERE email='{_data['email']}'")
        if len(cb.all())>0:
            return "此信箱已被註冊！"
        elif _data['email']==flask.session['email_verify']['email'] and _data['code']==flask.session['email_verify']['code'] and len(_data['username'])>0 and len(_data['username'])<=12 and len(_data['password'])>=8 and len(_data['password'])<=20:
            cb = db.session.execute(f"INSERT INTO public.users (username,email,password) VALUES('{_data['username']}','{_data['email']}','{gethashed(_data['password'])}')")
            db.session.commit()
            return "ok"
        else:
            return "註冊失敗，請聯絡管理員"
    else:
        return flask.render_template('register.html')

@app.route('/register/verify', methods = ['GET', 'POST'])
def register_verify():
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        cb = db.session.execute(f"SELECT * FROM public.users WHERE email='{_data['email']}'")
        if len(cb.all())>0:
            return "此信箱已被註冊！"
        else:
            code = get_random_string(10)
            send_mail([_data['email']],"信箱認證", f'''
                    <div style="font-size: 1.5em;">
                    <p>您好，</p>
                    <p>您的信箱認證碼為<a style="padding-left: 1em; color: red; border-radius: 5px;">{code}</a></p>
                    </div>
            ''')
            flask.session.permanent = False
            flask.session['email_verify'] = {
                "email": _data['email'],
                "code": code
            }
            return "ok"
    else:
        _data = {
            "email": flask.request.args.get("email"),
            "code": flask.request.args.get("code")
        }
        if _data != flask.session['email_verify']:
            return "ERROR"
        else:
            return "ok"



@app.route('/monster/<monster_id>')
def monster(monster_id):
    monster_data = {
        "name": "垃圾怪",
        "tag": ["北勢溪","漂流垃圾","人就是共犯"],
        "category": "水域", #人文、過度、水域、山野
        "element": "water", #water, ground, wind, fire
        "founder": "黃玟霖",
        "date": ["2011","5","10"],
        "local": "北勢溪親水吊橋下方",
        "disc": "出現在河流中堆積很多垃圾的地方，像是垃圾袋、寶特瓶，那散發出很臭的味道，因為長期堆滿惡臭的垃圾，人經過的時候都會久留。",
        "strong": "收集垃圾一口吐出",
        "weak": "怕光、怕人",
        "title": "北勢溪的漂流垃圾垃圾",
        "story": "一堆噁心的垃圾在原本清澈的北勢溪漂流著，要問是誰做的？其實就是我們自己。人們因為懶惰，不把垃圾丟入垃圾桶，反而直接丟在河裡，所以才會製造出垃圾怪，垃圾怪一開始會把人們所丟的垃圾收集起來，等收到一定的量，再全部放出來，使河川遭受永久性的污染，就是為了讓河川裡的魚蝦等...受到傷害。垃圾怪喜歡暗暗的地方，而且很怕被人發現，所以都待在河川深處，大家都覺得垃圾怪很可惡，殊不知人類才是罪惡的共犯。"
    }
    login_data = flask.session.get('login_data', None)
    if login_data is not None:
        login_data = json.loads(login_data)
    return flask.render_template('monster.html', login_data = login_data, monster_data = monster_data)

@app.route('/test', methods=['GET'])
def test():
    if app.debug is not True:
        return flask.abort(403)
    msg_to = ['rrtw0627@gmail.com','haca00193@gmail.com']
    msg_subject = 'TEST'
    msg_content = f'''
        <h1>test</h1>
        <p>yoyoyo</p>
    '''
    send_mail(msg_to, msg_subject, msg_content)
    return "TEST"
    #return flask.render_template('test.pug', data={"A": "AA","B": "BB"})

if __name__ == '__main__':
    app.run(threaded=True, port=5000, debug=True)