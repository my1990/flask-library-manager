
from flask import Flask, request, session, url_for, redirect, \
	 render_template, abort, g, flash, _app_ctx_stack
import time,pymysql

app = Flask(__name__)
CSPR_ENABLED = True # 启用 CSPR (跨站请求伪造) 保护，在表单中使用，隐藏属性
app.config['SECRET_KEY'] = 'this is secret_key'  # 建立一个用于加密的密钥，验证表单

def sql_exe(sql):
    host = 'rm-uf643ap9b01399w94o.mysql.rds.aliyuncs.com'
    conn = pymysql.connect(host=host, port=3306, user='root', passwd='Qw1234567', db='library',charset="utf8")
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    return result
def jian():
    error = None
    if 'username' not in session or session['username'] == None:
        error = '请先登录账户'
    print(error)
    return error
@app.before_request
def before_request():
    g.user = None
    if 'username' in session:
        g.user = session['username']


@app.route('/')
def index():
    return render_template('index.html')

#管理员登入
@app.route('/manager_login', methods=['GET', 'POST'])
def manager_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != '123456':
            error = '用户名或密码错误'
        else:
            session['username'] = request.form['username']
            return redirect(url_for('manager'))
    return render_template('manager_login.html', error = error)


# 普通用户登录
@app.route('/reader_login', methods=['GET', 'POST'])
def reader_login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        if not user:
            error = '请输入用户名'
        elif not password:
            error = '请输入密码'
        else:
            sql = "select * from users where username='%s' " % user
            result = sql_exe(sql)
            if len(result) == 0:
                error = '用户不存在'
            else:
                sql = "SELECT pwd FROM users WHERE username='%s'" % user
                pwd = sql_exe(sql)[0][0]
                if str(pwd) == str(password):
                    session['username'] = request.form['username']
                    return redirect(url_for('reader'))
                else:
                    error = '密码错误'
    return render_template('reader_login.html', error=error)

#账号注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = '请输入用户名'
        elif not request.form['password']:
            error = '请输入密码'
        elif request.form['password'] != request.form['password2']:
            error = '俩次密码不一致，请重新输入'
        else:
            sql = "select * from users where username='%s'" % request.form['username']
            result = sql_exe(sql)
            if len(result) == 0:
                sql = "INSERT INTO `users` (username,pwd) VALUES ('%s','%s');" % (request.form['username'],request.form['password'])
                sql_exe(sql)
                return redirect(url_for('reader_login'))
            else:
                error = '账号已存在'
                return render_template('register.html', error=error)
    return render_template('register.html', error = error)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))

#书籍管理
@app.route('/manager/books')
def manager_books():
    error = jian()
    if error == None:
        books_sql = "SELECT * FROM `books`;"
        books = sql_exe(books_sql)
        return render_template('manager_books.html',books = books )
    else:
        return render_template('index.html', error=error)

@app.route('/manager')
def manager():
    return render_template('manager.html')

@app.route('/reader')
def reader():
    return render_template('reader.html')

@app.route('/manager/users')
def manager_users():
    error = jian()
    if error == None:
        users_sql = 'SELECT * FROM `users`;'
        users = sql_exe(users_sql)
        return render_template('manager_users.html', users = users)
    else:
        return render_template('index.html', error=error)

@app.route('/manager/user/<id>', methods=['GET', 'POST'])
def manager_user(id):
    error = jian()
    if error == None:
        user_info_sql = "SELECT * FROM `users` WHERE user_id = '%s';" % id
        user_info = sql_exe(user_info_sql)
        return render_template('manager_userinfo.html',user=user_info)
    else:
        return render_template('index.html', error=error)

@app.route('/manager/tables')
def manager_tables():
    error = jian()
    if error == None:
        books1 = 'select * from books'
        return render_template('manager_tables.html',books=books1)
    else:
        return render_template('index.html', error=error)

@app.route('/manager/user/modify/<id>', methods=['GET', 'POST'])
def manger_user_modify(id):
    error = jian()
    if error == None:
        user_sql = "select * from users where user_id = '%s'" % id
        user = sql_exe(user_sql)
        if request.method == 'POST':
            if not request.form['password']:
                return redirect(url_for('manager_user', id = id))
            else:
                update_sql = "UPDATE `users` SET pwd = '%s' where user_id = '%s'" % (request.form['password'],id)
                sql_exe(update_sql)
                return redirect(url_for('manager_user', id = id))
        return render_template('manager_user_modify.html', user=user, error = error)
    else:
        return render_template('index.html', error=error)
#注销账户
@app.route('/manager/user/deleter/<id>', methods=['GET', 'POST'])
def manger_user_delete(id):
    error = jian()
    if error == None:
        delete_sql = "DELETE FROM `users` WHERE user_id = '%s';" % id
        sql_exe(delete_sql)
        return redirect(url_for('manager_users'))
    else:
        return render_template('index.html', error=error)
#上架书籍
@app.route('/manager/books/add', methods=['GET', 'POST'])
def manager_books_add():
    error = jian()
    if error == None:
        if request.method == 'POST':
            if not request.form['ISBN']:
                error = 'You have to input the book ISBN'
            elif not request.form['book_name']:
                error = 'You have to input the book name'
            elif not request.form['author']:
                error = 'You have to input the book author'
            elif not request.form['company']:
                error = 'You have to input the publish company'
            elif not request.form['date']:
                error = 'You have to input the publish date'
            else:
                add_sql ="INSERT INTO `books` (ISBN,book_name,author,publish_com,publish_date) VALUES( '%s', '%s', '%s', '%s', '%s')" % \
                         (request.form['ISBN'],request.form['book_name'],request.form['author'],request.form['company'],request.form['date'])
                sql_exe(add_sql)
                return redirect(url_for('manager_books'))
        return render_template('manager_books_add.html', error = error)
    else:
        return render_template('index.html', error=error)
#下架书籍
@app.route('/manager/books/delete', methods=['GET', 'POST'])
def manager_books_delete():
    error = jian()
    if error == None:
        if request.method == 'POST':
            if not request.form['ISBN']:
                error = 'You have to input the book ISBN'
            else:
                book_sql = "select * from books where ISBN = '%s'" % request.form['ISBN']
                book = sql_exe(book_sql)
                if book is None:
                    error = 'Invalid book ISBN'
                else:
                    book_delete_sql = "DELETE FROM `books` WHERE ISBN= '%s'" % request.form['ISBN']
                    sql_exe(book_delete_sql)
                    return redirect(url_for('manager_books'))
        return render_template('manager_books_delete.html', error = error)
    else:
        return render_template('index.html', error=error)

@app.route('/manager/book/<id>', methods=['GET', 'POST'])
def manager_book(id):
    error = jian()
    if error == None:
        reader_info = None
        book_info_sql = "SELECT * FROM books WHERE book_id ='%s'" % id
        book_info = sql_exe(book_info_sql)
        if len(book_info) != 0:
            book_info = book_info[0]
            current_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            status_sql = "SELECT STATUS FROM `books` WHERE book_id ='%s'" % id  # 查询书籍借阅状态
            status = sql_exe(status_sql)[0][0]
            if int(status) == 1:  # 状态为1  表示书籍已被借阅
                reader_info_sql = "SELECT * FROM `borrows` WHERE book_id = '%s'" % id
                reader_info = sql_exe(reader_info_sql)
            else:
                reader_info = None
            if request.method == 'POST':
                return redirect(url_for('manager_book', id = id))
        return render_template('manager_book.html', book = book_info, reader = reader_info)
    else:
        return render_template('index.html', error=error)

#修改书籍信息
@app.route('/manager/modify/<id>', methods=['GET', 'POST'])
def manager_modify(id):
    error = jian()
    if error == None:
        book_info_sql = "SELECT * FROM books WHERE book_id ='%s'" % id
        book_info = sql_exe(book_info_sql)[0]
        if request.method == 'POST':
            if not request.form['isbn']:
                error = 'You have to input the book isbn'
            elif not request.form['name']:
                error = 'You have to input the book name'
            elif not request.form['author']:
                error = 'You have to input the book author'
            elif not request.form['company']:
                error = 'You have to input the publish company'
            elif not request.form['date']:
                error = 'You have to input the publish date'
            else:
                update_sql = "UPDATE `books` SET ISBN='%s',book_name='%s',author='%s',publish_com='%s',publist_date='%s' WHERE book_id = '%s';" \
                            (request.form['isbn'],request.form['name'],request.form['author'],request.form['company'],request.form['date'],id)
                sql_exe(update_sql)
                return redirect(url_for('manager_book', id = id))
        return render_template('manager_modify.html', book = book_info, error = error,id=id)
    else:
        return render_template('index.html', error=error)

@app.route('/reader/info', methods=['GET', 'POST'])
def reader_info():
    error = jian()
    if error == None:
        return render_template('reader_info.html')
    else:
        return render_template('index.html', error=error)

#修改用户信息
@app.route('/reader/modify', methods=['GET', 'POST'])
def reader_modify():
    error = jian()
    if error == None:
        user_sql = "SELECT * FROM `users` WHERE username = '%s';" % g.user
        user = sql_exe(user_sql)
        if request.method == 'POST':
            if not request.form['username']:
                error = 'You have to input your name'
            elif not request.form['password']:
                return redirect(url_for('reader_info'))
            else:
                update_sql = "UPDATE `users` SET username='%s',pwd='%s' WHERE username='%s';" % (request.form['username'],request.form['password'],g.user)
                sql_exe(update_sql)
                return redirect(url_for('reader_info'))
        return render_template('reader_modify.html', error = error,user=user)
    else:
        return render_template('index.html', error=error)

#书籍查询
@app.route('/reader/query', methods=['GET', 'POST'])
def reader_query():
    error = jian()
    if error == None:
        books = None
        if request.method == 'POST':
            if request.form['item'] == 'name':
                if not request.form['query']:
                    error = '请输入书籍名'
                else:
                    sql = "SELECT * FROM `books` WHERE book_name = '%s'" % request.form['query']
                    books = sql_exe(sql)
                    if not books:
                        error = '查询结果为空'
            else:
                if not request.form['query']:
                    error = '请输入作者名'
                else:
                    sql = "SELECT * FROM `books` WHERE author = '%s'" % request.form['query']
                    books = sql_exe(sql)
                    if not books:
                        error = '查询结果为空'
        return render_template('reader_query.html', books = books, error = error)
    else:
        return render_template('index.html', error=error)
#借书
@app.route('/reader/book/<id>', methods=['GET', 'POST'])
def reader_book(id):
    error = jian()
    if error == None:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sql = "SELECT * FROM `books` WHERE book_id = '%s' " % id
        book = sql_exe(sql)
        status_sql = "SELECT STATUS FROM `books` WHERE book_id ='%s'" %id  #查询书籍借阅状态
        status = sql_exe(status_sql)[0][0]
        if int(status) == 1:     #状态为1  表示书籍已被借阅
            reader_info_sql = "SELECT * FROM `borrows` WHERE book_id = '%s'" % id
            reader_info = sql_exe(reader_info_sql)
        else:
            reader_info = None
        if request.method == 'POST':  #借书动作
            message = '借阅成功'
            flash(message)
            sql = "UPDATE `books` SET STATUS = 1 WHERE book_id = '%s';" % id  #借书时将状态更改为已借阅
            sql_exe(sql)
            userid_sql = "SELECT user_id FROM `users` WHERE username = '%s';" % g.user
            user_id = sql_exe(userid_sql)[0][0]
            insert_sql = "INSERT INTO `borrows` (book_id,user_id,date_borrow) VALUES ('%s','%s','%s');" % (id,user_id,current_time)  #插入借阅记录
            sql_exe(insert_sql)
            return redirect(url_for('reader_book', id = id,message=message))
        return render_template('reader_book.html',reader = reader_info, error = error,book=book)
    else:
        return render_template('index.html',error=error)
@app.route('/reader/histroy', methods=['GET', 'POST'])
def reader_histroy():
    error = jian()
    if error == None:
        histroys = []
        userid_sql = "SELECT user_id FROM `users` WHERE username = '%s';" % g.user  #获取当前user_id
        user_id = sql_exe(userid_sql)[0][0]
        books_sql = "SELECT * FROM `borrows` WHERE user_id = '%s';" % user_id
        books=sql_exe(books_sql)
        for i in books:
            book_id = i[1]
            book_name_sql = "SELECT book_name FROM `books` WHERE book_id = '%s';" % book_id
            book_name = sql_exe(book_name_sql)[0]
            histroy_info = [i[0],book_name,i[2],i[3],i[4]]
            histroys.append(histroy_info)
        if request.method == 'POST':
            print('ss',)
            "UPDATE `books` SET STATUS=0 WHERE book_name ='%s'" % book_name  #更改借书状态
            return render_template('reader_histroy.html', histroys=histroys)
        return render_template('reader_histroy.html', histroys = histroys)
    else:
        return render_template('index.html', error=error)

@app.errorhandler(404) #处理异常错误,先定义404错误页面，再调用
def not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.run(debug=True,port=8080)



