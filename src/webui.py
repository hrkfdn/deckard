from flask import Flask, jsonify, render_template, Response
from sassutils.wsgi import SassMiddleware
import pygments.formatters


def serve(report, host="localhost", port=8080, debug=True):
    app = Flask(__name__)
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        __name__: ('static/sass', 'static/css', '/static/css')
    })

    try:
        formatter = pygments.formatters.HtmlFormatter(style="arduino")
    except pygments.util.ClassNotFound:
        formatter = pygments.formatters.HtmlFormatter()

    css = formatter.get_style_defs('.highlight')

    @app.route("/")
    def index():
        return render_template("index.html", report=report)

    @app.route("/hooks")
    def hooks():
        return jsonify({k: v.__dict__ for (k, v) in report.hooks.items()})

    @app.route("/hooks/<md5>/")
    def hook(md5):
        if md5 in report.hooks:
            return render_template("hook.html", report=report, hook=report.hooks[md5])
        else:
            return "invalid hash", 404

    @app.route("/hooks/<md5>/callgraph")
    def callgraph(md5):
        if md5 in report.hooks:
            return jsonify(report.get_cg(report.hooks[md5]))
        else:
            return "invalid hash", 404

    @app.route("/static/css/pygments.css")
    def pygments_css():
        return Response(css, mimetype="text/css")

    app.run(host, port, debug)
