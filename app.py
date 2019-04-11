import flask

app = flask.Flask(__name__)

# home page for clickbait: have user input bar
@app.route("/")
def hello_route():
    return flask.send_from_directory(".", "clickbaitHome.html")


@app.route("/api/v1/classify", methods=["POST"])
def classify_api():
    request = flask.request.get_json(silent=True)
    # requestDict = {userUrl: request}
    print(request)
    print(type(request))
    if isinstance(request, dict):
        response = {
            "your url: " + request.get(userUrl)
        }
    else:
        response = {
            "error": "Bad input"
        }
    return flask.jsonify(response)