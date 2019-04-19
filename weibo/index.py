import psycopg2
import re
from flask import Flask, g, jsonify, render_template, request, Response, redirect, session
from flask_bcrypt import Bcrypt

CONN = None

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
bcrypt = Bcrypt(app)

def set_dbname_test():
	global dbname
	dbname = 'weibo_test'

def set_dbname_normal():
	global dbname
	dbname = 'postgres'

def connect_db():
	CONN = psycopg2.connect("dbname='" + dbname + "' user='postgres' host='127.0.0.1' password='postgres'")
	return CONN

def get_db():
	if not hasattr(g, 'postgres_db'):
		g.postgres_db = connect_db()
	return g.postgres_db

@app.route('/', methods=['GET'])
def login():
	return render_template('login.html')
    
@app.route('/home', methods=['GET'])
def home():
	if 'login_email' not in session:
		return redirect("http://localhost:8888")
	count = select_count(session['login_email'])
	posts = select_post(session['login_id'])
	comments = select_comment(session['login_id'])
	return render_template('home.html',posts=posts,count=count,comments=comments)

@app.route('/home', methods=['POST'])
def post():
	if 'login_email' in session:
		content = request.form['content'].strip()
		if insert_post(session['login_id'],content):
			resp = jsonify("success")
		else:
			resp = jsonify("You must type some letters in content")
		return resp
	else:
		resp = jsonify("Not login")
		return resp

@app.route('/login', methods=['POST'])
def login_do():
	email = request.form['email'].strip()
	password = request.form['password'].strip()
	if not valid_email(email):
		resp = jsonify("Invalid e-mail address")
		return resp
	if not valid_pass(password):
		resp = jsonify("Password should at least 6 characters")
		return resp
	if valid_user(email, password):
		session['login_email'] = email
		session['login_id'] = select_userid(email)
		resp = jsonify("success")
	else:
		resp = jsonify("incorrect email or password")
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.route('/registration', methods=['POST'])
def registration():
	email = request.form['email'].strip()
	password = request.form['password'].strip()
	confirm = request.form['confirm'].strip()
	if password != confirm:
		resp = jsonify("Your password can't be confirmed")
		return resp
	if not valid_email(email):
		resp = jsonify("Invalid e-mail address")
		return resp
	if not valid_pass(password):
		resp = jsonify("Password should at least 6 characters")
		return resp
	if insert_user(email, password):
		resp = jsonify("success")
	else:
		resp = jsonify("Email already exist")
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.route('/changepwd',methods=['GET'])
def changepwd():
	if 'login_email' not in session:
		return redirect("http://localhost:8888")
	return render_template('changepwd.html')

@app.route('/changepwd',methods=['POST'])
def dochangepwd():
	if 'login_email' in session:
		oldpwd = request.form['oldpwd'].strip()
		newpwd = request.form['newpwd'].strip()
		confirm = request.form['confirm'].strip()
		if newpwd != confirm:
			resp = jsonify("Your password can't be confirmed")
			return resp
		if not valid_pass(newpwd) or not valid_pass(oldpwd):
			resp = jsonify("Password should at least 6 characters")
			return resp
		if update_passwd(session['login_id'],oldpwd, newpwd):
			resp = jsonify("success")
		else:
			resp = jsonify("Your Old Password is Wrong")
		resp.headers['Access-Control-Allow-Origin'] = '*'
		return resp
	else:
		resp = jsonify("Not login")
		return resp
			
@app.route('/logout', methods=['POST'])
def logout():
	session.pop('login_email',None)
	session.pop('login_id',None)
	resp = jsonify('success')
	return resp

@app.route('/search_user',methods=['GET','POST'])
def search_user():
	if 'login_email' in session:
		session['search_email'] = request.form['search'].strip()
		if(len(session['search_email'])==0):
			res = None
			return render_template('search_user.html',res=res)
		cur = CONN.cursor()
		cur.execute("select username,id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.users where username like %s order by username", [session['login_id'], '%' + session['search_email'] + '%'])
		res = cur.fetchall()
		session['flag'] = 1;
		return render_template('search_user.html',res=res)
	else:
		resp = jsonify("Not login")
		return resp

@app.route('/following')
def following():
	if 'login_email' in session:
		user1_id = session['login_id']
		cur = CONN.cursor()
		cur.execute("select username,user2_id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.follows,weibo.users where user1_id=%s and weibo.follows.user2_id=weibo.users.id", [user1_id,user1_id])
		res = cur.fetchall()
		session['flag'] = 2;
		return render_template('search_user.html',res=res)
	else:
		resp = jsonify("Not login")
		return resp

@app.route('/follower')
def follower():
	if 'login_email' in session:
		user2_id = session['login_id']
		cur = CONN.cursor()
		cur.execute("select username,user1_id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.follows,weibo.users where user2_id=%s and weibo.follows.user1_id=weibo.users.id", [user2_id,user2_id])
		res = cur.fetchall()
		session['flag'] = 3;
		return render_template('search_user.html',res=res)
	else:
		resp = jsonify("Not login")
		return resp

@app.route('/follow/<user2_id>')
def follow(user2_id):
	if 'login_email' in session:
		user1_id = session['login_id']
		cur = CONN.cursor()
		try:
			cur.execute("insert into weibo.follows(user1_id,user2_id) values(%s,%s)",[user1_id,user2_id])
			CONN.commit()
		except Exception as err:
			CONN.rollback()
			return jsonify('already followed')
		if (session['flag'] == 1):
			cur.execute("select username,id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.users where username like %s order by username", [session['login_id'], '%' + session['search_email'] + '%'])
		elif (session['flag'] == 2):
			cur.execute("select username,user2_id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.follows,weibo.users where user1_id=%s and weibo.follows.user2_id=weibo.users.id", [user1_id,user1_id])
		else:
			cur.execute("select username,user1_id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.follows,weibo.users where user2_id=%s and weibo.follows.user1_id=weibo.users.id", [user1_id,user1_id])
		res = cur.fetchall()
		return render_template('search_user.html',res=res)
	else:
		resp = jsonify("Not login")
		return resp
	
@app.route('/unfollow/<user2_id>')
def unfollow(user2_id):
	if 'login_email' in session:
		user1_id = session['login_id']
		cur = CONN.cursor()
		cur.execute("delete from weibo.follows where user1_id=%s and user2_id=%s",[user1_id,user2_id])
		CONN.commit()
		if cur.rowcount == 0:
			return jsonify('already unfollowed')
		if (session['flag'] == 1):
			cur.execute("select username,id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.users where username like %s order by username", [session['login_id'], '%' + session['search_email'] + '%'])
		elif (session['flag'] == 2):
			cur.execute("select username,user2_id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.follows,weibo.users where user1_id=%s and weibo.follows.user2_id=weibo.users.id", [user1_id,user1_id])
		else:
			cur.execute("select username,user1_id,(select 1 from weibo.follows where user1_id = %s and weibo.users.id=user2_id) as is_follow from weibo.follows,weibo.users where user2_id=%s and weibo.follows.user1_id=weibo.users.id", [user1_id,user1_id])
		res = cur.fetchall()
		return render_template('search_user.html',res=res)
	else:
		resp = jsonify("Not login")
		return resp

@app.route('/edit_post/<int:post_id>',methods=['GET'])
def edit_post(post_id):
	if 'login_email' not in session:
		return redirect("http://localhost:8888")
	cur = CONN.cursor()
	cur.execute('select content from weibo.posts where id=%s',[post_id])
	content = cur.fetchone()[0]
	return render_template('editpost.html',post_id=post_id,content=content)
	
@app.route('/edit_post',methods=['POST'])
def do_edit_post():
	if 'login_email' in session:
		content = request.form['content'].strip()
		post_id = request.form['post_id']
		if len(content) == 0:
			resp = jsonify("You must type some letters in content")
			return resp
		cur = CONN.cursor()
		cur.execute("update weibo.posts set content=%s where id=%s and user_id=%s", [content,post_id,session['login_id']])
		CONN.commit()
		if cur.rowcount == 0:
			resp = jsonify("You can not update other's post!")
		else:
			resp = jsonify("success")
	else:
		resp = jsonify("Not login")
	return resp

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
	if 'login_email' in session:
		cur = CONN.cursor()
		cur.execute("delete from weibo.posts where id=%s and user_id=%s",[post_id,session['login_id']])
		CONN.commit()
		if cur.rowcount == 0:
			resp = jsonify("You can not delete other's post!")
			return resp
		else:
			return redirect('/home')
	else:
		resp = jsonify("Not login")
		return resp

@app.route('/like_post/<int:post_id>')
def like_post(post_id):
	if 'login_email' in session:
		cur = CONN.cursor()
		try:
			cur.execute("insert into weibo.like_posts(user_id,post_id) values (%s,%s)",[session['login_id'],post_id])
			CONN.commit()
			return redirect('/home')
		except Exception as err:
			CONN.rollback()
			resp = jsonify("already liked!")
	else:
		resp = jsonify("Not login")
	return resp
	
@app.route('/unlike_post/<int:post_id>')
def unlike_post(post_id):
	if 'login_email' in session:
		cur = CONN.cursor()
		cur.execute("delete from weibo.like_posts where user_id=%s and post_id=%s",[session['login_id'],post_id])
		CONN.commit()
		if cur.rowcount == 0:
			resp = jsonify("already unliked!")
		else:
			return redirect('/home')
	else:
		resp = jsonify("Not login")
	return resp

@app.route('/add_comment/<int:post_id>',methods=['POST'])
def add_comment(post_id):
	if 'login_email' in session:
		comment = request.form['comment'].strip()
		if len(comment) > 0:
			cur = CONN.cursor()
			cur.execute("insert into weibo.comments(user_id,post_id,content) values (%s,%s,%s)",[session['login_id'],post_id,comment])
			CONN.commit()
			return redirect('/home')
		else:
			resp = jsonify("You must type some letters in content")
	else:
		resp = jsonify("Not login")
	return resp

@app.route('/like_comment/<int:comment_id>')
def like_comment(comment_id):
	if 'login_email' in session:
		cur = CONN.cursor()
		try:
			cur.execute("insert into weibo.like_comments(user_id,comment_id) values (%s,%s)",[session['login_id'],comment_id])
			CONN.commit()
			return redirect('/home')
		except Exception as err:
			CONN.rollback()
			resp = jsonify("already liked!")
	else:
		resp = jsonify("Not login")
	return resp

@app.route('/unlike_comment/<int:comment_id>')
def unlike_comment(comment_id):
	if 'login_email' in session:
		cur = CONN.cursor()
		cur.execute("delete from weibo.like_comments where user_id=%s and comment_id=%s",[session['login_id'],comment_id])
		CONN.commit()
		if cur.rowcount == 0:
			resp = jsonify("already unliked!")
		else:
			return redirect('/home')
	else:
		resp = jsonify("Not login")
	return resp
	
@app.route('/edit_comment/<int:comment_id>',methods=['GET'])
def edit_comment(comment_id):
	if 'login_email' not in session:
		return redirect("http://localhost:8888")
	cur = CONN.cursor()
	cur.execute('select content from weibo.comments where id=%s',[comment_id])
	content = cur.fetchone()[0]
	return render_template('editcomment.html',comment_id=comment_id,content=content)
	
@app.route('/edit_comment',methods=['POST'])
def do_edit_comment():
	if 'login_email' in session:
		content = request.form['content'].strip()
		comment_id = request.form['comment_id']
		if len(content) == 0:
			resp = jsonify("You must type some letters in content")
			return resp
		cur = CONN.cursor()
		cur.execute("update weibo.comments set content=%s where id=%s and user_id=%s", [content,comment_id,session['login_id']])
		CONN.commit()
		if cur.rowcount == 0:
			resp = jsonify("You can not update other's comment!")
		else:
			resp = jsonify("success")
	else:
		resp = jsonify("Not login")
	return resp

@app.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
	if 'login_email' in session:
		cur = CONN.cursor()
		cur.execute("delete from weibo.comments where id=%s and user_id=%s",[comment_id,session['login_id']])
		CONN.commit()
		if cur.rowcount == 0:
			resp = jsonify("You can not delete other's comment!")
			return resp
		else:
			return redirect('/home')
	else:
		resp = jsonify("Not login")
		return resp

def valid_email(email):
	if re.match("^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$",email) == None:
		return 0
	else:
		return 1

def valid_pass(password):
	if len(password) < 6:
		return 0
	else:
		return 1

def valid_user(email, password):
	cur = CONN.cursor()
	try:
		cur.execute("select password from weibo.users where username=%s", (email, ))
		res = cur.fetchone()[0]
	except Exception as err:
		return 0
	if(bcrypt.check_password_hash(res,password) == True):
		return 1
	else:
		return 0

def insert_user(email, password):
	cur = CONN.cursor()
	try:
		password = bcrypt.generate_password_hash(password).decode('utf-8')
		cur.execute("insert into weibo.users (username, password) values (%s, %s)", (email, password))
		CONN.commit()
	except Exception as err:
		CONN.rollback()
		return 0
	return cur.rowcount

def select_post(user_id):
	cur = CONN.cursor()
	cur.execute("select (select username from weibo.users where id=user_id),id,content,created_at,liked_count,(select 1 from weibo.like_posts where user_id=%s and post_id=weibo.posts.id) as is_liked from weibo.posts where user_id=%s or user_id in (select user2_id from weibo.follows where user1_id=%s) order by created_at desc", [user_id, user_id, user_id])
	return cur.fetchall()

def select_comment(user_id):
	cur = CONN.cursor()
	cur.execute("select id,(select username from weibo.users where id=user_id),post_id,created_at,content,liked_count,(select 1 from weibo.like_comments where user_id=%s and comment_id=weibo.comments.id) as is_liked from weibo.comments order by created_at desc", [user_id,])
	return cur.fetchall()
	
def insert_post(user_id, content):
	cur = CONN.cursor()
	if len(content) > 0:
		cur.execute("insert into weibo.posts (user_id,content) values (%s,%s)", (user_id, content))
		CONN.commit()
		return 1
	else:
		return 0
		
def update_passwd(user_id, oldpwd, newpwd):
	cur = CONN.cursor()
	cur.execute("select password from weibo.users where id=%s", (user_id, ))
	res = cur.fetchone()[0]
	if(bcrypt.check_password_hash(res,oldpwd) == True):
		newpwd = bcrypt.generate_password_hash(newpwd).decode('utf-8')
		cur.execute("update weibo.users set password=%s where id=%s", (newpwd,user_id))
		CONN.commit()
		return 1
	else:
		return 0

def select_userid(username):
	cur = CONN.cursor()
	cur.execute("select id from weibo.users where username=%s", (username,))
	return cur.fetchone()[0]

def select_count(username):
	cur = CONN.cursor()
	cur.execute("select post_count,followers_count,followings_count from weibo.users where username=%s", (username,))
	return cur.fetchone()

if __name__ == '__main__':
	set_dbname_normal()
else:
	set_dbname_test()
CONN = connect_db()
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8888)

