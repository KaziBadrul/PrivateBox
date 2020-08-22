from message_enc import app, db, bcrypt, login_manager
from flask import render_template, url_for, flash, redirect, request
from message_enc.forms import RoomForm, RegistrationForm, LoginForm, PostForm
from message_enc.models import Room, User, Post, UserRooms
from flask_login import login_user, logout_user, login_required, current_user
import secrets
import datetime

# HOME

@app.route("/")
@app.route("/home")
@login_required
def home():
    joined_rooms = current_user.rooms
    posts_list = []
    for room in joined_rooms:
        posts = Post.query.filter_by(room_id=room.room_id).order_by(Post.date.desc()).limit(2).all()
        posts_list.append(posts)
    if current_user.rooms:
        return render_template('home.html', posts_list=posts_list)
    else:
        return render_template('home.html', posts=None)


# ROOM RELATED

def random_id_key():
    id = secrets.randbits(16)
    room = Room.query.get(id)
    if room:
        random_id_key()
    else:
        return id

@app.route("/create_room", methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(creator=current_user.username, title=form.title.data, description=form.description.data, key=form.key.data, id=random_id_key())
        db.session.add(room)
        db.session.commit()
        flash(f"Room '{form.title.data}' created!", 'success')
        return redirect(url_for('home'))
    return render_template('create_room.html', form=form)

@app.route("/view_rooms")
def view_rooms():
    rooms = Room.query.all()
    return render_template('view_rooms.html', rooms=rooms)

@app.route("/view_rooms/verify", methods=['GET','POST'])
def room_verification():
    room_id = request.form['room_id']
    key_by_user = request.form['pin']
    room = Room.query.get(room_id)
    if str(room.key) == str(key_by_user):
        return redirect(url_for('room', room_id=room_id))
    else:
        flash(f'Wrong PIN!', 'warning')
        return redirect(url_for('view_rooms'))

@app.route("/joined_rooms")
@login_required
def joined_rooms():
    user_rooms = UserRooms.query.filter_by(user=current_user)
    return render_template('joined_rooms.html', user_rooms=user_rooms, Room=Room)

@app.route("/room/<string:room_id>")
@login_required
def room(room_id):
    room = Room.query.filter_by(id=room_id).first()
    user_rooms = current_user.rooms
    for joined_room in user_rooms:
        if room.id == joined_room.room_id:
            break
    else:
        user_room = UserRooms(user=current_user, room_id=room_id)
        db.session.add(user_room)
        db.session.commit()
    posts = Post.query.filter_by(on_room=room)
    return render_template('room.html', posts=posts, room=room)

@app.route("/view_rooms/search", methods=['POST'])
@login_required
def searched_room():
    searched_id = request.form['search_box']
    if searched_id[0] == "#":
        searched_id = searched_id[1:]
    rooms = []
    room = Room.query.get(searched_id)
    rooms.append(room)
    if rooms[0]:
        return render_template('view_rooms.html', rooms=rooms)
    else:
        flash(f'Room #{searched_id} not found!', 'warning')
        return render_template('view_rooms.html', rooms=Room.query.all())



# USER RELATED

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash(f"Account for '{form.username.data}' created!", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Successfully logged in!", "success")
            return redirect(url_for("home"))
        else:
            flash("Incorrect email or password!", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# POST RELATED

@app.route("/room/<string:room_id>/create_post", methods=["GET", "POST"])
@login_required
def create_post(room_id):
    form = PostForm()
    if form.validate_on_submit():
        room = Room.query.filter(Room.id==room_id).first()
        post = Post(title=form.title.data, content=form.content.data, on_room=room, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('room', room_id=room_id))
    return render_template('create_post.html', form=form)