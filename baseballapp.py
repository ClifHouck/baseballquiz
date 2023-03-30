from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
import random
from Levenshtein import distance
import json
import jsonschema

app = Flask(__name__)

# Define the JSON schema for the players data
players_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "patternProperties": {
        "^[0-9]+$": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "picture_file_name": {"type": "string"}
            },
            "required": ["name", "picture_file_name"]
        }
    }
}

# Load the players data from the file
with open("players.json", "r") as f:
    players_data = json.load(f)

# Validate the players data against the schema
try:
    jsonschema.validate(players_data, players_schema)
    print("Players data is valid!")
except jsonschema.ValidationError as e:
    print("Players data is invalid:")
    print(e)

players_keys = list(players_data.keys())

@app.route("/")
def index():
    if request.method == "POST" and "restart" in request.form:
        session["score"] = 0
        session["guesses"] = 0
        return redirect(url_for("index"))
    
    random_player_id = random.choice(players_keys)
    random_player = players_data[random_player_id]
    session["current_player_id"] = random_player_id

    if "score" in session:
        score = session["score"]
    else:
        score = 0
        session["score"] = score
        session["guesses"] = 0

    if not session:
        session["score"] = 0
        session["guesses"] = 0

    return render_template(
        "index.html",
        player={
            "name": random_player["name"],
            "picture_file_name": random_player["picture_file_name"]
        },
        score=session["score"],
    )

@app.route("/submit", methods=["POST"])
def submit():
    player_id = session["current_player_id"]
    player = players_data[player_id]
    guessed_name = request.form["name"].strip().lower()
    last_name = player["name"].split()[-1].lower()
    distance_score = distance(guessed_name.lower(), last_name)
    if distance_score <= 2:
        session["score"] += 1
        message = "Correct!"
    else:
        message = "Incorrect!"
    session["guesses"] = session.get("guesses", 0)
    session["guesses"] += 1
    if session["guesses"] >= 20:
        percentage = session["score"] / 20 * 100
        if percentage >= 65:
            pass_fail = "Congratulations, you passed!"
        else:
            pass_fail = "Try again?"
        session["score"] = 0
        session["guesses"] = 0
        return render_template("final.html", percentage=percentage, pass_fail=pass_fail)
    else:
        return render_template(
            "submit.html",
            message=message,
            player={
                "name": player["name"],
                "picture_file_name": player["picture_file_name"]
            },
            score=session["score"],
        )
    
@app.route("/restart")
def restart():
    # Reset the score and guess counter
    session["score"] = 0
    session["guesses"] = 0
    # Redirect the user to the index page as if they were starting a new session
    return redirect(url_for("index"))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True)
