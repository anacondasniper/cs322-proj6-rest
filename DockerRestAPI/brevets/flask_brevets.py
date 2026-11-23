"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import pymongo
import logging
import validation

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
mongo = pymongo.MongoClient("db", 27017)
db = mongo.brevets
controls = db.controls
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    bd = request.args.get('brevet_dist', 200, type=int)
    start = request.args.get('start_time', arrow.now().isoformat(), type=str)
    app.logger.debug("request.args: {}".format(request.args))
    app.logger.debug("km={}".format(km))
    app.logger.debug("brevet distance={}".format(bd))
    app.logger.debug("start time={}".format(start))
    open_time = acp_times.open_time(km, bd, start)
    close_time = acp_times.close_time(km, bd, start)
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/_submit", methods=["POST"])
def _submit():
    docs = []
    data = request.get_json(silent=True)
    if data is None:
        return flask.jsonify(error="No data received"), 400
    rows = data.get("controls", [])
    try:
        brevet_dist = int(data["brevet_dist"])
    except (KeyError, ValueError, TypeError):
        return flask.jsonify(error="Invalid brevet distance"), 400
    start_time = data.get("start_time")
    msg = validation.validate_controls(rows, brevet_dist)
    if msg:
        return flask.jsonify(error=msg), 400
    if len(rows) == 0:
        return flask.jsonify(error="No controls to submit"), 400
    for row in rows:
        try:
            km = float(row["km"])
        except (ValueError, KeyError, TypeError) as e:
            return flask.jsonify(error=str(e)), 400
        if km < 0:
            return flask.jsonify(error="Km less than 0"), 400
        open_time = acp_times.open_time(km, brevet_dist, start_time)
        close_time = acp_times.close_time(km, brevet_dist, start_time)
        docs.append({
            "km": km,
            "miles": row.get("miles"), 
            "location": row.get("location"), 
            "open": open_time,
            "close": close_time
        })
    controls.delete_many({})
    controls.insert_many(docs)
    return flask.jsonify(message="Success"), 200

@app.route("/display")
def display():
    try:
        docs = list(controls.find())
    except pymongo.errors.PyMongoError as e:
        flask.flash("No controls have been submitted yet")
        return flask.redirect(flask.url_for("index"))
    if len(docs) == 0:
        flask.flash("No docs found!")
        return flask.redirect(flask.url_for("index"))
    return flask.render_template("display.html", controls=docs)
#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
