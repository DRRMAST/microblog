DROP SCHEMA weibo CASCADE;
CREATE SCHEMA weibo;

CREATE TABLE weibo.USERS (
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	password TEXT NOT NULL,
	post_count INTEGER NOT NULL DEFAULT 0,
	followers_count INTEGER NOT NULL DEFAULT 0,
	followings_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE weibo.POSTS (
	id SERIAL PRIMARY KEY,
	user_id BIGINT REFERENCES weibo.users(id),
	post_id BIGINT REFERENCES weibo.posts(id),
	created_at TIMESTAMPTZ DEFAULT now(),
	content TEXT NOT NULL DEFAULT '',
	liked_count INTEGER NOT NULL DEFAULT 0,
	repost_count INTEGER NOT NULL DEFAULT 0,
	comments_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE weibo.COMMENTS (
	id SERIAL PRIMARY KEY,
	user_id BIGINT REFERENCES weibo.users(id),
	post_id BIGINT REFERENCES weibo.posts(id),
	comment_id BIGINT REFERENCES weibo.comments(id),
	created_at TIMESTAMPTZ DEFAULT now(),
	content TEXT NOT NULL DEFAULT '',
	liked_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE weibo.LIKE_POSTS (
	id SERIAL PRIMARY KEY,
	user_id BIGINT REFERENCES weibo.users(id),
	post_id BIGINT REFERENCES weibo.posts(id),
	created_at TIMESTAMPTZ DEFAULT now(),
	UNIQUE (user_id, post_id)
);

CREATE TABLE weibo.LIKE_COMMENTS (
	id SERIAL PRIMARY KEY,
	user_id BIGINT REFERENCES weibo.users(id),
	comment_id BIGINT REFERENCES weibo.comments(id),
	created_at TIMESTAMPTZ DEFAULT now(),
	UNIQUE (user_id, comment_id)
);

CREATE TABLE weibo.FOLLOWS (
	id SERIAL PRIMARY KEY,
	user1_id BIGINT REFERENCES weibo.users(id),
	user2_id BIGINT REFERENCES weibo.users(id),
	UNIQUE (user1_id, user2_id)
);

CREATE UNIQUE INDEX index_username on weibo.users (username);

CREATE OR REPLACE FUNCTION post_count_procedure() RETURNS TRIGGER AS $$
DECLARE
    v_post_count INTEGER;
BEGIN
    IF ( TG_OP = 'INSERT' ) THEN
        SELECT INTO v_post_count COUNT(*) FROM weibo.posts WHERE user_id = NEW.user_id;
        UPDATE weibo.users SET post_count = v_post_count WHERE id = NEW.user_id;
        RETURN NEW;
    ELSIF ( TG_OP = 'DELETE' ) THEN
        SELECT INTO v_post_count COUNT(*) FROM weibo.posts WHERE user_id = OLD.user_id;
        UPDATE weibo.users SET post_count = v_post_count WHERE id = OLD.user_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER post_count_trigger AFTER INSERT OR DELETE ON weibo.posts
FOR EACH ROW EXECUTE PROCEDURE post_count_procedure();

CREATE OR REPLACE FUNCTION followers_count_procedure() RETURNS TRIGGER AS $$
DECLARE
	v_followers_count INTEGER;
BEGIN
	IF ( TG_OP = 'INSERT' ) THEN
		SELECT INTO v_followers_count COUNT(*) FROM weibo.follows WHERE user2_id = NEW.user2_id;
		UPDATE weibo.users SET followers_count = v_followers_count WHERE id = NEW.user2_id;
		RETURN NEW;
	ELSIF ( TG_OP = 'DELETE' ) THEN
		SELECT INTO v_followers_count COUNT(*) FROM weibo.follows WHERE user2_id = OLD.user2_id;
		UPDATE weibo.users SET followers_count = v_followers_count WHERE id = OLD.user2_id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER followers_count_trigger AFTER INSERT OR DELETE ON weibo.follows
FOR EACH ROW EXECUTE PROCEDURE followers_count_procedure();

CREATE OR REPLACE FUNCTION followings_count_procedure() RETURNS TRIGGER AS $$
DECLARE
	v_followings_count INTEGER;
BEGIN
	IF ( TG_OP = 'INSERT' ) THEN
		SELECT INTO v_followings_count COUNT(*) FROM weibo.follows WHERE user1_id = NEW.user1_id;
		UPDATE weibo.users SET followings_count = v_followings_count WHERE id = NEW.user1_id;
		RETURN NEW;
	ELSIF ( TG_OP = 'DELETE' ) THEN
		SELECT INTO v_followings_count COUNT(*) FROM weibo.follows WHERE user1_id = OLD.user1_id;
		UPDATE weibo.users SET followings_count = v_followings_count WHERE id = OLD.user1_id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER followings_count_trigger AFTER INSERT OR DELETE ON weibo.follows
FOR EACH ROW EXECUTE PROCEDURE followings_count_procedure();

CREATE OR REPLACE FUNCTION liked_post_count_procedure() RETURNS TRIGGER AS $$
DECLARE
	v_liked_count INTEGER;
BEGIN
	IF ( TG_OP = 'INSERT' ) THEN
		SELECT INTO v_liked_count COUNT(*) FROM weibo.like_posts where post_id = NEW.post_id;
		UPDATE weibo.posts SET liked_count = v_liked_count WHERE id = NEW.post_id;
		RETURN NEW;
	ELSIF ( TG_OP = 'DELETE' ) THEN
		SELECT INTO v_liked_count COUNT(*) FROM weibo.like_posts where post_id = OLD.post_id;
		UPDATE weibo.posts SET liked_count = v_liked_count WHERE id = OLD.post_id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER liked_post_count_trigger AFTER INSERT OR DELETE ON weibo.like_posts
FOR EACH ROW EXECUTE PROCEDURE liked_post_count_procedure();

CREATE OR REPLACE FUNCTION liked_comment_count_procedure() RETURNS TRIGGER AS $$
DECLARE
	v_liked_count INTEGER;
BEGIN
	IF ( TG_OP = 'INSERT' ) THEN
		SELECT INTO v_liked_count COUNT(*) FROM weibo.like_comments where comment_id = NEW.comment_id;
		UPDATE weibo.comments SET liked_count = v_liked_count WHERE id = NEW.comment_id;
		RETURN NEW;
	ELSIF ( TG_OP = 'DELETE' ) THEN
		SELECT INTO v_liked_count COUNT(*) FROM weibo.like_comments where comment_id = OLD.comment_id;
		UPDATE weibo.comments SET liked_count = v_liked_count WHERE id = OLD.comment_id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER liked_comment_count_trigger AFTER INSERT OR DELETE ON weibo.like_comments
FOR EACH ROW EXECUTE PROCEDURE liked_comment_count_procedure();

CREATE OR REPLACE FUNCTION delete_comment_procedure() RETURNS TRIGGER AS $$
BEGIN
	IF ( TG_OP = 'DELETE' ) THEN
		DELETE FROM weibo.like_comments where comment_id = OLD.id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER delete_comment_trigger BEFORE DELETE ON weibo.comments
FOR EACH ROW EXECUTE PROCEDURE delete_comment_procedure();

CREATE OR REPLACE FUNCTION delete_post_procedure() RETURNS TRIGGER AS $$
BEGIN
	IF ( TG_OP = 'DELETE' ) THEN
		DELETE FROM weibo.like_posts where post_id = OLD.id;
		DELETE FROM weibo.comments where post_id = OLD.id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER delete_post_trigger BEFORE DELETE ON weibo.posts
FOR EACH ROW EXECUTE PROCEDURE delete_post_procedure();

CREATE OR REPLACE FUNCTION delete_user_procedure() RETURNS TRIGGER AS $$
BEGIN
	IF ( TG_OP = 'DELETE' ) THEN
		DELETE FROM weibo.posts where user_id = OLD.id;
		DELETE FROM weibo.follows where user1_id = OLD.id;
		DELETE FROM weibo.follows where user2_id = OLD.id;
		RETURN OLD;
	END IF;
    RETURN NULL;
END; $$
LANGUAGE plpgsql;

CREATE TRIGGER delete_user_trigger BEFORE DELETE ON weibo.users
FOR EACH ROW EXECUTE PROCEDURE delete_user_procedure();
