from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, g, session, abort
from flask.ext.github import GitHub
from flask.ext.seasurf import SeaSurf
from database_setup import User, init_db, get_db_session
import db_helper

app = Flask(__name__)
app.config.from_object(__name__)

# SeaSurf is a python library for CSRF protection
csrf = SeaSurf(app)

# Register this application at https://github.com/settings/applications/new
#
#   Homepage URL: http://localhost:5000
#   Authorization callback URL: http://localhost:5000/github-callback
#
# Copy your Client ID and Client Secret after registering this app
# and paste them in below.
app.config['GITHUB_CLIENT_ID'] = 'xxxxxxxxxxxxxxxxxxxx'
app.config['GITHUB_CLIENT_SECRET'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

github = GitHub(app)
db_session = get_db_session()

project_template_file = open('templates/list_item_template.html', 'r')
project_item_template = project_template_file.read()
project_template_file.close()

comment_template_file = open('templates/comment_template.html', 'r')
comment_template = comment_template_file.read()
comment_template_file.close()


@app.before_request
def before_request():
    """Set default value for g.user and check if user_id is present in cache."""
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    """Remove the current session scope."""
    db_session.remove()
    return response


@github.access_token_getter
def token_getter():
    """Return user's access token."""
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/signin')
def signin():
    """User signin handler. This will authorize user with GitHub's OAuth."""
    if session.get('user_id', None) is None:
        return github.authorize()
    else:
        return 'Already logged in'


@app.route('/signout')
def signout():
    """User signout handler."""
    session.pop('user_id', None)
    flash("You've been successfully signed out :)")
    return redirect(url_for('index'))


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    """Handle authorization, and register new user into DB."""
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        flash("Oops! Looks like your access has been denied!")
        return redirect(next_url)

    # check if we can find user with the token
    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        response = github.raw_request('GET','user', params={'access_token': access_token})
        user_data = response.json()
        # check again if we can find user with user's GitHub URL
        # register new user if not found
        user = db_helper.get_user_from_users_github(user_data['html_url'])
        if user is None:
            user = User(access_token)
            db_session.add(user)

        # update user profile with data from GitHub
        if 'login' in user_data:
            user.username = str(user_data['login'])
        if 'name' in user_data:
            user.fullname = str(user_data['name'])
        if 'email' in user_data:
            user.email = str(user_data['email'])
        if 'avatar_url' in user_data:
            user.avatar_url = user_data['avatar_url']
        user.github_url = user_data['html_url']
        user.github_access_token = access_token
        db_session.commit()

    session['user_id'] = user._id
    return redirect(next_url)


@app.route('/')
def index():
    """Handler function for root page."""
    return render_template("index.html", g=g)


@app.route('/user/<username>/')
def user_profile(username):
    """Handler function for user's profile page."""
    user = db_helper.get_user_from_username(username)
    items = db_helper.get_users_project_items(user._id)
    return render_template('profile.html',
                           user=user,
                           items=items,
                           get_time=db_helper.get_readable_datetime)


@app.route('/<nd>/')
def nd_category(nd):
    """Handler for Nanodegree category page."""
    return render_template('nd_category.html',
                           nd=nd,
                           formal_name=db_helper.get_formal_name(nd))


@app.route('/<nd>/<project_no>/')
def project_category(nd, project_no):
    """Handler for Project category page inside a specific Nanodegree."""
    return render_template('p_category.html',
                           nd=nd,
                           formal_name=db_helper.get_formal_name(nd),
                           project_no=project_no)


@app.route('/<nd>/<project_no>/<int:project_id>/')
def project_item(nd, project_no, project_id):
    """Handler for a specific project item page."""
    item = db_helper.get_specific_project(project_id)
    if item is None:
        flash("Requested project does not exist!")
        return redirect(url_for("index"))
    comments = db_helper.get_comments(project_id)
    return render_template('project_item.html',
                           item=item,
                           get_user=db_helper.get_user_from_user_id,
                           get_name=db_helper.get_formal_name,
                           comments=comments,
                           get_time=db_helper.get_readable_datetime)


@app.route('/new', methods=['GET', 'POST'])
def new_project():
    """Handler for new project page. User can post new project here."""
    if request.method == "POST":
        db_helper.add_new_project(request.form, g.user._id)
        flash("Your project's been successfully shared!")
        return redirect(url_for("loading_page"))
    else:
        return render_template('new_project.html')


@app.route('/loading/')
def loading_page():
    """Handler function for loading page after new project share.
       This page is just for processing image capturing."""
    return render_template('loading_page.html')


@app.route('/<nd>/<project_no>/<int:project_id>/edit/', methods=['GET', 'POST'])
def edit_project(nd, project_no, project_id):
    """Handler for project edit page. Only the author of the project can edit."""
    item = db_helper.get_specific_project(project_id)
    if item is None:
        flash("Requested project does not exist!")
        return redirect(url_for("index"))
    if not g.user or g.user._id != item.author:
        flash("You can not edit other's project!")
        return redirect(url_for("project_item", nd=nd, project_no=project_no, project_id=project_id))
    if request.method == "POST":
        url_edited = db_helper.update_project(project_id, request.form)
        flash("Your project's been successfully edited!")
        if url_edited:
            return redirect(url_for("loading_page"))
        else:
            return redirect(url_for("project_item", nd=nd, project_no=project_no, project_id=project_id))
    else:
        return render_template("edit_project.html", item=item)


@app.route('/<nd>/<project_no>/<int:project_id>/delete/', methods=['GET', 'POST'])
def delete_project(nd, project_no, project_id):
    """Handler for project delete page. Only the author of the project can delete."""
    item = db_helper.get_specific_project(project_id)
    if item is None:
        flash("Requested project does not exist!")
        return redirect(url_for("index"))
    if not g.user or g.user._id != item.author:
        flash("You can not delete other's project!")
        return redirect(url_for("project_item", nd=nd, project_no=project_no, project_id=project_id))
    if request.method == "POST":
        db_helper.remove_project(project_id)
        flash("Your project is successfully deleted!")
        return redirect(url_for("index"))
    else:
        return render_template('delete_project.html', nd=nd, project_no=project_no, project_id=project_id)


@app.route('/<nd>.json/')
def nd_projects_JSON(nd):
    """Return a list of projects for given Nanodegree category in JSON format."""
    items = db_helper.get_nd_category_items(nd)
    return jsonify(Projects=[e.serialize for e in items])


@app.route('/api/v1/projects')
def project_list_api():
    """Return JSON object of project list for AJAX calls."""
    args = request.args
    cursor = int(args.get('cursor'))
    if 'nd' in args and 'p' in args:
        items = db_helper.get_project_items_with_cursor(cursor, args.get('nd'), args.get('p'))
        leng = items.count()
        next_cursor = cursor+leng
        more = True if leng == 20 else False
        return jsonify(Projects=[convert_project_to_html(e) for e in items], Cursor=next_cursor, More=more)
    elif 'nd' in args:
        items = db_helper.get_project_items_with_cursor(cursor, args.get('nd'))
        leng = items.count()
        next_cursor = cursor+leng
        more = True if leng == 20 else False
        return jsonify(Projects=[convert_project_to_html(e) for e in items], Cursor=next_cursor, More=more)
    else:
        items = db_helper.get_project_items_with_cursor(cursor)
        leng = items.count()
        next_cursor = cursor+leng
        more = True if leng == 20 else False
        return jsonify(Projects=[convert_project_to_html(e) for e in items], Cursor=next_cursor, More=more)


@app.route('/api/v1/comment', methods=['POST'])
def new_comment():
    """API for handling new comment POSTs, and returns HTML formatted new comment element."""
    if not request.json or 'project_id' not in request.json or 'content' not in request.json:
        abort(400)
    comment = db_helper.add_new_comment(request.json)
    return jsonify(Comment=convert_comment_to_html(comment)), 201


@app.route('/api/v1/comment/<int:cmt_id>', methods=['POST'])
def delete_comment(cmt_id):
    """API for handling delete comment calls."""
    result = db_helper.remove_comment(cmt_id, request.json['user'])
    if result is True:
        return jsonify(Result=True)
    else:
        abort(400)


def convert_project_to_html(item):
    """Convert project data into HTML element for AJAX calls."""
    author = db_helper.get_user_from_user_id(item.author).username
    project_elem = project_item_template.format(item_url=url_for('project_item', nd=item.nd_category, project_no=item.p_category, project_id=item._id),
                                                thumbnail=item.thumbnail,
                                                name=item.name,
                                                nd_category=item.nd_category,
                                                p_category=item.p_category,
                                                user_url=url_for('user_profile', username=author),
                                                author=author,
                                                created=db_helper.get_readable_datetime(item.created),
                                                no_of_comments=db_helper.get_comment_count(item._id))
    return project_elem


def convert_comment_to_html(comment):
    """Convert comment data into HTML element for AJAX calls."""
    author = db_helper.get_user_from_user_id(comment.author)
    comment_elem = comment_template.format(user_img=author.avatar_url,
                                           user_profile=url_for('user_profile', username=author.username),
                                           username=author.username,
                                           created=db_helper.get_readable_datetime(comment.created),
                                           content=comment.content,
                                           cmt_id=comment._id)
    return comment_elem


if __name__ == '__main__':
    init_db()
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
