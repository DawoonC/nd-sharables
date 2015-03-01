# ND Sharables

This web app is a place where Udacity Nanodegree students can share their projects.
<br>

Users can signin with GitHub account and CREATE, READ, UPDATE, and DELETE (CRUD) the projects, and also can add a comment on the projects.
<br>

This project, the third in [Udacity’s Full Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004), focuses on using full stack web development skills to build a web app from the scratch, which can perform user authentications and CRUD functionality.
<br>


<i>You can checkout the demo at [here](https://nd-sharables.herokuapp.com/).</i>
<br>

## Python Libraries Used in this Project
- Flask
- GitHub-Flask
- Jinja2
- SQLAlchemy
- Cloudinary


## How to Run

1. First, you need to install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads) on your machine.

2. Then, you'll need to clone this repository to your local machine.

3. Go to the vagrant directory in the cloned repository, then open a terminal window and type <b>$ vagrant up</b> to launch your virtual machine. This will take some time in your first run, because it needs to install some dependencies.

4. Once it is up and running, type <b>$ vagrant ssh</b> to log into it. This will log your terminal in to the virtual machine, and you'll get a Linux shell prompt. 

5. Open the app.py file in nd_sharables directory, you'll see an instruction on how to register this app on GitHub and obtain Client ID.

6. Once you've registered the app and set Client ID/Secret in the <i>app.py</i> file, you are now ready to launch the app.

7. On your virtual machine, go to <i>/vagrant/nd_sharables</i> directory, then type <b>$ python app.py</b>. This will launch the application.

8. You can check out the page from your browser at <i>[http://localhost:5000](http://localhost:5000)</i>.

9. If the terminal says that it can't find some modules, then open <i>requirements.txt</i> file in the current directory. You will see an instruction on how to install dependencies.
