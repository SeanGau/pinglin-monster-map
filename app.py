import flask
import hashlib
from os import walk
app = flask.Flask(__name__)
app.jinja_env.globals['GLOBAL_TITLE'] = "坪林尋怪地圖"

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000, debug=True)