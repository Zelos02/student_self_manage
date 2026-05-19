from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Todo, FocusSession


focus_bp = Blueprint("focus", __name__, url_prefix="/focus")


@focus_bp.route("/start/<int:todo_id>", methods=["POST"])
@login_required
def start_focus(todo_id):
    todo = Todo.query.filter_by(
        todo_id=todo_id,
        user_id=current_user.user_id
    ).first_or_404()

    # 防止同一个用户同时开启多个计时
    running_session = FocusSession.query.filter_by(
        user_id=current_user.user_id,
        session_status="进行中"
    ).first()

    if running_session:
        flash("你当前已有正在进行的计时，请先结束后再开始新的计时", "warning")
        return redirect(url_for("focus.focus_session", session_id=running_session.session_id))

    session = FocusSession(
        user_id=current_user.user_id,
        todo_id=todo.todo_id,
        start_time=datetime.now(),
        session_status="进行中"
    )

    todo.status = "进行中"

    db.session.add(session)
    db.session.commit()

    flash("计时已开始", "success")
    return redirect(url_for("focus.focus_session", session_id=session.session_id))


@focus_bp.route("/session/<int:session_id>")
@login_required
def focus_session(session_id):
    session = FocusSession.query.filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first_or_404()

    todo = Todo.query.filter_by(
        todo_id=session.todo_id,
        user_id=current_user.user_id
    ).first_or_404()

    return render_template(
        "focus_session.html",
        session=session,
        todo=todo
    )


@focus_bp.route("/end/<int:session_id>", methods=["POST"])
@login_required
def end_focus(session_id):
    session = FocusSession.query.filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first_or_404()

    todo = Todo.query.filter_by(
        todo_id=session.todo_id,
        user_id=current_user.user_id
    ).first_or_404()

    if session.session_status == "已结束":
        flash("该计时记录已经结束", "warning")
        return redirect(url_for("todo.todo_list"))

    session.end_time = datetime.now()

    # 这里手动算一遍，方便不依赖触发器也能正常显示。
    # MySQL 触发器也会自动计算，二者不会冲突。
    duration = session.end_time - session.start_time
    session.duration_seconds = int(duration.total_seconds())
    session.session_status = "已结束"

    todo.status = "已完成"

    db.session.commit()

    flash("计时已结束，记录已保存", "success")
    return redirect(url_for("todo.todo_list"))