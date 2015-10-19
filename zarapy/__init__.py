from flask import Flask

from flask.sessions import SessionInterface
from inspector import inspect_page
import sys

session_opts = {
    'session.type': 'ext:memcached',
    'session.url': '127.0.0.1:11211',
    'session.data_dir': './cache',
}

class BeakerSessionInterface(SessionInterface):
    def open_session(self, app, request):
        session = request.environ['beaker.session']
        return session

    def save_session(self, app, session, response):
        session.save()

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.register_blueprint(inspect_page)

app.config.from_pyfile('app.cfg')
app.secret_key = 'b\x02|{\xb8Tt\xf1N\x99\x9d\xa3\x15\xe2~\x80\xc9\x18\xfb\x87lv\xc1\xf7'
#app.secret_key = os.urandom(24)

import zarapy.view


if __name__ == "__main__":
    app.run()
