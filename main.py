# -*- coding: utf-8 -*-

import os
import sys
import datetime
import peewee
import web

reload(sys)
sys.setdefaultencoding('utf8')

DB = peewee.MySQLDatabase('myv2ex', host='127.0.0.1', port=3306, user='root', passwd='123456')
DB.connect()


class BaseModel(peewee.Model):
    class Meta:
        database = DB


class Posts(BaseModel):
    id = peewee.IntegerField()
    title = peewee.TextField()
    content = peewee.TextField()
    created = peewee.DateTimeField()
    user_id = peewee.IntegerField()


class Users(BaseModel):
    id = peewee.IntegerField
    username = peewee.CharField()
    passwd = peewee.TextField()
    email = peewee.TextField()
    join_time = peewee.DateTimeField()
    last_login = peewee.DateTimeField()


class Comments(BaseModel):
    id = peewee.IntegerField()
    content = peewee.TextField()
    time = peewee.DateTimeField()
    user_id = peewee.IntegerField()
    username = peewee.CharField()
    post_id = peewee.IntegerField()

urls = (
    '/', 'HomeHandler',
    '/signup', 'SignupHandler',
    '/signin', 'SigninHandler',
    '/signout', 'SignoutHandler',
    '/u/(\w+)', 'UserHandler',
    '/create', 'CreateHandler',
    '/t/(\d+)', 'PostHandler',
    '/edit/(\d+)', 'EditHandler',
    '/del/(\d+)', 'DeleteHandler',
    '/daily/(\w+)', 'DailyHandler'
)


render = web.template.render(os.path.join(os.path.dirname(__file__), 'templates'), base='base')
render_plain = web.template.render(os.path.join(os.path.dirname(__file__), 'templates'))


def render_login(user):
    return web.template.render(os.path.join(os.path.dirname(__file__), 'templates'), base='base_logined', globals={'user': user})


def current_user():
    user = web.cookies().get('userid')
    username = ''
    if user:
        web.setcookie('userid', user, 600)
        username = Users.get(Users.id == user).username
    return user, username


class App(web.application):
    def run(self, port=9999, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


class HomeHandler(web.application):
    def GET(self):
        records = Posts.select().order_by(Posts.id.desc()).limit(30)
        posts = []

        for record in records:
            author = Users.get(Users.id == record.user_id).username
            comments = Comments.select().where(Comments.post_id == record.id)
            comment_num = comments.count()
            last_comment = comments.order_by(Comments.time.desc()).first()
            if not last_comment:
                last_comment_user = ''
            else:
                last_comment_user = Users.get(Users.id == last_comment.user_id).username
            posts.append([record.title, record.id, author, record.created, last_comment_user, comment_num])
        # title, id, author
        uid, user = current_user()
        daily_mission = False
        if user:
            last = Users.get(Users.username == user).last_login
            today = datetime.datetime.now()
            if today.year == last.year and today.month == last.month and today.day == last.day:
                daily_mission = False
            else:
                daily_mission = True

            return render_login(user).home(posts, user, daily_mission)
        else:
            return render.home(posts, '', daily_mission)


class SignupHandler(web.application):
    def GET(self):
        return render.signup()

    def POST(self):
        i = web.input()
        #TODO: 后台安全检查
        if i.username and i.password and i.email:
            join_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                Users.create(username=i.username, passwd=i.password, email=i.email, join_time=join_time)
            except:
                print 'err'
        raise web.seeother('/')


class SigninHandler(web.application):
    def GET(self):
        return render.signin('')

    def POST(self):
        i = web.input()

        user_exist = Users.select().where(Users.username == i.username, Users.passwd == i.password)
        if user_exist:
            user_id = user_exist.first().id

            web.setcookie('userid', user_id, 600)
            raise web.seeother('/')
        else:
            info = '用户名密码不匹配'
            return render.signin(info)


class SignoutHandler(web.application):
    def GET(self):
        web.setcookie('userid', '', -1)
        raise web.seeother('/')


class UserHandler(web.application):
    def GET(self, user):
        uid, login = current_user()
        u_record = Users.get(Users.username == user)
        user_id = u_record.id
        join_time = u_record.join_time
        records = Posts.select().where(Posts.user_id == user_id).order_by(Posts.created.desc())
        posts = []
        for record in records:
            author = Users.get(Users.id == record.user_id).username
            comments = Comments.select().where(Comments.post_id == record.id)
            comment_num = comments.count()
            last_comment = comments.order_by(Comments.time.desc()).first()
            if not last_comment:
                last_comment_user = ''
            else:
                last_comment_user = Users.get(Users.id == last_comment.user_id).username
            posts.append([record.title, record.id, author, record.created, last_comment_user, comment_num])
        if login:
            return render_login(user).user(user, posts, join_time)
        else:
            return render.user(user, posts, join_time)


class CreateHandler(web.application):
    def GET(self):
        uid, login = current_user()
        if login:
            return render_login(login).create()
        else:
            return render.unauthorized('无权限，请先<a href="/signin">登录</a>')

    def POST(self):
        uid, login = current_user()
        if not login:
            return render.unauthorized('无权限，请先<a href="/signin">登录</a>')
        user_id = Users.get(Users.username == login).id
        i = web.input()
        created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        post = Posts.create(title=i.title, content=i.content, user_id=user_id, created=created)

        raise web.seeother('/t/%s' % post.id)


class PostHandler(web.application):
    def GET(self, pid):
        uid, login = current_user()
        post = Posts.get(Posts.id == pid)
        if not post:
            raise web.notfound()

        title = post.title
        content = post.content
        created = post.created
        authorname = Users.get(Users.id == post.user_id).username

        comment_records = Comments.select().where(Comments.post_id == pid).order_by(Comments.time)
        comments = []
        for r in comment_records:
            comments.append(r)
        if login:
            return render_login(login).post(title, content, created, authorname, login, pid, comments)
        else:
            return render.post(title, content, created, authorname, '', id, comments)

    def POST(self, pid):
        uid, reply_user = current_user()
        if not uid:
            return render.unauthorized('只有登录用户才可以回复，请先<a href="/signin">登录</a>')
        i = web.input()
        reply_content = i.content
        created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if i.content:
            Comments.create(content=reply_content, time=created, user_id=uid, username=reply_user, post_id=pid)
        raise web.seeother('/t/%s' % pid)


class DeleteHandler(web.application):
    def GET(self, id):
        uid, user = current_user()
        if not user:
            render.unauthorized('无权限，请先<a href="/signin">登录</a>')
        try:
            user_id = Posts.get(Posts.id == id).user_id
        except:
            # TODO: 帖子不存在处理
            pass
        else:
            if user_id != uid:
                render_login(user).unauthorized('这是别人的帖子，你不能删除。')
            Posts.delete().where(Posts.id == id).execute()
            raise web.seeother('/')


class DailyHandler(web.application):
    def GET(self, user):
        uid, c_user = current_user()
        if c_user == user:
            user_record = Users.get(Users.username == user)
            last = user_record.last_login
            today = datetime.datetime.now()
            daily_mission = True
            if today.year == last.year and today.month == last.month and today.day == last.day:
                daily_mission = False
            if daily_mission:
                new_last_login = today.strftime('%Y-%m-%d %H:%M:%S')
                user_record.last_login = new_last_login
                user_record.save()
                raise web.seeother('/')
            else:
                raise web.notfound()
        else:
            raise web.notfound()



if __name__ == '__main__':
    app = App(urls, globals())
    app.run()