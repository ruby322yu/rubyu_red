from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ruby/myweb/database.db'
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(32))
    player_name1 = db.Column(db.String(32))
    player_name2 = db.Column(db.String(32))
    player_name3 = db.Column(db.String(32))
    player_name4 = db.Column(db.String(32))
    player_name5 = db.Column(db.String(32))
    player_name6 = db.Column(db.String(32))
    player_dotaid1 = db.Column(db.Integer, unique=True)
    player_dotaid2 = db.Column(db.Integer, unique=True)
    player_dotaid3 = db.Column(db.Integer, unique=True)
    player_dotaid4 = db.Column(db.Integer, unique=True)
    player_dotaid5 = db.Column(db.Integer, unique=True)
    player_dotaid6 = db.Column(db.Integer, unique=True)
    captain_pos = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    total_matches = db.Column(db.Integer)
    matches_won = db.Column(db.Integer)
    status = db.Column(db.String(16))
    immunity = db.Column(db.DateTime)

    def __init__(self, team_name, email, password, name1,name2,name3,name4,name5,name6,
                 dotaid1, dotaid2, dotaid3, dotaid4, dotaid5, dotaid6, captain_pos):
        self.team_name = team_name
        self.email = email
        self.password = password
        self.player_name1 = name1
        self.player_name2 = name2
        self.player_name3 = name3
        self.player_name4 = name4
        self.player_name5 = name5
        self.player_name6 = name6
        self.player_dotaid1 = dotaid1
        self.player_dotaid2 = dotaid2
        self.player_dotaid3 = dotaid3
        self.player_dotaid4 = dotaid4
        self.player_dotaid5 = dotaid5
        self.player_dotaid6 = dotaid6
        self.captain_pos = captain_pos
        self.status = "free"
        self.immunity = datetime.datetime.now()

        self.matches_won = 0
        self.total_matches = 0
        # still need to do starting id and rank
        num_teams = len(Team.query.all())+1
        self.id = num_teams
        self.rank = num_teams

    def __repr__(self):
        return '<Team %r>' % self.team_name

    def is_free(self):
        return self.status=="free"



class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id1 =  db.Column(db.Integer)
    team_id2 =  db.Column(db.Integer)
    winning_team_id =  db.Column(db.Integer)
    dotabuff_url1 =  db.Column(db.Integer)
    dotabuff_url2 =  db.Column(db.Integer)
    dotabuff_url3 =  db.Column(db.Integer)
    status = db.Column(db.String(16))

    def __init__(self, team1, team2):
        self.team_id1 = team1
        self.team_id2 = team2
        self.winning_team_id = None
        self.status = "pending"
        self.dotabuff_url1 = ""
        self.dotabuff_url2 = ""
        self.dotabuff_url3 = ""

        self.id = len(Match.query.all())+1

    def __repr__(self):
        return 'Match: '+str(self.team_id1) + " challenges "+str(self.team_id2)+ " status:"+self.status


def get_in_progress(team1_id, team2_id):
    return Match.query.filter_by(team_id1 = team1_id).filter_by(team_id2 = team2_id).filter_by(status="in_progress").first()

def get_in_pending(team1_id, team2_id):
    return Match.query.filter_by(team_id1 = team1_id).filter_by(team_id2 = team2_id).filter_by(status="pending").first()


# assumes both teams are available to challenge
# creates a new match object, sets both teams to immune for 2 days
def challenge(team1_id, team2_id):
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)

    team1.status = "challenging"
    team2.status = "challenged"
    team1.immunity = datetime.datetime.now() +  datetime.timedelta(days=2)
    team2.immunity = datetime.datetime.now() +  datetime.timedelta(days=2)
    # send an email
    new_match = Match(team1_id, team2_id)
    db.session.add(new_match)
    db.session.commit()


def finish_challenge(team1_id, team2_id, team1_won, db_url1="", db_url2="", db_url3=""):
    match = get_in_progress(team1_id, team2_id)
    match.status = "finished"
    match.dotabuff_url1 = db_url1
    match.dotabuff_url2 = db_url2
    match.dotabuff_url3 = db_url3

    if team1_won: # challenging team won
        match.winning_team_id = team1_id
        swap_rank(team1_id, team2_id)
    else:  # defending team won
        match.winning_team_id = team2_id
        team1 = Team.query.get(team1_id)
        team2 = Team.query.get(team2_id)
        team2.immunity = datetime.datetime.now() + datetime.timedelta(days=2)
        team1.status = "free"
        team2.status = "immune"
        team1.total_matches += 1
        team2.total_matches += 1
        team2.matches_won += 1

    db.session.commit()


# challenging, defending
def swap_rank(team1_id, team2_id):
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)
    team1.total_matches += 1
    team2.total_matches += 1
    team1.matches_won += 1
    # swap their ranks
    tmp = team1.rank
    team1.rank = team2.rank
    team2.rank = tmp
    # set both team to 1 day immunity
    team1.status = "immune"
    team2.status = "immune"
    team1.immunity = datetime.datetime.now() + datetime.timedelta(days=1)
    team2.immunity = datetime.datetime.now() + datetime.timedelta(days=1)

    db.session.commit()

def accept_challenge(team1_id, team2_id):
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)

    team1.status = "in_progress"
    team2.status = "in_progress"

    match = get_in_pending(team1_id, team2_id)
    match.status = "in_progress"
    # send an email somewhere here
    db.session.commit()

