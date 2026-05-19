import os
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from extensions import db


profile_bp = Blueprint("profile", __name__)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route("/profile")
@login_required
def profile_center():
    return render_template("profile.html")


@profile_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    nickname = request.form.get("nickname", "").strip()
    email = request.form.get("email", "").strip()
    avatar_url = request.form.get("avatar_url", "").strip()
    avatar_file = request.files.get("avatar_file")

    if not nickname:
        flash("昵称不能为空", "danger")
        return redirect(url_for("profile.profile_center"))

    current_user.nickname = nickname
    current_user.email = email

    # 1. 优先处理本地上传头像
    if avatar_file and avatar_file.filename:
        if not allowed_file(avatar_file.filename):
            flash("头像格式不支持，请上传 png、jpg、jpeg、gif 或 webp 格式图片", "danger")
            return redirect(url_for("profile.profile_center"))

        upload_folder = current_app.config.get("UPLOAD_FOLDER", "static/uploads/avatars")
        os.makedirs(upload_folder, exist_ok=True)

        original_filename = secure_filename(avatar_file.filename)
        ext = original_filename.rsplit(".", 1)[1].lower()
        new_filename = f"{current_user.user_id}_{uuid4().hex}.{ext}"

        save_path = os.path.join(upload_folder, new_filename)
        avatar_file.save(save_path)

        # 数据库存 static 下的相对路径，方便模板 url_for('static', filename=...)
        current_user.avatar = f"uploads/avatars/{new_filename}"

    # 2. 如果没有上传文件，但填写了图片 URL，则使用 URL
    elif avatar_url:
        current_user.avatar = avatar_url

    db.session.commit()

    flash("个人信息修改成功", "success")
    return redirect(url_for("profile.profile_center"))


@profile_bp.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not old_password or not new_password or not confirm_password:
        flash("请完整填写密码信息", "danger")
        return redirect(url_for("profile.profile_center"))

    if new_password != confirm_password:
        flash("两次输入的新密码不一致", "danger")
        return redirect(url_for("profile.profile_center"))

    if len(new_password) < 6:
        flash("新密码长度不能少于 6 位", "danger")
        return redirect(url_for("profile.profile_center"))

    if not check_password_hash(current_user.password_hash, old_password):
        flash("原密码错误", "danger")
        return redirect(url_for("profile.profile_center"))

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash("密码修改成功，请牢记新密码", "success")
    return redirect(url_for("profile.profile_center"))


@profile_bp.route("/help")
@login_required
def help_page():
    return render_template("help.html")