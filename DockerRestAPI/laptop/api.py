from flask import Flask, jsonify, request, Response, abort
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("db", 27017)
controls = client.brevets.controls

def to_csv(rows, fields):
    lines = [",".join(fields)]
    for row in rows:
        values = []
        for f in fields:
            values.append(row[f])
        lines.append(",".join(values))
    return "\n".join(lines)

@app.route("/listAll")
@app.route("/listAll/json")
def list_all():
    return jsonify(get_times(["open", "close"], "open"))

@app.route("/listAll/csv")
def list_all_csv():
    f = ["open", "close"]
    rows = get_times(f, "open")
    return Response(to_csv(rows, f), mimetype="text/csv")

@app.route("/listOpenOnly")
@app.route("/listOpenOnly/json")
def list_open_only():
    return jsonify(get_times(["open"], "open"))

@app.route("/listOpenOnly/csv")
def list_open_only_csv():
    rows = get_times(["open"], "open")
    return Response(to_csv(rows, ["open"]), mimetype="text/csv")

@app.route("/listCloseOnly")
@app.route("/listCloseOnly/json")
def list_close_only():
    return jsonify(get_times(["close"], "close"))

@app.route("/listCloseOnly/csv")
def list_close_only_csv():
    rows = get_times(["close"], "close")
    return Response(to_csv(rows, ["close"]), mimetype="text/csv")


def get_times(fields, sort_field):
    """fields: which of 'open'/'close' to include; sort_field: which one to sort by."""
    raw = request.args.get("top")
    if raw is None:
        top = None
    else:
        try:
            top = int(raw)
        except ValueError as e:
            abort(400)
        if top < 1:
            abort(400)
    projection = {"_id": 0}
    for f in fields:
        projection[f] = 1 

    cursor = controls.find({}, projection).sort(sort_field, 1)

    if top is not None:
        cursor = cursor.limit(top)
    return list(cursor)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
