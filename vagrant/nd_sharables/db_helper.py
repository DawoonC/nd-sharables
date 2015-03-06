from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Project, Comment
import cloudinary

engine = create_engine('sqlite:///ndSharables.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


def get_user_from_username(username):
    """Get user object from given username."""
    return session.query(User).filter_by(username=username).first()


def get_user_from_user_id(user_id):
    """Get user object from given user ID."""
    return session.query(User).filter_by(_id=user_id).first()


def get_user_from_users_github(url):
    """Get user object from given user ID."""
    return session.query(User).filter_by(github_url=url).first()


def get_latest_projects():
    """Get latest projects from DB."""
    return session.query(Project).order_by(desc(Project.created)).slice(0,10)


def get_users_project_items(user_id):
    """Get user's latest projects from DB."""
    return session.query(Project).filter_by(author=user_id).order_by(desc(Project.created)).all()


def get_nd_category_items(nd):
    """Get latest projects for given ND category."""
    return session.query(Project).filter_by(nd_category=nd).order_by(desc(Project.created)).slice(0,10)


def get_p_category_items(nd, project_no):
    """Get latest projects for given project category."""
    return session.query(Project).filter_by(nd_category=nd, p_category=project_no).order_by(desc(Project.created)).slice(0,10)


def get_specific_project(project_id):
    """Get specific project for given project ID."""
    item = session.query(Project).filter_by(_id=project_id)
    if len(item.all()) == 0:
        return None
    return item.one()


def get_project_items_with_cursor(cursor, nd=None, project_no=None):
    """Get latest projects from DB, start from given cursor position."""
    if nd is not None and project_no is not None:
        return session.query(Project).filter_by(nd_category=nd, p_category=project_no).order_by(desc(Project.created)).slice(cursor,cursor+20)
    elif nd is not None:
        return session.query(Project).filter_by(nd_category=nd).order_by(desc(Project.created)).slice(cursor,cursor+20)
    else:
        return session.query(Project).order_by(desc(Project.created)).slice(cursor,cursor+20)


# This function requires an account at Cloudinary and URL2PNG add-on
# If you want to try this out, then goto http://cloudinary.com and create a free account,
# then choose free trial at https://cloudinary.com/console/addons#url2png
# and then copy your API key from dashboard and paste it in the terminal when run this app.
# e.g. $ CLOUDINARY_URL=cloudinary://000000000000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx python app.py
def get_thumbnal_url_from(project_url):
    """Take Thumbnail image from submitted project URL."""
    if project_url.endswith('/'):
        project_url = project_url[:-1]
    project_url = project_url + "/url2png/thumbnail_max_width=200"
    img_url = cloudinary.CloudinaryImage(project_url, type="url2png").build_url(
                                         crop="fill", width=200, height=150, gravity="north",
                                         sign_url=True)
    return img_url


# Uncomment the thumbnail part if you want to try out the URL2PNG service.
def add_new_project(form, user_id):
    """Add new project into DB."""
    new_project = Project(name=form["project_name"],
                          url=form["project_url"],
                          nd_category=form["nd_category"],
                          p_category=form["p_category"],
                          description=form["description"],
                          author=user_id,)
                          #thumbnail=get_thumbnal_url_from(form["project_url"]))
    session.add(new_project)
    session.commit()


# Uncomment the thumbnail part if you want to try out the URL2PNG service.
def update_project(project_id, form):
    """Update an existing project in DB."""
    url_edited = False
    project = session.query(Project).filter_by(_id=project_id).one()

    # update each fields
    project.name = form["project_name"]
    project.description = form["description"]
    if project.url != form["project_url"]:
        project.url = form["project_url"]
        # project.thumbnail = get_thumbnal_url_from(form["project_url"])
        url_edited = True

    session.add(project)
    session.commit()
    return url_edited


def remove_project(project_id):
    """Remove the project from DB."""
    project = session.query(Project).filter_by(_id=project_id).one()
    session.delete(project)
    session.commit()


def add_new_comment(data):
    """Add new comment into DB."""
    new_comment = Comment(author=data['author'],
                          project_id=data['project_id'],
                          content=data['content'])
    session.add(new_comment)
    session.commit()
    return new_comment


def get_comments(project_id):
    """Get comments for the given project_id."""
    return session.query(Comment).filter_by(project_id=project_id).order_by(Comment.created).all()


def remove_comment(cmt_id, user_id):
    """Remove the comment from DB."""
    comment = session.query(Comment).filter_by(_id=cmt_id).one()
    if comment.author == user_id:
        session.delete(comment)
        session.commit()
        return True
    else:
        return False


def get_comment_count(project_id):
    """Count number of comment for the given project_id and return in appropriate format."""
    num = len(get_comments(project_id))
    if num == 0:
        return "Comment"
    elif num == 1:
        return "1 Comment"
    else:
        return str(num)+" Comments"


def get_readable_datetime(datetime):
    """Convert datetime object into readable format."""
    current_time = datetime.now()
    diff = int((current_time - datetime).total_seconds())
    if diff < 60:
        return "%s sec ago" % diff
    elif (diff/60) < 60:
        return "%s min ago" % (diff/60)
    elif (diff/60/60) < 48:
        return "%s hr ago" % (diff/60/60)
    elif (diff/60/60/24) < 61:
        return "%s days ago" % (diff/60/60/24)
    else:
        return "%s months ago" % (diff/60/60/24/30)


def get_formal_name(name):
    """Convert short ND category name into a formal name."""
    if name == "FEND":
        return "Front-End Web Developer Nanodegree"
    elif name == "DAND":
        return "Data Analyst Nanodegree"
    elif name == "FSND":
        return "Full Stack Web Developer Nanodegree"
    elif name == "iOSND":
        return "iOS Developer Nanodegree"
    elif name == "Other":
        return "Other Projects"
    return "Err.. This ND does not exist yet!"
