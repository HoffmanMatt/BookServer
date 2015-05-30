__author__ = 'group'

import flask
import easypg
import bcrypt
import datetime
import time
import calendar
#import json

from data import home, log, books, search, user, lists, friends, quote, review, editBook, tags, comments

app = flask.Flask('BookServer')


@app.route('/')
def login():
    with easypg.cursor() as cur:
        num_users = user.get_user_count(cur)
        num_friends = friends.count_num_friends(cur)
    return flask.render_template('login.html',
                                 num_users=num_users,
                                 num_friends=num_friends)


@app.route('/login_request/')
def login_request():
    if 'loginName' in flask.request.args:
        login = flask.request.args['loginName']
    else:
        flask.abort(400)

    if 'loginPass' in flask.request.args:
        password = flask.request.args['loginPass']
    else:
        flask.abort(400)

    with easypg.cursor() as cur:
        user_id = log.validate_login_info(cur, login, password)

    if user_id == -1:
       flask.abort(401)

    flask.session['user_id'] = user_id

    return flask.redirect('/home/')


@app.route('/logout/')
def logout():
    user_id = flask.session['user_id']
    flask.session.pop('user_id', None)
    return flask.redirect('/')


@app.route('/new_account/')
def new_account():
    return flask.render_template('new_account.html')



@app.route('/new_account/add')  #, methods=['POST']
def create_account():

    if 'loginName' in flask.request.args:
        loginName = flask.request.args['loginName']
    else:
        flask.abort(400)

    if 'loginPass' in flask.request.args:
        loginPass = flask.request.args['loginPass']
    else:
        flask.abort(400)

    if 'confirmPass' in flask.request.args:
        confirmPass = flask.request.args['confirmPass']
    else:
        flask.abort(400)

    if 'userName' in flask.request.args:
        userName = flask.request.args['userName']
    else:
        flask.abort(400)

    if 'email' in flask.request.args:
        email = flask.request.args['email']
    else:
        flask.abort(400)

    if 'birthDate' in flask.request.args:
        birthDate = flask.request.args['birthDate']
    else:
        flask.abort(400)

    if confirmPass != loginPass:
        flask.abort(400)

    with easypg.cursor() as cur:
        isUnique = log.is_unique_name(cur, loginName)

    if isUnique == True:
         with easypg.cursor() as cur:
            log.add_user(cur, loginName, loginPass, userName, email, birthDate)
    else:
        flask.abort(400)
    return flask.redirect('/')


@app.route('/home/')
def homePage():
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        user_info = user.get_user_info(cur, uid)
        num_books = home.get_book_count(cur)
        num_authors = home.get_author_count(cur)
        comment_wall = home.get_user_comment_wall(cur, uid)
        quote_wall = home.get_user_quote_wall(cur, uid)
        review_wall = home.get_user_review_wall(cur, uid)
        num_comments = comment_wall.__len__()
        num_reviews = review_wall.__len__()
        num_quotes = quote_wall.__len__()
    return flask.render_template('home.html',
                                 uid=uid,
                                 user_info=user_info,
                                 num_books=num_books,
                                 num_authors=num_authors,
                                 comment_wall=comment_wall,
                                 quote_wall=quote_wall,
                                 review_wall=review_wall,
                                 num_comments=num_comments,
                                 num_reviews=num_reviews,
                                 num_quotes=num_quotes)



@app.route('/account/')
def account_details():
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        user_info = user.get_user_info(cur, uid)

        user_list = lists.get_user_list_info(cur, uid)
        num_lists = lists.get_num_lists_for_user(cur, uid)
        books_read = books.get_books_read(cur, uid)
        num_books_read = books.num_books_read(cur, uid)
        friends_list = friends.get_all_friends(cur, uid)
        total_pages_read = books.num_pages_read(cur, uid)
        num_friends_targeting_user = friends.num_friends_targeting_user(cur, uid)
        num_friends = friends.num_friends_for_user(cur, uid)
        friends_targeting = friends.get_friends_targeting_user(cur, uid)

    return flask.render_template('account.html',
                                 books_read=books_read,
                                 num_books_read=num_books_read,
                                 num_lists=num_lists,
                                 user_info=user_info,
                                 #user_list=user_list,
                                 list_name=user_list,
                                 friends=friends_list,
                                 num_friends=num_friends,
                                 friends_for_user=num_friends_targeting_user,
                                 friends_targeting=friends_targeting,
                                 total_pages_read=total_pages_read)



@app.route('/account/update/')    #, methods=['POST']
def update_account():
    uid = flask.session['user_id']
    current_pass_needed = False
    new_email_needed = False
    new_login_needed = False
    new_name_needed = False
    new_pass_needed = False

    if 'newLogin' in flask.request.args:
        newLogin = flask.request.args['newLogin']
        if newLogin != "":
            new_login_needed = True
            current_pass_needed = True

    if 'newEmail' in flask.request.args:
        newEmail = flask.request.args['newEmail']
        if newEmail != "":
            new_email_needed = True
            current_pass_needed = True

    if 'newName' in flask.request.args:
        newName = flask.request.args['newName']
        if newName != "":
            new_name_needed = True
            current_pass_needed = True

    if 'newPass' in flask.request.args:
        newPass = flask.request.args['newPass']
        confirmPass = flask.request.args['confirmPass']
        if newPass != confirmPass:
            flask.abort(400)
        if newPass != "":
            new_pass_needed = True
            current_pass_needed = True


    # this if-statement activates only if any user info needs to be changed.
    # this if-statement confirms the current password.
    if current_pass_needed:
        currentPass = flask.request.args['currentPass']
        with easypg.cursor() as cur:
            if user.is_valid_pass(cur, currentPass, uid):
                print "is valid"
            else:
                flask.abort(403)

    # if the entry fields for each column wasn't empty, it will replace user's data appropriately.

    if new_pass_needed:
        hash = bcrypt.hashpw(newPass, bcrypt.gensalt())
        with easypg.cursor() as cur:
            user.change_user_pass(cur, hash, uid)

    if new_name_needed:
        with easypg.cursor() as cur:
            user.change_user_name(cur, newName, uid)

    if new_email_needed:
        with easypg.cursor() as cur:
            user.change_user_email(cur, newEmail, uid)

    if new_login_needed:
        with easypg.cursor() as cur:
            if log.is_unique_name(cur, newLogin):
                user.change_user_login(cur, newLogin, uid)
            else:
                flask.abort(400)
    return flask.redirect('/account/')


@app.route('/account/new_list/')    #, methods=['POST']
def new_list():
    uid = flask.session['user_id']
    name = flask.request.args['listName']
    with easypg.cursor() as cur:
        lists.add_list(cur, uid, name)
    return flask.redirect('/account/')


@app.route('/account/remove_list/<ulid>', methods=['POST'])
def remove_list(ulid):
    with easypg.cursor() as cur:
        lists.remove_list(cur, ulid)
    return flask.redirect('/account/')


@app.route('/account/BookList/<ulid>')    #, methods=['POST']
def new_book_in_list(ulid):
    bid = flask.request.args['bid']
    with easypg.cursor() as cur:
        lists.add_book_to_list(cur, bid, ulid)
    return flask.redirect('/account/')


@app.route('/account/book_list/remove_book/<ulid>/<bid>', methods=['POST'])
def remove_book_in_list(ulid, bid):
    with easypg.cursor() as cur:
        lists.remove_book_from_list(cur, ulid, bid)
    return flask.redirect('/account/')


@app.route('/books/book_list/<ulid>')
def view_particular_list(ulid):
    viewer_id = flask.session['user_id']
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, viewer_id)
        list_owner_id = lists.get_owner_for_list(cur, ulid)
        list_owner_login = user.get_user_login(cur, list_owner_id)
        list_info = lists.get_books_in_list(cur, ulid)
        num_books_in_list = list_info.__len__()
        list_name = lists.get_list_name(cur, ulid)
        comment_info = comments.get_comments_for_list(cur, ulid)

        if login == list_owner_login:
            same_user = True
        else:
            same_user = False

    return flask.render_template('list.html',
                                 login=login,
                                 list_owner_login=list_owner_login,
                                 list_owner_id=list_owner_id,
                                 num_books_in_list=num_books_in_list,
                                 list_info=list_info,
                                 list_name=list_name,
                                 same_user=same_user,
                                 ulid=ulid,
                                 comment_info=comment_info)





@app.route('/books/book_list/new_comments/<ulid>', methods=['POST'])
def add_comment_to_list(ulid):
    uid = flask.session['user_id']
    comment = flask.request.form['comment']
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    with easypg.cursor() as cur:
        poster = user.get_user_login(cur, uid)
        comments.add_comment(cur, ulid, uid, comment, date, poster)
    ulid = str(ulid)
    return flask.redirect('/books/book_list/' + ulid)


@app.route('/books/book_list/remove_comments/<ulid>/<lc_id>', methods=['POST'])
def remove_comment_from_list(ulid, lc_id):
    with easypg.cursor() as cur:
        comments.remove_comment(cur, lc_id)
    ulid = str(ulid)
    return flask.redirect('/books/book_list/' + ulid)


@app.route('/user/<profile_id>')
def profile_id(profile_id):
    viewer_uid = flask.session['user_id']
    are_friends = False
    with easypg.cursor() as cur:
        user_info = user.get_user_info(cur, profile_id)
        if user_info is None:
            flask.abort(400)
        viewer_login = user.get_user_login(cur, viewer_uid)
        profile_login = user.get_user_login(cur, profile_id)
        friends_list = friends.get_all_friends(cur, profile_id)
        quote_info = quote.get_quotes_for_user(cur, profile_id)
        review_info = review.get_reviews_for_user(cur, profile_id)
        num_reviews = review.get_num_reviews_for_user(cur, profile_id)
        num_quotes = quote.get_num_quotes_for_user(cur, profile_id)
        num_books_read = books.num_books_read(cur, profile_id)
        num_distinct_read = books.num_unique_books_read(cur, profile_id)
        books_read = books.get_books_read(cur, profile_id)
        total_pages_read = books.num_pages_read(cur, profile_id)
        num_lists = lists.get_num_lists_for_user(cur, profile_id)
        list_name = lists.get_user_list_info(cur, profile_id)
    if friends_list is None:
        print "no friends"
    else:
        with easypg.cursor() as cur:
            are_friends = friends.already_friends(cur, viewer_uid, profile_id)

    if viewer_login == profile_login:
        same_user = True
    else:
        same_user = False
    with easypg.cursor() as cur:
        friend_points = friends.num_friends_targeting_user(cur, profile_id)
        quote_points = quote.get_quote_points_for_user(cur, profile_id)
        review_points = review.get_num_reviews_for_user(cur, profile_id)
        book_points = books.num_unique_books_read(cur, profile_id)
        comment_points = comments.get_comment_points_for_user(cur, profile_id)
    total_points = 0
    total_points = total_points + friend_points
    total_points = total_points + review_points
    total_points = total_points + book_points
    #total_points = total_points + quote_points
    total_points = total_points + comment_points

    return flask.render_template('profile.html',
                                 same_user=same_user,
                                 total_points=total_points,
                                 are_friends=are_friends,
                                 viewer_id=viewer_uid,
                                 viewer_login=viewer_login,
                                 profile_id=profile_id,
                                 user_info=user_info,
                                 quote_info=quote_info,
                                 review_info=review_info,
                                 num_quotes=num_quotes,
                                 num_reviews=num_reviews,
                                 num_books_read=num_books_read,
                                 books_read=books_read,
                                 num_distinct_read=num_distinct_read,
                                 total_pages_read=total_pages_read,
                                 friends_list=friends_list,
                                 num_lists=num_lists,
                                 list_name=list_name)


@app.route('/user/points/<profile_id>')
def profile_points(profile_id):
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)
        profile_login = user.get_user_login(cur, profile_id)
        friend_points = friends.num_friends_targeting_user(cur, profile_id)
        quote_points = 0
        #quote_points = quote.get_quote_points_for_user(cur, profile_id)
        review_points = review.get_num_reviews_for_user(cur, profile_id)
        book_points = books.num_unique_books_read(cur, profile_id)
        comment_points = comments.get_comment_points_for_user(cur, profile_id)
    total_points = 0
    total_points = total_points + friend_points
    total_points = total_points + review_points
    total_points = total_points + book_points
    #total_points = total_points + quote_points
    total_points = total_points + comment_points

    return flask.render_template('points_page.html',
                                 login=login,
                                 profile_id=profile_id,
                                 total_points=total_points,
                                 friend_points=friend_points,
                                 book_points=book_points,
                                 profile_login=profile_login,
                                 quote_points=quote_points,
                                 review_points=review_points,
                                 comment_points=comment_points)


@app.route('/user/<profile_id>/<year>')
def profile_id_year(profile_id, year):
    viewer_uid = flask.session['user_id']
    are_friends = False
    if flask.request.args['year']:
        year = flask.request.args['year']

    if profile_id == viewer_uid:
        same_user = True
    else:
        same_user = False
    print "ids: ", profile_id, viewer_uid

    with easypg.cursor() as cur:
        user_info = user.get_user_info(cur, profile_id)
        if user_info is None:
            flask.abort(400)
        friends_list = friends.get_all_friends(cur, viewer_uid)
        num_books_read = books.num_books_read_for_year(cur, profile_id, year)
        books_read = books.get_books_read_for_year(cur, profile_id, year)
        distinct_books_for_year = books.num_distinct_books_read_for_year(cur, profile_id, year)
        total_pages_read = books.num_pages_read_for_year(cur, profile_id, year)
        viewer_login = user.get_user_login(cur, viewer_uid)
        profile_login = user.get_user_login(cur, profile_id)
    if friends_list is None:
        print "no friends"
    else:
        with easypg.cursor() as cur:
            are_friends = friends.already_friends(cur, viewer_uid, profile_id)
    if viewer_login == profile_login:
        same_user = True
    else:
        same_user = False

    return flask.render_template('profile_year.html',
                                 same_user=same_user,
                                 are_friends=are_friends,
                                 viewer_id=viewer_uid,
                                 profile_id=profile_id,
                                 user_info=user_info,
                                 num_books_read=num_books_read,
                                 distinct_books_for_year=distinct_books_for_year,
                                 books_read=books_read,
                                 total_pages_read=total_pages_read,
                                 year=year)


@app.route('/user/add_friend/<friend_id>')
def add_friend(friend_id):
    uid = flask.session['user_id']
    friend_id = int(friend_id)
    print friend_id

    with easypg.cursor() as cur:
        if friends.already_friends(cur, uid, friend_id):
            return flask.redirect('/user/%d' % (friend_id, ))
        else:
            friends.add_friend(cur, uid, friend_id)
    return flask.redirect('/user/%d' % (friend_id, ))


@app.route('/user/remove_friend/<friend_id>')
def remove_friend(friend_id):
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        if friends.already_friends(cur, uid, friend_id):
            friends.remove_friend(cur, uid, friend_id)
        else:
            return flask.redirect('/user/' + (friend_id))
    friend_id =  str(friend_id)
    return flask.redirect('/user/' + (friend_id))


@app.route('/books/title/')
def list_books_by_title():
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        book_info = books.get_all_books_by_title(cur, page)
        num_books = books.get_book_count(cur)

    remainder = num_books % 50
    extraPage = 0
    if remainder != 0:
        extraPage = 1
    maxPages = int(num_books / 50) + extraPage

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1

    is_publisher = False
    is_title = True
    is_author = False

    return flask.render_template('books.html',
                                 is_publisher=is_publisher,
                                 is_title=is_title,
                                 num_books=num_books,
                                 books=book_info,
                                 page=page,
                                 nextPage=nextPage,
                                 prevPage=prevPage,
                                 maxPages=maxPages,
                                 login=login)



@app.route('/books/publisher/')
def list_books_by_publisher():
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        book_info = books.get_all_books_by_publisher(cur, page)
        num_books = books.get_book_count(cur)

    remainder = num_books % 50
    extraPage = 0
    if remainder != 0:
        extraPage = 1
    maxPages = int(num_books / 50) + extraPage

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1
    is_title = False
    is_author = False
    is_publisher = True

    return flask.render_template('books.html',
                                 is_publisher=is_publisher,
                                 is_title=is_title,
                                 is_author=is_author,
                                 num_books=num_books,
                                 books=book_info,
                                 page=page,
                                 nextPage=nextPage,
                                 prevPage=prevPage,
                                 maxPages=maxPages,
                                 login=login)

@app.route('/books/tag/')
def list_books_by_tag():
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        book_info = books.get_all_books_by_tag(cur, page)
        num_books = books.get_book_count(cur)

    remainder = num_books % 50
    extraPage = 0
    if remainder != 0:
        extraPage = 1
    maxPages = int(num_books / 50) + extraPage

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1
    is_title = False
    is_author = False
    is_publisher = False
    is_tag = True

    return flask.render_template('books.html',
                                 is_publisher=is_publisher,
                                 is_title=is_title,
                                 is_author=is_author,
                                 is_tag=is_tag,
                                 num_books=num_books,
                                 books=book_info,
                                 page=page,
                                 nextPage=nextPage,
                                 prevPage=prevPage,
                                 maxPages=maxPages,
                                 login=login)


@app.route('/books/author/')
def list_books_by_author():
    uid = flask.session['user_id']
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        book_info = books.get_all_books_by_author_1(cur, page)
        num_books = books.get_book_count(cur)

    remainder = num_books % 50
    extraPage = 0
    if remainder != 0:
        extraPage = 1
    maxPages = int(num_books / 50) + extraPage

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1
    is_title = False
    is_author = True
    is_publisher = False

    return flask.render_template('books.html',
                                 is_publisher=is_publisher,
                                 is_title=is_title,
                                 is_author=is_author,
                                 num_books=num_books,
                                 books=book_info,
                                 page=page,
                                 nextPage=nextPage,
                                 prevPage=prevPage,
                                 maxPages=maxPages,
                                 login=login)



@app.route('/books/<bid>')
def get_book(bid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        book_info = books.get_book(cur, bid)
        review_info = review.get_book_reviews_by_date_with_points(cur, bid)
        quote_info = quote.get_book_quotes_by_date_with_points(cur, bid)
        num_quotes = quote.get_quote_count(cur, bid)
        num_reviews = review.get_review_count(cur, bid)
        login = user.get_user_login(cur, uid)
        has_read = books.has_read_book(cur, uid, bid)
        has_rated = books.already_rated_by_user(cur, uid, bid)
        book_has_rating = books.book_has_rating(cur, bid)
        num_tags = tags.num_tags_for_book(cur, bid)
        #if num_tags > 0:
        tag_list = tags.get_tags_for_book(cur, bid)
        if book_has_rating:
            book_rating = books.get_book_rating(cur, bid)
            book_rating = '{:.{prec}f}'.format(book_rating, prec=3)
            num_book_ratings = books.count_num_ratings_for_book(cur, bid)
        else:
            book_rating = None
            num_book_ratings = 0
    if book_info is None:
        flask.abort(404)
    return flask.render_template('book.html',
                                 uid=uid,
                                 book_id=bid,
                                 login=login,
                                 book=book_info,
                                 review_info=review_info,
                                 quote_info=quote_info,
                                 num_quotes=num_quotes,
                                 num_reviews=num_reviews,
                                 has_read=has_read,
                                 has_rated=has_rated,
                                 book_has_rating=book_has_rating,
                                 book_rating=book_rating,
                                 num_book_ratings=num_book_ratings,
                                 num_tags=num_tags,
                                 tag_list=tag_list)


@app.route('/books/<bid>/rate/<stars>')
def add_rating_to_book(bid, stars):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        if books.already_rated_by_user(cur, uid, bid):
            books.change_rating(cur, stars, uid, bid)
        else:
            books.add_rating(cur, stars, uid, bid)
    return flask.redirect('/books/' + bid)


@app.route('/search')
def get_search_results():
    if 'q' in flask.request.args:
        query = flask.request.args['q']
    else:
        flask.abort(400)

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        results, total = search.search_books(cur, query, page)

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1

    extraPage = 0
    remainder = total % 50
    if remainder != 0:
        extraPage = 1
    maxPages = int(total / 50) + extraPage
    return flask.render_template('search_results.html',
                                 query=query,
                                 books=results,
                                 total=total,
                                 resultsPages=maxPages,
                                 prevPage=prevPage,
                                 nextPage=nextPage,
                                 page=page)



@app.route('/books/<bid>/reviews/add/<uid>', methods=['POST'])
def add_review(bid, uid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        poster = user.get_user_login(cur, uid)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    text = flask.request.form['review']
    app.logger.info('got review from %s: %s', poster, text)
    with easypg.cursor() as cur:
        review.add_review(cur, text, bid, st, uid, poster)

    return flask.redirect('/books/' + bid)


@app.route('/books/reviews/delete/<rid>')  #, methods=['POST']
def delete_review(rid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        review.delete_review(cur, rid)
    uid = str(uid)
    return flask.redirect('/user/' + uid)



@app.route('/books/<bid>/quotes/add/<uid>', methods=['POST'])
def add_quote(bid, uid):
    uid = flask.session["user_id"]
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    text = flask.request.form['quote']
    with easypg.cursor() as cur:
        quote.add_quote(cur, text, bid, uid, date)
    return flask.redirect('/books/' + bid)


@app.route('/books/quotes/delete/<qid>') #, methods=['POST']
def delete_quote(qid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        quote.delete_quote(cur, qid)
    uid = str(uid)
    return flask.redirect('/user/' + uid)


@app.route('/books/<bid>/mark_read/')
def mark_read(bid):
    uid = flask.session["user_id"]
    dateRead = flask.request.args['dateRead']
    with easypg.cursor() as cur:
        books.add_book_read(cur, uid, bid, dateRead)
    return flask.redirect('/books/' + bid)



@app.route('/books/<bid>/<rid>/d', methods=['POST'])
def initiate_down_vote_review(bid, rid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        currentVote = review.get_user_vote_for_review(cur, uid, rid)
        if currentVote == None:
            review.add_vote_review(cur, -1, uid, rid)
        else:
            review.change_review_vote(cur, -1, uid, rid)
    return flask.redirect('/books/' + bid)


@app.route('/books/<bid>/<rid>/u', methods=['POST'])
def initiate_up_vote_review(bid, rid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        currentVote = review.get_user_vote_for_review(cur, uid, rid)
        if currentVote == None:
            review.add_vote_review(cur, 1, uid, rid)
        else:
            review.change_review_vote(cur, 1, uid, rid)

    return flask.redirect('/books/' + bid)



@app.route('/books/<lc_id>/dc', methods=['POST'])
def initiate_down_vote_comment(lc_id):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        list_id = comments.get_user_list_id(cur, lc_id)
        currentVote = comments.get_user_vote_for_comment(cur, uid, lc_id)
        if currentVote == None:
            comments.add_vote_comment(cur, -1, uid, lc_id)
        else:
            comments.change_comment_vote(cur, -1, uid, lc_id)
    list_id = str(list_id)
    return flask.redirect('/books/book_list/' + list_id)



@app.route('/books/<lc_id>/uc', methods=['POST'])
def initiate_up_vote_comment(lc_id):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        list_id = comments.get_user_list_id(cur, lc_id)
        currentVote = comments.get_user_vote_for_comment(cur, uid, lc_id)
        if currentVote == None:
            comments.add_vote_comment(cur, 1, uid, lc_id)
        else:
            comments.change_comment_vote(cur, 1, uid, lc_id)
    list_id = str(list_id)
    return flask.redirect('/books/book_list/' + list_id)



@app.route('/books/<bid>/<qid>/dq', methods=['POST'])
def initiate_down_vote_quote(bid, qid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        currentVote = quote.get_user_vote_for_quote(cur, uid, qid)
        if currentVote == None:
            quote.add_vote_quote(cur, -1, uid, qid)
        else:
            quote.change_quote_vote(cur, -1, uid, qid)
    return flask.redirect('/books/' + bid)

@app.route('/books/<bid>/<qid>/uq', methods=['POST'])
def initiate_up_vote_quote(bid, qid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        currentVote = quote.get_user_vote_for_quote(cur, uid, qid)
        if currentVote == None:
            quote.add_vote_quote(cur, 1, uid, qid)
        else:
            quote.change_quote_vote(cur, 1, uid, qid)
    return flask.redirect('/books/' + bid)


@app.route('/books/publisher/<pub_name>')
def list_books_by_pub(pub_name):
    uid = flask.session["user_id"]
    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        pub_book_list = books.get_all_books_with_publisher(cur, pub_name, page)
        login = user.get_user_login(cur, uid)
    total = pub_book_list.__len__()

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1

    extraPage = 0
    remainder = total % 50
    if remainder != 0:
        extraPage = 1
    maxPages = int(total / 50) + extraPage

    return flask.render_template('pubBooks.html',
                                 login=login,
                                 pub_book_list=pub_book_list,
                                 publisher=pub_name,
                                 total=total)


@app.route('/books/author/<author>')
def find_books_with_author(author):
    uid = flask.session["user_id"]
    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        auth_book_list = books.get_all_books_with_author(cur, author, page)
        login = user.get_user_login(cur, uid)
    total = auth_book_list.__len__()

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1

    extraPage = 0
    remainder = total % 50
    if remainder != 0:
        extraPage = 1
    maxPages = int(total / 50) + extraPage

    return flask.render_template('authBooks.html',
                                 login=login,
                                 auth_book_list=auth_book_list,
                                 author_name=author,
                                 total=total)


@app.route('/books/tag/<tag>')
def find_books_with_tag(tag):
    uid = flask.session["user_id"]
    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        book_list = books.get_all_books_with_tag(cur, tag, page)
        login = user.get_user_login(cur, uid)
    total = book_list.__len__()

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None
    nextPage = page + 1

    extraPage = 0
    remainder = total % 50
    if remainder != 0:
        extraPage = 1
    maxPages = int(total / 50) + extraPage

    return flask.render_template('tagBooks.html',
                                 login=login,
                                 book_list=book_list,
                                 tag_name=tag,
                                 total=total)



@app.route('/books/add/')
def add_book_page():
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)
    return flask.render_template('add_book.html',
                                 login=login)



@app.route('/books/add/request/', methods=['POST'])
def add_book_handler():
    title = flask.request.form['title']
    edition = flask.request.form['edition']
    isbn = flask.request.form['isbn']
    author_name = flask.request.form['author_name']
    publisher = flask.request.form['publisher']
    pub_date = flask.request.form['pub_date']
    pages = flask.request.form['pages']
    cover_type = flask.request.form['cover_type']
    description = flask.request.form['description']
    if title == "":
        flask.abort(402)
    if edition == "":
        flask.abort(402)
    if isbn == "":
        flask.abort(402)
    if author_name == "":
        flask.abort(402)
    if publisher == "":
        flask.abort(402)
    if pages == "":
        flask.abort(402)

    with easypg.cursor() as cur:
        aid = books.get_author_id(cur, author_name)
        bid = editBook.add_book(cur, title, edition, isbn, author_name, publisher,
                                pub_date, pages, cover_type, description, aid)
    bid = str(bid)
    return flask.redirect('/books/' + bid)



@app.route('/books/edit/<bid>')
def edit_book_info_page(bid):
    uid = flask.session["user_id"]
    with easypg.cursor() as cur:
        login = user.get_user_login(cur, uid)
        book_info = books.get_book(cur, bid)
    return flask.render_template('editBook.html',
                                 book=book_info,
                                 bid=bid,
                                 login=login)



@app.route('/books/edit_author/<bid>/<author_id>')
def edit_book_author(bid, author_id):
    new_name = flask.request.args['new_author']
    with easypg.cursor() as cur:
        editBook.change_author_name(cur, author_id, new_name)
    bid = str(bid)
    return flask.redirect('/books/edit/' + bid)



@app.route('/books/delete_author/<bid>/<author_id>')
def delete_book_author(bid, author_id):
    with easypg.cursor() as cur:
        editBook.delete_author(cur, author_id)
    bid = str(bid)
    return flask.redirect('/books/edit/' + bid)



@app.route('/books/edit_description/<bid>')
def edit_book_description(bid):
    new_description = flask.request.args['new_description']
    with easypg.cursor() as cur:
        editBook.edit_book_description(cur, new_description, bid)
    bid = str(bid)
    return flask.redirect('/books/edit/' + bid)


@app.route('/books/edit_pub_date/<bid>')
def edit_pub_date(bid):
    new_pub_date = flask.request.args['new_pub_date']
    with easypg.cursor() as cur:
        editBook.edit_book_pub_date(cur, new_pub_date, bid)
    bid = str(bid)
    return flask.redirect('/books/edit/' + bid)


@app.route('/books/edit_pages/<bid>')
def edit_pages(bid):
    new_pages = flask.request.args['new_pages']
    with easypg.cursor() as cur:
        editBook.edit_book_pages(cur, new_pages, bid)
    bid = str(bid)
    return flask.redirect('/books/edit/' + bid)


@app.route('/books/add_tag/<bid>')
def add_book_tag(bid):
    tag_text = flask.request.args['tag_text']
    with easypg.cursor() as cur:
        if tags.tag_already_exists(cur, tag_text):
            tag_id = tags.get_tag_id(cur, tag_text)
            if tags.tag_already_exists_for_book(cur, tag_id, bid):
                print "nothing"
            else:
                tags.add_tag_to_book(cur, tag_id, bid)
        else:
            tags.create_new_tag(cur, tag_text)
            tag_id = tags.get_tag_id(cur, tag_text)
            tags.add_tag_to_book(cur, tag_id, bid)
    bid = str(bid)
    return flask.redirect('/books/' + bid)



@app.route('/books/remove_tag/<bid>/<tid>/')
def remove_book_tag(bid, tid):
    with easypg.cursor() as cur:
        tags.remove_tag_for_book(cur, tid, bid)
    bid = str(bid)
    return flask.redirect('/books/' + bid)




if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XpH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0', debug=True)





#####bugs########
#to each individual book page, the number of times the book has been read
# points for user, quote review

