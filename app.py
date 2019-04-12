import flask

import clickbait_test_real

app = flask.Flask(__name__)

# home page for clickbait: have user input bar
@app.route("/")
def hello_route():
    return flask.send_from_directory(".", "clickbaitHome.html")


@app.route("/api/v1/classify", methods=["POST"])
def classify_api():
    request = flask.request.get_json(silent=True)
    print(request)
    print(type(request))
    # call backend methods ???
    client = clickbait_test_real.get_authenticated_service()
    videoId = clickbait_test_real.get_video_id(request)
    videoData = clickbait_test_real.get_single_video(client)
    print("YEET")
    #return prediction from backend
    return flask.jsonify(request)
