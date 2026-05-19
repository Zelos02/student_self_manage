from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Todo, Category


todo_bp = Blueprint("todo", __name__, url_prefix="/todos")


def parse_datetime(value):
    """
    处理 HTML datetime-local 提交的时间格式。
    例如：2026-01-10T22:00
    """
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


@todo_bp.route("/")
@login_required
def todo_list():
    todos = (
        Todo.query
        .filter_by(user_id=current_user.user_id)
        .order_by(Todo.created_at.desc())
        .all()
    )

    categories = (
        Category.query
        .filter_by(user_id=current_user.user_id)
        .order_by(Category.created_at.desc())
        .all()
    )

    category_map = {
        category.category_id: category.category_name
        for category in categories
    }

    return render_template(
        "todo_list.html",
        todos=todos,
        category_map=category_map
    )


@todo_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_todo():
    categories = (
        Category.query
        .filter_by(user_id=current_user.user_id)
        .order_by(Category.created_at.desc())
        .all()
    )

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        timing_mode = request.form.get("timing_mode", "count_up")
        target_minutes = request.form.get("target_minutes", "").strip()
        due_time = request.form.get("due_time", "").strip()
        remind_before_minutes = request.form.get("remind_before_minutes", "").strip()
        category_id = request.form.get("category_id", "").strip()
        new_category_name = request.form.get("new_category_name", "").strip()

        if not title:
            flash("待办事项标题不能为空", "danger")
            return redirect(url_for("todo.add_todo"))

        if timing_mode not in ["count_up", "count_down"]:
            timing_mode = "count_up"

        target_minutes = int(target_minutes) if target_minutes else None
        remind_before_minutes = int(remind_before_minutes) if remind_before_minutes else 10
        due_time = parse_datetime(due_time)

        final_category_id = None

        if category_id:
            category = Category.query.filter_by(
                category_id=int(category_id),
                user_id=current_user.user_id
            ).first()

            if category:
                final_category_id = category.category_id

        elif new_category_name:
            new_category = Category(
                user_id=current_user.user_id,
                category_name=new_category_name,
                color="#409EFF"
            )
            db.session.add(new_category)
            db.session.flush()
            final_category_id = new_category.category_id

        todo = Todo(
            user_id=current_user.user_id,
            category_id=final_category_id,
            title=title,
            description=description,
            timing_mode=timing_mode,
            target_minutes=target_minutes,
            due_time=due_time,
            remind_before_minutes=remind_before_minutes,
            status="未开始"
        )

        db.session.add(todo)
        db.session.commit()

        flash("待办事项添加成功", "success")
        return redirect(url_for("todo.todo_list"))

    return render_template("todo_form.html", todo=None, categories=categories)


@todo_bp.route("/edit/<int:todo_id>", methods=["GET", "POST"])
@login_required
def edit_todo(todo_id):
    todo = Todo.query.filter_by(
        todo_id=todo_id,
        user_id=current_user.user_id
    ).first_or_404()

    categories = (
        Category.query
        .filter_by(user_id=current_user.user_id)
        .order_by(Category.created_at.desc())
        .all()
    )

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        timing_mode = request.form.get("timing_mode", "count_up")
        target_minutes = request.form.get("target_minutes", "").strip()
        due_time = request.form.get("due_time", "").strip()
        remind_before_minutes = request.form.get("remind_before_minutes", "").strip()
        category_id = request.form.get("category_id", "").strip()
        new_category_name = request.form.get("new_category_name", "").strip()
        status = request.form.get("status", "未开始")

        if not title:
            flash("待办事项标题不能为空", "danger")
            return redirect(url_for("todo.edit_todo", todo_id=todo.todo_id))

        if timing_mode not in ["count_up", "count_down"]:
            timing_mode = "count_up"

        if status not in ["未开始", "进行中", "已完成", "已取消"]:
            status = "未开始"

        target_minutes = int(target_minutes) if target_minutes else None
        remind_before_minutes = int(remind_before_minutes) if remind_before_minutes else 10
        due_time = parse_datetime(due_time)

        final_category_id = None

        if category_id:
            category = Category.query.filter_by(
                category_id=int(category_id),
                user_id=current_user.user_id
            ).first()

            if category:
                final_category_id = category.category_id

        elif new_category_name:
            new_category = Category(
                user_id=current_user.user_id,
                category_name=new_category_name,
                color="#409EFF"
            )
            db.session.add(new_category)
            db.session.flush()
            final_category_id = new_category.category_id

        todo.title = title
        todo.description = description
        todo.timing_mode = timing_mode
        todo.target_minutes = target_minutes
        todo.due_time = due_time
        todo.remind_before_minutes = remind_before_minutes
        todo.category_id = final_category_id
        todo.status = status

        db.session.commit()

        flash("待办事项修改成功", "success")
        return redirect(url_for("todo.todo_list"))

    return render_template("todo_form.html", todo=todo, categories=categories)


@todo_bp.route("/delete/<int:todo_id>", methods=["POST"])
@login_required
def delete_todo(todo_id):
    todo = Todo.query.filter_by(
        todo_id=todo_id,
        user_id=current_user.user_id
    ).first_or_404()

    db.session.delete(todo)
    db.session.commit()

    flash("待办事项删除成功", "success")
    return redirect(url_for("todo.todo_list"))


@todo_bp.route("/finish/<int:todo_id>", methods=["POST"])
@login_required
def finish_todo(todo_id):
    todo = Todo.query.filter_by(
        todo_id=todo_id,
        user_id=current_user.user_id
    ).first_or_404()

    todo.status = "已完成"
    db.session.commit()

    flash("待办事项已标记为完成", "success")
    return redirect(url_for("todo.todo_list"))