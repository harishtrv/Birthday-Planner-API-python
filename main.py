from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# http://harishtkottur.pythonanywhere.com/
class User(db.Model):
  userName = db.Column(db.String(30), primary_key=True)
  contactNo = db.Column(db.Integer, unique=True, nullable=False)
  DOB = db.Column(db.Date, unique=False, nullable=False)
  pw =  db.Column(db.String(20), unique=False, nullable=False)
  def __repr__(self):
    return f"{self.userName} - {self.contactNo} - {self.DOB}"

class Friends(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  userName = db.Column(db.String(30),unique=False, nullable=False)
  friendName = db.Column(db.String(30),unique=False, nullable=False)

class Sessions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  userName = db.Column(db.String(30),unique=True, nullable=False)

@app.route("/getfriends/<userName>")
def getfriends(userName):
  friends = Friends.query.filter_by(userName=userName).all()
  output = []
  for friend in friends:
    user  = User.query.get(friend.friendName)
    if user is not None:
      user_data = {'userName':user.userName,'contactNo':user.contactNo,'DOB':user.DOB.strftime("%x")}
      output.append(user_data)
  return {'friends':output}

@app.route("/getfriendsuggestion/<userName>")
def getfriendsuggestion(userName):
  friends = Friends.query.filter_by(userName = userName).all()
  flist = []
  for friend in friends:
    flist.append(friend.friendName)
  output = []
  users  = User.query.all()
  for user in users:
    if flist.count(user.userName) <= 0 and user.userName!=userName:
      user_data = {'userName':user.userName,'contactNo':user.contactNo,'DOB':user.DOB.strftime("%x")}
      output.append(user_data)
  return {'suggestedfriends':output}

@app.route("/addfriend", methods=['POST'])
def addfriend():
  friend = Friends(userName=request.json['userName'],friendName=request.json['friendName'])
  db.session.add(friend)
  db.session.commit()
  return {'friendName':friend.friendName}

@app.route("/getallfriends")
def getallfriends():
  friends = Friends.query.all()
  output = []
  for friend in friends:
    user_data = {'userName':friend.userName,'friend':friend.friendName}
    output.append(user_data)
  return {'FriendsList':output}

@app.route("/getallusers")
def getallusers():
  users = User.query.all()
  output = []
  for user in users:
    user_data = {'userName':user.userName,'contactNo':user.contactNo,'DOB':user.DOB.strftime("%x")}
    output.append(user_data)
  response = {'users':output}
  return response

@app.route("/getusers/<userName>")
def getusers(userName):
  user = User.query.get(userName)
  return {"userName": user.userName,"conactNo":user.contactNo, "DOB":user.DOB.strftime("%x")}

@app.route("/adduser", methods=['POST'])
def adduser():
  dob = request.json['DOB'].split('-')
  user = User(userName=request.json['userName'],contactNo=request.json['contactNo'],DOB=datetime(int(dob[0]),int(dob[1]),int(dob[2])), pw=request.json['pw'])
  db.session.add(user)
  db.session.commit()
  return {'userName':user.userName}

@app.route("/deleteuser/<userName>", methods=['DELETE'])
def deleteuser(userName):
  user  = User.query.get(userName)
  Friends.query.filter_by(userName = userName).delete()
  Friends.query.filter_by(friendName = userName).delete()

  if user is None:
    return {"error":"not found"}
  db.session.delete(user)
  db.session.commit()
  return {"userName": user.userName,"conactNo":user.contactNo, "DOB":user.DOB}

@app.route("/removefriend/<userName>/<friendName>", methods=['DELETE'])
def removefriend(userName, friendName):
  Friends.query.filter(Friends.userName == userName, Friends.friendName == friendName).delete()
  db.session.commit()
  return {"userName": userName, "friendName": friendName}

@app.route("/authenticate/<userName>/<pw>")
def authenticate(userName, pw):
  user = User.query.get(userName)
  if user is None:
    return {"error":"not found"}
  if(user.pw == pw):
    Sessions.query.filter_by(userName = userName).delete()
    sessionId= int(random.random()*10000000)
    session = Sessions(id=sessionId, userName=userName)
    db.session.add(session)
    db.session.commit()
    return {"message":"success", "sessionId":sessionId}
  return {"message":"wrong password"}

@app.route("/sessionValidation/<userName>/<sessionId>")
def sessionValidation(userName, sessionId):
  session = Sessions.query.get(sessionId)
  if(session and session.userName == userName):
    return {"message":"success"}
  return {"message":"Session expired"}

@app.route("/")
def hello():
  db.create_all()
  return "<p>Hello</p>"

if __name__ == "__main__":
    app.run(debug=True)
