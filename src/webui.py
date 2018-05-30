from flask import Flask, jsonify, render_template
from sassutils.wsgi import SassMiddleware


def serve(report, host="localhost", port=8080, debug=True):
    app = Flask(__name__)
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        __name__: ('static/sass', 'static/css', '/static/css')
    })

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/hooks")
    def hooks():
        return jsonify({k:v.__dict__ for (k, v) in report.hooks.items()})

    @app.route("/hooks/<hash>")
    def hook(hash):
        if hash in report.hooks:
            return jsonify(report.hooks[hash].__dict__)
        else:
            return ("invalid hash", 404)

    app.run(host, port, debug)