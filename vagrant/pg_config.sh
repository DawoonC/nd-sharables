
apt-get -qqy update
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
pip install GitHub-Flask
pip install cloudinary
pip install Flask-SeaSurf==0.2.0
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
