from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import join_room, leave_room, send, SocketIO
import datetime
from os import path
import os
#import eventlet
#eventlet.monkey_patch()

app = Flask(__name__);
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///main.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "etshtssrstjrdtrtsj@dtyjyjrtyj3456rthjrstjrjeyrstyjrsthjr";
socketio = SocketIO(app, manage_session=False);

db = SQLAlchemy(app);
app.app_context().push();



def create_database():
	if not path.exists('App/main.db'):
		db.create_all();

class UserModel(db.Model):
	id = db.Column(db.Integer(), primary_key=True);
	e_mail = db.Column(db.String(length=20), nullable=False);
	password = db.Column(db.String(length=20), nullable=False);

create_database();
import smtplib
import random

class Sendmail:
	def __init__(self, email):
		self.a = 0;
		self.code="";
		while self.a<=3:
			self.codes = str(random.randint(0, 9));
			self.code +=self.codes; 
			self.a+=1;	
			
		self.sender = "shanutc1212@gmail.com";
		self.receiver = email;
		self.password = "wuqemjopppviyoif";
		self.subject = "Account Verification";
		self.body = f"Your Account Verification code is {self.code}";

		message = f"""from: best.com
		To: {self.receiver}
		Subject: {self.subject}\n
		{self.body}	
		"""

		server = smtplib.SMTP("smtp.gmail.com", 587);
		server.starttls();
		
		server.login(self.sender, self.password);
		print("logged In...")

		server.sendmail(self.sender, self.receiver, message)
		
		server.quit();
		self.orignal_code = self.code;




from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import string

store_email = None;
store_password = None;
global val_e_mail
val_e_mail = None; 

@app.route('/', methods=['GET', 'POST'])
def home():
	global val_e_mail
	if 'email' in session:
		print(val_e_mail, "--------------------------------")
		username = session.get('email').split('@')[0];
		return render_template("home.html", infor=username) 
	else:
		return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
	if 'searching' in session:
		search = request.form.get("search");
		print(search)
		search_res = "%{}%".format(search);
		
		check_pass_word = UserModel.query.filter(UserModel.password.like(search_res)).all()
		check_mail = UserModel.query.filter(UserModel.e_mail.like(search_res)).all()
		
		return render_template('search_results.html', infor=check_mail);
	else:
		return redirect(url_for('home'))	

@app.route('/login', methods=['GET', 'POST'])
def login():
	global val_e_mail
	if request.method == 'POST':
		val_e_mail = request.form.get('e_mail');
		password = request.form.get('password');
		user = UserModel.query.filter_by(e_mail=val_e_mail).first();
		pass_word = UserModel.query.filter_by(password=password).first();
		if val_e_mail == "" and password == "":
			flash("Empty E-mail or Password", category="danger")
		else:	
			if user:
				if pass_word:
					session['email'] = val_e_mail;
					return redirect(url_for("home"))
				else:
					flash("Incorrect Password, Try Again", category='danger')
			else:
				flash("Incorrect E-Mail, Try Again", category='danger')			
	return render_template('login.html');



@app.route('/verify', methods=['GET', 'POST'])

def Verify():
	global p
	global sent
	
	if store_email != None:
		while p < 1:
			sent = Sendmail(store_email);
			p+=1;

		if request.method == 'POST':
			store_ver_1 = request.form.get('ver1');
			store_ver_2 = request.form.get('ver2');
			store_ver_3 = request.form.get('ver3');
			store_ver_4 = request.form.get('ver4');

			full_code = str(store_ver_1) + str(store_ver_2) + str(store_ver_3) + str(store_ver_4);
			print(full_code + " this is the code $$$$$$$$$$$$$$$$$$$$$$$$$$")
			if full_code == sent.orignal_code:
				storing_email_and_pass_in_db = UserModel(e_mail=store_email, password=store_password);
				db.session.add(storing_email_and_pass_in_db);
				db.session.commit();
				return redirect(url_for("login"));

		return render_template('verify.html', v_mail=store_email);
	elif 'password' in session:
		return redirect(url_for("/"));
	else:
		return redirect(url_for("login"));

			
@app.route('/signIn', methods=['GET', 'POST'])
def Signup():
	global store_email
	global store_password
	global p
	p = 0;
	if request.method == 'POST':
		store_email = request.form.get('st_mail');
		store_password = request.form.get('st_password');
		retype_password = request.form.get('confirm_password');
		print(str(p) + "during signup");
		if (store_password == retype_password != ""):
			return redirect(url_for("Verify"));
			
	return render_template("sign_in.html");

@app.route('/account-creation', methods=['GET', 'POST'])
def account():
	return render_template('account_creation.html')

@app.route('/logout')
def logout():
	session.pop('email', None);
	return redirect(url_for("login"));

rooms = {};

def generate_code(leng):
	while True:
		code = "";
		alpha = string.ascii_lowercase;
		code = "".join(random.choice(alpha) for i in range(leng))
		if code not in rooms:
			break;
	return code

@app.route('/chattingform', methods=['POST', 'GET'])
def chattingform():
	session.pop('room', None);
	if request.method == 'POST':
		code = request.form.get('roomcode');
		join = request.form.get('joinbtn', False);
		create = request.form.get('createbtn', False)

		if join != False and not code:
			flash("No Room code is Provided..", category='danger');
			return render_template('chatform.html');
		room = code;
		if create != False:
			room = generate_code(4);
			rooms[room] = {'members' : 0, 'messages' : []};
		elif code not in rooms:
			 flash("Room does not exists..", category='danger');
			 return render_template('chatform.html');

		session['room'] = room;
		return redirect(url_for('liveChatting'));	 
	return render_template('chatform.html');

@app.route('/chatting')
def liveChatting():
	if session.get('room') is None:
		return redirect(url_for('chattingform'));
	return render_template('chatting.html', roomcode=session.get('room'));

@socketio.on("connect")
def connect(auth):
	room = session.get('room');
	if not room:
		return
	if room not in rooms:
		leave_room(room);
	join_room(room);
	send({"name":session.get('email').split('@')[0], "message":"has entered the room."}, to=room)
	rooms[room]['members'] += 1;
	print(f"{session.get('email')} has joined the room {room}")
	print(rooms, "this is rooms dataset")

@socketio.on("disconnect")
def disconnect():
	room = session.get('room');
	leave_room(room);

	if room in rooms:
		rooms[room]['members'] -= 1;
		if rooms[room]['members'] <= 0:
			del rooms[room]
	send({"name":session.get('email'), "message":"has left the room."}, to=room)
	print(f"{session.get('email')} has left the room {room}")

@socketio.on("message")
def message(data):
	room = session.get("room");
	if room not in rooms:
		return
	content = {
		"name": session.get('email').split('@')[0],
		"message": data["data"]
	}

	send(content, to=room, include_self=False);
	rooms[room]['messages'].append(content);
	print(rooms, " with some cool messages")



print("hello")

if __name__ == "__main__":
	socketio.run(app);

