import flask, json, hashlib, string, random, os, shutil, requests
from datetime import datetime, timezone, timedelta
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sassutils.wsgi import SassMiddleware
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener

app = flask.Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['GLOBAL_TITLE'] = "坪林尋怪地圖"
app.jinja_env.globals['GLOBAL_VERSION'] = datetime.now().timestamp()
db = SQLAlchemy(app)
mail = Mail(app)
register_heif_opener()

ADMIN_ID = {1, 3, 47}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}

elements = {"water": "水", "ground": "地", "wind": "風", "fire": "火"}
demo_monster_data = {
    "thumb": "demo_A.png",
    "image": ["demo_A.png", "demo_B.png", "demo_C.png"],
    "founder_id": 1,
    "founder": "黃玟霖",
    "name": "垃圾怪",
    "tag": ["北勢溪", "漂流垃圾", "人就是共犯"],
    "category": "水域",  # 人文、過度、水域、山野
    "element": "water",  # water, ground, wind, fire
    "date": ["2011", "05", "10"],
    "local": "北勢溪親水吊橋下方",
    "disc": "出現在河流中堆積很多垃圾的地方，像是垃圾袋、寶特瓶，那散發出很臭的味道，因為長期堆滿惡臭的垃圾，人經過的時候都會久留。",
    "strong": "收集垃圾一口吐出",
    "weak": "怕光、怕人",
    "title": "北勢溪的漂流垃圾垃圾",
    "story": "一堆噁心的垃圾在原本清澈的北勢溪漂流著，要問是誰做的？其實就是我們自己。人們因為懶惰，不把垃圾丟入垃圾桶，反而直接丟在河裡，所以才會製造出垃圾怪，垃圾怪一開始會把人們所丟的垃圾收集起來，等收到一定的量，再全部放出來，使河川遭受永久性的污染，就是為了讓河川裡的魚蝦等...受到傷害。垃圾怪喜歡暗暗的地方，而且很怕被人發現，所以都待在河川深處，大家都覺得垃圾怪很可惡，殊不知人類才是罪惡的共犯。"
}

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

def alert(message, redir):  # alert then redirect
    return f'''<script type="text/javascript">
						alert("{message}");
						window.location.href = "{redir}";
						</script>'''

def send_mail(recevier_array, subject, html_content):
    msg = Message(subject=app.jinja_env.globals['GLOBAL_TITLE'] +
                  " - "+subject, recipients=recevier_array, html=html_content)
    mail.send(msg)

# ------------------------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    login_data = flask.session.get('login_data', None)
    if login_data is not None:
        login_data = json.loads(login_data)
    return flask.render_template('index.html', login_data=login_data)


@app.route('/map')
def monstermap():
    geojson = {"type": "FeatureCollection", "features": []}

    cb = db.session.execute(
        text("SELECT ST_AsGeoJSON(geom),data,id FROM public.monsters WHERE hidden=False ORDER BY id")).mappings().all()
    for row in cb:
        d = {"type": "Feature", "geometry": {
            "type": "Point", "coordinates": []}, "properties": {}}
        if row['st_asgeojson'] is not None:
            d['geometry'] = json.loads(row['st_asgeojson'])
        if row['data'] is not None:
            d['properties'] = row['data']
        else:
            continue
        d['properties']['monster_id'] = row['id']
        geojson['features'].append(d)

    login_data = flask.session.get('login_data', None)
    if login_data is not None:
        login_data = json.loads(login_data)

    return flask.render_template('map.html', login_data=login_data, geojson=geojson)


@app.route('/portal', methods=['GET', 'POST'])
def portal():
    login_data = flask.session.get('login_data', None)
    if login_data is None:
        return alert('尚未登入！', flask.url_for('login'))
    login_data = json.loads(login_data)

    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        if _data['email'] != login_data['email']:
            return flask.abort(406)
        else:
            db.session.begin()
            if len(_data['password']) >= 8 and len(_data['password']) <= 20:
                db.session.execute(
                    text("UPDATE public.users SET password=:password WHERE email=:email"), {"password": gethashed(_data['password']), "email": _data['email']})
            if len(_data['username']) > 0 and len(_data['username']) <= 12:
                db.session.execute(
                    text("UPDATE public.users SET username=:username WHERE email=:email"), {"username": _data['username'], "email": _data['email']})
                login_data['username'] = _data['username']
                flask.session['login_data'] = json.dumps(login_data)
            db.session.commit()
            return "ok"
    else:
        isAdmin = login_data['id'] in ADMIN_ID
        cb = db.session.execute(text("SELECT * FROM public.monsters WHERE founder=:founder ORDER BY id"), {"founder": login_data['id']}).mappings().all()
        if isAdmin:
            cb = db.session.execute(text("SELECT * FROM public.monsters ORDER BY id DESC")).mappings().all()
        login_data['data'] = []
        tz = timezone(timedelta(hours=8), "Asia/Taipei")
        for row in cb:
            founder_name = db.session.execute(
                text("SELECT username FROM public.users WHERE id=:id"), {"id": row['founder']}).mappings().first()
            commentCount = db.session.execute(
                text("SELECT COUNT(*) FROM public.comments WHERE monster_id=:id AND hidden=false"), {"id": row['id']}).mappings().first()['count']
            login_data['data'].append({
                "name": row["data"]["name"],
                "slug": row["id"],
                "founder": founder_name["username"],
                "create_at": row["create_at"].astimezone(tz).strftime("%Y/%m/%d %H:%M:%S"),
                "hidden": "隱藏中" if row["hidden"] else "顯示中",
                "comments": commentCount
            })
        comments = None
        if isAdmin:
            comments = db.session.execute(
            text("SELECT id, author, data, create_at, monster_id, hidden, (SELECT username AS author_name FROM public.users WHERE id=author) FROM public.comments ORDER BY id DESC")).mappings().all()
        return flask.render_template('portal.html', login_data=login_data, isAdmin=isAdmin, comments = comments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        _data = flask.request.form
        cb = db.session.execute(
            text("SELECT * FROM public.users WHERE email=:email AND password=:password"), {"email": _data['email'], "password": gethashed(_data['password'])}).mappings().first()
        if cb is not None:
            cb_data = dict(cb)
            session_data = {
                "email": cb_data['email'],
                "username": cb_data['username'],
                "id": cb_data['id']
            }
            flask.session.permanent = False
            flask.session['login_data'] = json.dumps(session_data)
            # send_mail([_data['email']], "login", "<h1>有人登入你的帳號！</h1>")
            return flask.redirect(flask.url_for('monstermap'))
        else:
            return alert("帳號或密碼錯誤！", flask.url_for('login'))
    else:
        return flask.render_template('login.html')


@app.route('/logout')
def logout():
    flask.session.clear()
    return alert("您已登出！", "/map")


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        cb = db.session.execute(
            text("SELECT * FROM token_table WHERE token=:token"), {"token": _data['token']}).mappings().first()
        if cb is not None:
            cb_data = dict(cb)
            exp_t = cb_data['token_expire']
            if exp_t.timestamp() > datetime.now().timestamp() and len(_data['password']) >= 8 and len(_data['password']) <= 20:
                db.session.execute(
                    text("UPDATE public.users SET password=:password WHERE email=:email"), {"password": gethashed(_data['password']), "email": cb_data['email']})
                db.session.execute(
                    text("DELETE FROM public.token_table WHERE email=:email"), {"email": cb_data['email']})
                db.session.commit()
                return "ok"
        return flask.abort(406)
    else:
        return flask.render_template('reset.html')


@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if flask.request.method == 'POST':
        _data = flask.request.form
        token = gethashed(str(datetime.now().timestamp())+_data['email'])
        cb = db.session.execute(
            text("SELECT * FROM public.users WHERE email=:email"), {"email": _data['email']})
        if len(cb.mappings().all()) == 0:
            return alert("此信箱尚未註冊！", flask.url_for('forget'))
        db.session.execute(
            text("INSERT INTO public.token_table (email,token,token_expire) VALUES(:email,:token,(NOW() + interval '1 hour'))"), {"email": _data['email'], "token": token})
        db.session.commit()
        send_mail([_data['email']], "忘記密碼", f'''
				<div style="font-size: 1.5em; text-align: center;">
				<p>您好，</p>
				<p>坪林尋怪地圖收到<b>重設密碼</b>請求<p>
				<p>請點擊以下連結進行重設</p>
				<p><a href="https://strangepinglin.collective.tw/reset?token={token}" style="padding: 1em; background-color: #666;color: white; border-radius: 5px;">https://strangepinglin.collective.tw/reset?token={token}</a></p>
				<p>若無法點擊，請複製連結貼到​​​您的​​​瀏覽器</p>
				</div>
        ''')
        return alert("請至信箱收信！", flask.url_for('login'))
    else:
        return flask.render_template('forget.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        if flask.session.get('email_verify', None) is None:
            return "請先輸入並驗證Email"
        _data = flask.request.get_json()
        cb = db.session.execute(
            text("SELECT * FROM public.users WHERE email=:email"), {"email": _data['email']})
        if len(cb.mappings().all()) > 0:
            return "此信箱已被註冊！"
        elif _data['email'] == flask.session['email_verify']['email'] and _data['code'] == flask.session['email_verify']['code'] and len(_data['username']) > 0 and len(_data['username']) <= 12 and len(_data['password']) >= 8 and len(_data['password']) <= 20:
            cb = db.session.execute(
                text("INSERT INTO public.users (username,email,password) VALUES(:username,:email,:password)"), {
                    "username": _data['username'],
                    "email": _data['email'],
                    "password": gethashed(_data['password'])
                })
            db.session.commit()
            return "ok"
        else:
            return "註冊失敗，請聯絡管理員"
    else:
        return flask.render_template('register.html')


@app.route('/register/verify', methods=['GET', 'POST'])
def register_verify():
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        cb = db.session.execute(
            text("SELECT * FROM public.users WHERE email=:email"), {"email": _data['email']})
        if len(cb.mappings().all()) > 0:
            return "此信箱已被註冊！"
        else:
            code = get_random_string(10)
            send_mail([_data['email']], "信箱認證", f'''
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
            return flask.abort(406)
        else:
            return "ok"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    login_data = flask.session.get('login_data', None)
    if login_data is None:
        return flask.redirect("login", code=303)
    else:
        login_data = json.loads(login_data)
    if 'file' not in flask.request.files:
        return flask.abort(406)
    file = flask.request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return flask.abort(406)
    if file and allowed_file(file.filename):
        filename = "m" + str(datetime.now().timestamp()) + \
            "." + file.filename.rsplit('.', 1)[1].lower()
        im = Image.open(file)

        if hasattr(im, "_getexif"):
            orientation = 0x0112
            exif = im._getexif()
            if not exif:
                None
            elif orientation not in exif:
                None
            elif exif[orientation] == 3:
                im=im.rotate(180, expand=True)
            elif exif[orientation] == 6:
                im=im.rotate(270, expand=True)
            elif exif[orientation] == 8:
                im=im.rotate(90, expand=True)

        im.thumbnail((800, 800))
        if im.format != 'PNG':
            filename += '.jpg'
        if flask.request.form.get("current_path", None) is not None:
            im.save(os.path.join(app.config['UPLOAD_FOLDER'], flask.session.get(
                'current_editing', 'tmp'), filename))
        else:
            im.save(os.path.join(app.config['UPLOAD_FOLDER'], "tmp", filename))
        return filename


@app.route('/add', methods=['GET', 'POST'])
def add():
    login_data = flask.session.get('login_data', None)
    if login_data is None:
        return flask.redirect("login", code=303)
    else:
        login_data = json.loads(login_data)
    if flask.request.method == 'POST':
        _data = flask.request.get_json()
        _data["image"] = _data["image"][:3]
        _data["image"].insert(0, _data["thumb"])

        _data['founder'] = login_data['username']
        _data['founder_id'] = login_data['id']
        sql = text(f"INSERT INTO public.monsters (founder,data,geom) VALUES(:founder,:data,ST_MakePoint({_data['point'][1]},{_data['point'][0]})) RETURNING id")
        
        cb = db.session.execute(sql, {
            "founder": login_data['id'],
            "data": json.dumps(_data, ensure_ascii=True)
        })
        current_monster_id = str(cb.mappings().first()['id'])
        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], current_monster_id)):
            os.makedirs(os.path.join(
                app.config['UPLOAD_FOLDER'], current_monster_id))
        for image in _data["image"]:
            shutil.move(os.path.join(app.config['UPLOAD_FOLDER'], "tmp", image), os.path.join(
                app.config['UPLOAD_FOLDER'], current_monster_id, image))
        db.session.commit()
        return current_monster_id
        
    else:
        return flask.render_template('monster_add.html')


@app.route('/edit/<monster_id>', methods=['GET', 'POST'])
def edit(monster_id):
    login_data = flask.session.get('login_data', None)
    if login_data is None:
        return flask.redirect("login", code=303)
    else:
        login_data = json.loads(login_data)
        print(login_data)

    if flask.request.method == 'POST':
        if monster_id != flask.session.get('current_editing', None):
            return flask.abort(406)
        _data = flask.request.get_json()
        print(_data)
        sql = ""
        if "toggleHidden" in _data:
            sql = text("UPDATE public.monsters SET hidden = NOT hidden WHERE id = :id")
        elif "name" in _data and "point" in _data:
            sql = text(f"UPDATE public.monsters SET data = :data, geom = ST_MakePoint({_data['point'][1]},{_data['point'][0]}) WHERE id = :id")
        db.session.execute(sql, {
            "data": json.dumps(_data, ensure_ascii=True),
            "id": monster_id
        })
        db.session.commit()
        return "ok"
    else:
        cb = db.session.execute(
            text("SELECT ST_AsGeoJSON(geom),data,founder,hidden FROM public.monsters WHERE id=:id"), {"id": monster_id}).mappings().first()
        if cb is None:
            return flask.abort(404)
        if login_data['id'] != cb['founder'] and login_data['id'] not in ADMIN_ID:
            return flask.abort(403)

        cb['data']['date'] = list(
            map(lambda x: str(x).zfill(2), cb['data']['date']))

        flask.session['current_editing'] = monster_id
        return flask.render_template('monster_edit.html', login_data=login_data, monster_data=cb['data'], monster_pos=json.loads(cb['st_asgeojson']), monster_id=monster_id, hidden=cb['hidden'])


@app.route('/monster/<monster_id>')
def monster(monster_id):
    cb = db.session.execute(
        text("SELECT * FROM public.monsters WHERE id=:id"), {"id": monster_id}).mappings().first()
    if cb is None:
        return flask.abort(404)
    else:
        login_data = flask.session.get('login_data', None)
        can_edit = False
        if login_data is not None:
            login_data = json.loads(login_data)
            if login_data['id'] == cb['founder'] or login_data['id'] in ADMIN_ID:
                can_edit = True
        if cb['hidden'] == True and not can_edit:
            return flask.abort(403)

        cb['data']['date'] = list(
            map(lambda x: str(x).zfill(2), cb['data']['date']))
        monster_data = cb['data']
        monster_data['id'] = monster_id
        founder = db.session.execute(
            text("SELECT username FROM public.users WHERE id=:id"), {"id": cb['founder']}).mappings().first()
        comments = db.session.execute(
            text("SELECT author, data, (SELECT username AS author_name FROM public.users WHERE id=author) FROM public.comments WHERE monster_id=:id AND hidden=false"), {"id": monster_id}).mappings().all()
        monster_data['founder'] = founder['username']
        monster_data['comments'] = comments
        print(monster_data)
        return flask.render_template('monster.html', login_data=login_data, monster_data=monster_data, can_edit=can_edit, monster_id=monster_id)

@app.route('/addcomment', methods=['POST'])
def addcomment():
    login_data = flask.session.get('login_data', None)
    if login_data is not None:
        login_data = json.loads(login_data)
    else:
        return flask.jsonify({"success": False}), 403, {'contentType': 'application/json'}
    
    form = flask.request.form
    print(dict(form), login_data)
    cb = db.session.execute(
        text("INSERT INTO public.comments (author,monster_id,data) VALUES(:author,:monster_id,:data)"), {
            "author": login_data['id'],
            "monster_id": form['monster_id'],
            "data": json.dumps(form, ensure_ascii=True)
        })
    db.session.commit()
    
    return flask.jsonify({"success": True}), 200, {'contentType': 'application/json'}

@app.route('/test', methods=['GET'])
def test():
    if app.debug is not True:
        return flask.abort(403)
    msg_to = ['rrtw0627@gmail.com', 'haca00193@gmail.com']
    msg_subject = 'strangepinglin text mail'
    msg_content = f'''
        <h1>test!!!!</h1>
        <p>yoyoyo sooo strangeee</p>
    '''
    send_mail(msg_to, msg_subject, msg_content)
    return "test mail send"
    # return flask.render_template('test.pug', data={"A": "AA","B": "BB"})

@app.route('/igpost/<monster_id>', methods=['GET'])
def igpost(monster_id):
    if app.debug is not True:
        return flask.abort(403)
    cb = db.session.execute(
        text("SELECT * FROM public.monsters WHERE id=:id"), {"id": monster_id}).mappings().first()
    if cb is None:
        return flask.abort(404)
    cb['data']['date'] = list(
        map(lambda x: str(x).zfill(2), cb['data']['date']))
    monster_data = cb['data']
    monster_data['id'] = monster_id
    founder = db.session.execute(text("SELECT username FROM public.users WHERE id=:id"), {"id": cb['founder']}).mappings().first()
    monster_data['founder'] = founder['username']
    user_id = app.config['IG_USER_ID']
    access_token = app.config['IG_API_KEY']
    caption = f'''
    👹{monster_data['name']}👹
    棲地聚落：{monster_data['category']}
    元素屬性：{elements[monster_data['element']]}
    
    目擊者：{monster_data['founder']}
    目擊日期：{"/".join(monster_data['date'])}

    #{monster_data['title']}
    {monster_data['story']}
    #{" #".join(monster_data['tag'])}

    #坪林尋怪 #StrangePinglin #{monster_data['category']} #{elements[monster_data['element']]}
    #坪林故事採集 #Pinglinstory #採集人共作室 #Collectors
    '''
    #return f"<pre>{caption}</pre>"

    url = f"https://graph.facebook.com/v16.0/{user_id}/media"
    data = {
    "access_token": access_token,
    "image_url": f"https://strangepinglin.collective.tw/static/img/monsters/{monster_id}/{monster_data['image'][-2]}",
    "is_carousel_item": "true"
    }
    r = requests.post(url = url, data = data)
    print("media 1: ", r.json())
    media_id_1 = r.json().get("id")
    data = {
    "access_token": access_token,
    "image_url": f"https://strangepinglin.collective.tw/static/img/monsters/{monster_id}/{monster_data['image'][-1]}",
    "is_carousel_item": "true"
    }
    r = requests.post(url = url, data = data)
    print("media 2: ", r.json())
    media_id_2 = r.json().get("id")
    data = {
    "access_token": access_token,
    "media_type": "CAROUSEL",
    "children": f"{media_id_1},{media_id_2}",
    "caption": caption
    }
    r = requests.post(url = url, data = data)
    print("creation id: ", r.json())
    creation_id = r.json().get("id")
    url = f"https://graph.facebook.com/v16.0/{user_id}/media_publish"
    data = {
    "access_token": access_token,
    "creation_id": creation_id
    }
    r = requests.post(url = url, data = data)
    print(r.text)
    return(r.text)

if __name__ == '__main__':
    app.run(threaded=True, port=5005, debug=True, host='0.0.0.0')
