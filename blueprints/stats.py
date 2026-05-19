from datetime import date, datetime, timedelta
from calendar import monthrange

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text, func

from extensions import db
from models import FocusSession, Todo, Category


stats_bp = Blueprint("stats", __name__, url_prefix="/statistics")


def parse_date(value):
    if not value:
        return date.today()

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def get_range(selected_date, range_type):
    if range_type == "month":
        first_day = selected_date.replace(day=1)
        last_day_number = monthrange(selected_date.year, selected_date.month)[1]
        last_day = selected_date.replace(day=last_day_number)
        return first_day, last_day

    monday = selected_date - timedelta(days=selected_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def format_duration(seconds):
    seconds = int(seconds or 0)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remain_seconds = seconds % 60

    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    if minutes > 0:
        return f"{minutes}分钟{remain_seconds}秒"
    return f"{remain_seconds}秒"


@stats_bp.route("/")
@login_required
def index():
    selected_date = parse_date(request.args.get("date"))
    range_type = request.args.get("range_type", "week")

    if range_type not in ["week", "month"]:
        range_type = "week"

    start_date, end_date = get_range(selected_date, range_type)

    # 1. 查询某一天各待办事项用时，用于柱状图
    daily_rows = db.session.execute(
        text("""
            SELECT title, total_seconds
            FROM v_daily_todo_time
            WHERE user_id = :user_id
              AND focus_date = :focus_date
            ORDER BY total_seconds DESC
        """),
        {
            "user_id": current_user.user_id,
            "focus_date": selected_date
        }
    ).mappings().all()

    daily_labels = [row["title"] for row in daily_rows]
    daily_values = [
        round((row["total_seconds"] or 0) / 60, 2)
        for row in daily_rows
    ]

    # 2. 查询本周或本月分类用时，用于饼图
    category_rows = db.session.execute(
        text("""
            SELECT category_name, SUM(total_seconds) AS total_seconds
            FROM v_daily_category_time
            WHERE user_id = :user_id
              AND focus_date BETWEEN :start_date AND :end_date
            GROUP BY category_name
            ORDER BY total_seconds DESC
        """),
        {
            "user_id": current_user.user_id,
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().all()

    category_data = [
        {
            "name": row["category_name"] or "未分类",
            "value": round((row["total_seconds"] or 0) / 60, 2)
        }
        for row in category_rows
    ]

    # 3. 查询某一天的详细计时记录，带真实分类
    session_query_results = (
        db.session.query(FocusSession, Todo, Category)
        .join(Todo, FocusSession.todo_id == Todo.todo_id)
        .outerjoin(Category, Todo.category_id == Category.category_id)
        .filter(FocusSession.user_id == current_user.user_id)
        .filter(func.date(FocusSession.start_time) == selected_date)
        .filter(FocusSession.end_time.isnot(None))
        .order_by(FocusSession.start_time.desc())
        .all()
    )

    records = []

    for session, todo, category in session_query_results:
        duration_seconds = session.duration_seconds or 0

        records.append({
            "title": todo.title,
            "category_name": category.category_name if category else "未分类",
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration_seconds": duration_seconds,
            "duration_text": format_duration(duration_seconds),
            "duration_minutes": round(duration_seconds / 60, 2)
        })

    total_seconds_today = sum(
        record["duration_seconds"] or 0
        for record in records
    )

    total_minutes_today = round(total_seconds_today / 60, 2)
    record_count = len(records)
    task_count = len(daily_labels)

    avg_minutes = 0
    if record_count > 0:
        avg_minutes = round(total_minutes_today / record_count, 2)

    return render_template(
        "statistics.html",
        selected_date=selected_date,
        range_type=range_type,
        start_date=start_date,
        end_date=end_date,
        daily_labels=daily_labels,
        daily_values=daily_values,
        category_data=category_data,
        records=records,
        total_minutes_today=total_minutes_today,
        record_count=record_count,
        task_count=task_count,
        avg_minutes=avg_minutes
    )