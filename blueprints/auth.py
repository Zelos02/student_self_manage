from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        email = request.form.get("email", "").strip()
        nickname = request.form.get("nickname", "").strip()

        if not username or not password:
            flash("用户名和密码不能为空", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("两次输入的密码不一致", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("该用户名已存在，请更换用户名", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            nickname=nickname if nickname else username,
            created_at=datetime.now()
        )

        db.session.add(new_user)
        db.session.commit()

        flash("注册成功，请登录", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("用户名和密码不能为空", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("用户不存在", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password_hash, password):
            flash("密码错误", "danger")
            return redirect(url_for("auth.login"))

        if user.status != 1:
            flash("该账号已被禁用", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("登录成功", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")