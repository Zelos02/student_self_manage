from flask_login import UserMixin
from extensions import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime)

    def get_id(self):
        return str(self.user_id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category_name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)


class Todo(db.Model):
    __tablename__ = "todos"

    todo_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    timing_mode = db.Column(db.String(20), default="count_up")
    target_minutes = db.Column(db.Integer)
    due_time = db.Column(db.DateTime)
    remind_before_minutes = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default="未开始")
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


class FocusSession(db.Model):
    __tablename__ = "focus_sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    todo_id = db.Column(db.Integer, db.ForeignKey("todos.todo_id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)
    session_status = db.Column(db.String(20), default="进行中")


class Room(db.Model):
    __tablename__ = "rooms"

    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    room_code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime)


class RoomMember(db.Model):
    __tablename__ = "room_members"

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    joined_at = db.Column(db.DateTime)


class WishWall(db.Model):
    __tablename__ = "wish_wall"

    wish_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"))
    content = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime)