
apt-get -qqy update
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
pip install GitHub-Flask
pip install cloudinary
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
