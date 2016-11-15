from flask import Flask
from flask import render_template
from flask import request
from dota_analysis import *
from ladder_classes import *


#app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dotafyme", methods=['GET', 'POST'])
def dota_index():
    if request.method == 'POST':
        id = request.form['dota_id']
        return render_template("dotaloading.html", id = id)
    return render_template("dotaindex.html", error=None)


@app.route("/dotafyme/<int:account_id>")
def dota_analysis(account_id):
    try:
        player = player_data(api.get_player_summaries(account_id), account_id)
        player.generate_statement()
        return render_template("dotaresults.html", player=player)
    except:
        return render_template("dotaindex.html", error=True)


@app.route("/aboutme")
def aboutme():
    return render_template("aboutme.html")

@app.route("/myresume")
def resume():
    return render_template("myresume.html")

@app.route("/dotaladder/teams/<int:team_id>")
def team_page(team_id):
    team = Team.query.get(team_id)
    return render_template("team.html", team=team)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpage.html', error_code=404), 404

@app.errorhandler(501)
def server_error(e):
    return render_template('errorpage.html', error_code=501), 501


if __name__ == "__main__":
    app.debug = True
    app.run()