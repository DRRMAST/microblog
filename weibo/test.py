import unittest
import index

class Test(unittest.TestCase):
	def setUp(self):
		index.app.testing = True
		self.app = index.app.test_client()
		with index.app.app_context():
			index.set_dbname_test()
		self.register("toto@gmail.com","12345678","12345678")
		self.register("titi@gmail.com","12345678","12345678")
		self.register("tata@gmail.com","12345678","12345678")
		with index.app.app_context():
			conn = index.get_db()
			cursor = conn.cursor()
			cursor.execute('select id from weibo.users where username = \'toto@gmail.com\'')
			self.toto_id = cursor.fetchone()[0]
			self.titi_id = self.toto_id + 1
			self.tata_id = self.titi_id + 1
	
	def tearDown(self):
		self.logout()
	
	def cleardb(self):
		with index.app.app_context():
			conn = index.get_db()
			cursor = conn.cursor()
			cursor.execute('TRUNCATE TABLE weibo.USERS CASCADE')
			cursor.execute('TRUNCATE TABLE weibo.POSTS CASCADE')
			cursor.execute('TRUNCATE TABLE weibo.COMMENTS CASCADE')
			cursor.execute('TRUNCATE TABLE weibo.LIKE_POSTS CASCADE')
			cursor.execute('TRUNCATE TABLE weibo.LIKE_COMMENTS CASCADE')
			cursor.execute('TRUNCATE TABLE weibo.FOLLOWS CASCADE')
			conn.commit()
			conn.close()
		
	def register(self, email, password, confirm):
		return self.app.post('/registration', data=dict(email=email,password=password,confirm=confirm),follow_redirects=True)
		
	def login(self, email, password):
		return self.app.post('/login', data=dict(email=email,password=password),follow_redirects=True)
	
	def logout(self):
		return self.app.post('/logout', follow_redirects=True)
	
	def post(self,content):
		return self.app.post('/home', data=dict(content=content),follow_redirects=True)
		
	def changepwd(self, oldpwd, newpwd, confirm):
		return self.app.post('/changepwd', data=dict(oldpwd=oldpwd, newpwd=newpwd, confirm=confirm),follow_redirects=True)
		
	def search_user(self, search):
		return self.app.post('/search_user',data=dict(search=search),follow_redirects=True)
		
	def list_following(self):
		return self.app.get('/following', data=dict(), follow_redirects=True)
		
	def list_follower(self):
		return self.app.get('/follower', data=dict(), follow_redirects=True)
		
	def follow(self, userid):
		return self.app.get('/follow/' + str(userid), data=dict(), follow_redirects=True)
		
	def unfollow(self, userid):
		return self.app.get('/unfollow/' + str(userid), data=dict(), follow_redirects=True)
		
	def get_postid(self, userid, content):
		with index.app.app_context():
			conn = index.get_db()
			cursor = conn.cursor()
			cursor.execute('select id from weibo.posts where user_id=%s and content=%s',[userid,content])
			return cursor.fetchone()[0]
			
	def edit_post(self, post_id, content):
		return self.app.post('/edit_post', data=dict(post_id=post_id,content=content),follow_redirects=True)
		
	def delete_post(self, post_id):
		return self.app.get('/delete_post/' + str(post_id), data=dict(), follow_redirects=True)
		
	def like_post(self, post_id):
		return self.app.get('/like_post/' + str(post_id), data=dict(), follow_redirects=True)
		
	def unlike_post(self, post_id):
		return self.app.get('/unlike_post/' + str(post_id), data=dict(), follow_redirects=True)
		
	def test_register_invalid_email_invalid_pass(self):
		res = self.register("sdfsd@g mail.com","123","123")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		
	def test_register_invalid_email_valid_pass(self):
		res = self.register("sdfs d@gmail.com","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdfsd@g mail.com","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdfsd@gmail.c om","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("@.","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("@gmail.com","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdf@.com","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdf@gmail.","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdf@gmail.come","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdf@gmail.c","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdf@gmailcom","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		res = self.register("sdfgmail.com","12345678","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		
	def test_register_valid_email_invalid_pass(self):
		res = self.register("toto1@gmail.com","123","123")
		self.assertEqual(res.data,b'"Password should at least 6 characters"\n')
		res = self.register("toto1@gmail.com","","")
		self.assertEqual(res.data,b'"Password should at least 6 characters"\n')
		res = self.register("toto1@gmail.com","12345678","123456789")
		self.assertEqual(res.data,b'"Your password can\'t be confirmed"\n')
		
	def test_register_valid_email_valid_pass(self):
		res = self.register("toto1@gmail.com          ","12345678","12345678")
		self.assertEqual(res.data,b'"success"\n')
		res = self.register("          toto2@gmail.com","12345678","12345678")
		self.assertEqual(res.data,b'"success"\n')
		res = self.register("toto3@gmail.com","12345678","12345678")
		self.assertEqual(res.data,b'"success"\n')
		res = self.register("      toto4@gmail.com     ","12345678","12345678")
		self.assertEqual(res.data,b'"success"\n')
		self.cleardb()
		
	def test_register_duplicated_valid_email_valid_pass(self):
		res = self.register("toto@gmail.com    ","12345678","12345678")
		self.assertEqual(res.data,b'"Email already exist"\n')
	
	def test_login_invalid_email(self):
		res = self.login("   totogmail.com   ","12345678")
		self.assertEqual(res.data,b'"Invalid e-mail address"\n')
		
	def test_login_invalid_pass(self):
		res = self.login("   toto@gmail.com   ","1234")
		self.assertEqual(res.data,b'"Password should at least 6 characters"\n')
		
	def test_login_correct(self):
		res = self.login("   toto@gmail.com   ","12345678")
		self.assertEqual(res.data,b'"success"\n')
		
	def test_login_incorrect_pass(self):
		res = self.login("toto@gmail.com","123456789")
		self.assertEqual(res.data,b'"incorrect email or password"\n')
	
	def test_login_incorrect_email(self):
		res = self.login("totototo@gmail.com","123456789")
		self.assertEqual(res.data,b'"incorrect email or password"\n')
		
	def test_logout_correct(self):
		self.login("   toto@gmail.com   ","12345678")
		res = self.logout()
		self.assertEqual(res.data,b'"success"\n')
	
	def test_post_invalid(self):
		self.login("toto@gmail.com","12345678")
		res = self.post("   ")
		self.assertEqual(res.data,b'"You must type some letters in content"\n')
		res = self.post("")
		self.assertEqual(res.data,b'"You must type some letters in content"\n')
		
	def test_post_valid(self):
		self.login("toto@gmail.com","12345678")
		res = self.post("  This is a post  ")
		self.assertEqual(res.data,b'"success"\n')
		self.cleardb()
		
	def test_post_not_login(self):
		res = self.post("  This is a post  ")
		self.assertEqual(res.data,b'"Not login"\n')
		
	def test_changepwd_incorrect_oldpwd(self):
		self.login("toto@gmail.com","12345678")
		res = self.changepwd("123456789","87654321","87654321")
		self.assertEqual(res.data,b'"Your Old Password is Wrong"\n')
		res = self.changepwd("","87654321","87654321")
		self.assertEqual(res.data,b'"Password should at least 6 characters"\n')
		
	def test_changepwd_invalid_newpwd(self):
		self.login("toto@gmail.com","12345678")
		res = self.changepwd("12345678","8765","8765")
		self.assertEqual(res.data,b'"Password should at least 6 characters"\n')
	
	def test_changepwd_not_confirm(self):
		self.login("toto@gmail.com","12345678")
		res = self.changepwd("12345678","87654321","87653421")
		self.assertEqual(res.data,b'"Your password can\'t be confirmed"\n')
		
	def test_changepwd_correct(self):
		res = self.login("toto@gmail.com","12345678")
		res = self.changepwd("12345678","87654321","87654321")
		self.assertEqual(res.data,b'"success"\n')
		self.logout()
		res = self.login("toto@gmail.com","12345678")
		self.assertEqual(res.data,b'"incorrect email or password"\n')
		res = self.login("toto@gmail.com","87654321")
		self.assertEqual(res.data,b'"success"\n')
		self.changepwd("87654321","12345678","12345678")
		self.logout()
		
	def test_changepwd_not_login(self):
		res = self.changepwd("12345678","87654321","87654321")
		self.assertEqual(res.data,b'"Not login"\n')
		
	def test_follow_and_unfollow_user(self):
		self.login("toto@gmail.com","12345678")
		res = self.search_user("titi")
		assert b'Follow' in res.data
		res = self.follow(self.titi_id)
		assert b'Unfollow' in res.data
		res = self.unfollow(self.titi_id)
		assert b'Follow' in res.data
		
	def test_follow_and_unfollow_user_not_login(self):
		res = self.search_user("titi")
		self.assertEqual(res.data,b'"Not login"\n')
		res = self.follow(self.titi_id)
		self.assertEqual(res.data,b'"Not login"\n')
		res = self.unfollow(self.titi_id)
		self.assertEqual(res.data,b'"Not login"\n')
		
	def test_follow_and_unfollow_user_duplicated(self):
		self.login("toto@gmail.com","12345678")
		self.search_user("titi")
		self.follow(self.titi_id)
		res = self.follow(self.titi_id)
		self.assertEqual(res.data,b'"already followed"\n')
		self.unfollow(self.titi_id)
		res = self.unfollow(self.titi_id)
		self.assertEqual(res.data,b'"already unfollowed"\n')
		
	def test_search_user(self):
		self.login("toto@gmail.com","12345678")
		res = self.search_user("titi")
		assert b'titi@gmail.com' in res.data
		res = self.search_user("tata")
		assert b'tata@gmail.com' in res.data
		res = self.search_user("t")
		assert b'toto@gmail.com' in res.data
		assert b'titi@gmail.com' in res.data
		assert b'tata@gmail.com' in res.data
		
	def test_search_user_not_exist(self):
		self.login("toto@gmail.com","12345678")
		res = self.search_user("abc")
		assert b'no result!' in res.data
		
	def test_search_user_not_login(self):
		res = self.search_user("toto")
		assert b'Not login' in res.data
		
	def test_list_follower(self):
		self.login("toto@gmail.com","12345678")
		self.search_user("titi")
		self.follow(self.titi_id)
		self.logout()
		self.login("titi@gmail.com","12345678")
		res = self.list_follower()
		assert b'toto@gmail.com' in res.data
		self.logout()
		self.login("toto@gmail.com","12345678")
		self.search_user("titi")
		self.unfollow(self.titi_id)
		self.logout()
		self.login("titi@gmail.com","12345678")
		res = self.list_follower()
		assert b'no result!' in res.data
		
	def test_list_follower_not_login(self):
		res = self.list_follower()
		assert b'Not login' in res.data
		
	def test_list_following(self):
		self.login("toto@gmail.com","12345678")
		self.search_user("titi")
		self.follow(self.titi_id)
		res = self.list_following()
		assert b'titi@gmail.com' in res.data
		self.unfollow(self.titi_id)
		res = self.list_following()
		assert b'no result!' in res.data
		
	def test_list_following_not_login(self):
		res = self.list_following()
		assert b'Not login' in res.data
		
	def test_edit_post(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		res = self.edit_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"),"Hello!I am toto!")
		self.assertEqual(res.data,b'"success"\n')
		self.cleardb()
		
	def test_edit_post_invalid(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		res = self.edit_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"),"")
		self.assertEqual(res.data,b'"You must type some letters in content"\n')
		res = self.edit_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"),"     ")
		self.assertEqual(res.data,b'"You must type some letters in content"\n')
		self.cleardb()
		
	def test_edit_post_not_login(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		self.logout()
		res = self.edit_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"),"Hello!I am toto!")
		self.assertEqual(res.data,b'"Not login"\n')
		self.cleardb()
		
	def test_edit_other_user_post(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		self.logout()
		self.login("tata@gmail.com","12345678")
		res = self.edit_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"),"Hello!I am toto!")
		self.assertEqual(res.data,b'"You can not update other\'s post!"\n')
		self.cleardb()
		
	def test_delete_post(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		res = self.delete_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		assert b'Bonjour!Je suis toto!' not in res.data
		
	def test_delete_other_user_post(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		self.logout()
		self.login("tata@gmail.com","12345678")
		res = self.delete_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		self.assertEqual(res.data,b'"You can not delete other\'s post!"\n')
		self.cleardb()
		
	def test_delete_post_not_login(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		self.logout()
		res = self.delete_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		self.assertEqual(res.data,b'"Not login"\n')
		self.cleardb()
		
	def test_like_and_unlike_post(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		res = self.like_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		assert b'unlike(1)' in res.data
		res = self.unlike_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		assert b'like(0)' in res.data
		self.login("toto@gmail.com","12345678")
		self.delete_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		
	def test_like_and_unlike_post_not_login(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		self.logout()
		res = self.like_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		self.assertEqual(res.data,b'"Not login"\n')
		res = self.unlike_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		self.assertEqual(res.data,b'"Not login"\n')
		self.cleardb()
		
	def test_like_and_unlike_post_duplicated(self):
		self.login("toto@gmail.com","12345678")
		self.post("  Bonjour!Je suis toto!  ")
		self.like_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		res = self.like_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		self.assertEqual(res.data,b'"already liked!"\n')
		self.unlike_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		res = self.unlike_post(self.get_postid(self.toto_id,"Bonjour!Je suis toto!"))
		self.assertEqual(res.data,b'"already unliked!"\n')
		
if __name__=='__main__':
	unittest.main(verbosity=2)
