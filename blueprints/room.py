from datetime import date, datetime, timedelta
from calendar import monthrange
import random
import string

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import and_, func

from extensions import db
from models import User, Room, RoomMember, FocusSession, WishWall


room_bp = Blueprint("room", __name__, url_prefix="/rooms")


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


def generate_room_code(length=6):
    """生成唯一自习室邀请码"""
    chars = string.ascii_uppercase + string.digits

    while True:
        code = "".join(random.choice(chars) for _ in range(length))
        exists = Room.query.filter_by(room_code=code).first()

        if not exists:
            return code


def get_range(range_type):
    today = date.today()

    if range_type == "month":
        first_day = today.replace(day=1)
        last_day_number = monthrange(today.year, today.month)[1]
        last_day = today.replace(day=last_day_number)
        return first_day, last_day

    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def check_room_member(room_id):
    """判断当前用户是否已经加入该自习室"""
    return RoomMember.query.filter_by(
        room_id=room_id,
        user_id=current_user.user_id
    ).first()


@room_bp.route("/")
@login_required
def room_list():
    joined_rooms = (
        db.session.query(Room, RoomMember)
        .join(RoomMember, Room.room_id == RoomMember.room_id)
        .filter(RoomMember.user_id == current_user.user_id)
        .order_by(Room.created_at.desc())
        .all()
    )

    return render_template(
        "room_list.html",
        joined_rooms=joined_rooms
    )


@room_bp.route("/create", methods=["POST"])
@login_required
def create_room():
    room_name = request.form.get("room_name", "").strip()

    if not room_name:
        flash("自习室名称不能为空", "danger")
        return redirect(url_for("room.room_list"))

    room = Room(
        room_name=room_name,
        creator_id=current_user.user_id,
        room_code=generate_room_code(),
        created_at=datetime.now()
    )

    db.session.add(room)
    db.session.flush()

    member = RoomMember(
        room_id=room.room_id,
        user_id=current_user.user_id,
        joined_at=datetime.now()
    )

    db.session.add(member)
    db.session.commit()

    flash("自习室创建成功，你已自动加入该自习室", "success")
    return redirect(url_for("room.room_detail", room_id=room.room_id))


@room_bp.route("/join", methods=["POST"])
@login_required
def join_room():
    room_code = request.form.get("room_code", "").strip().upper()

    if not room_code:
        flash("请输入自习室邀请码", "danger")
        return redirect(url_for("room.room_list"))

    room = Room.query.filter_by(room_code=room_code).first()

    if not room:
        flash("邀请码不存在，请检查后重新输入", "danger")
        return redirect(url_for("room.room_list"))

    existing_member = RoomMember.query.filter_by(
        room_id=room.room_id,
        user_id=current_user.user_id
    ).first()

    if existing_member:
        flash("你已经加入该自习室", "warning")
        return redirect(url_for("room.room_detail", room_id=room.room_id))

    member = RoomMember(
        room_id=room.room_id,
        user_id=current_user.user_id,
        joined_at=datetime.now()
    )   

    db.session.add(member)
    db.session.commit()

    flash("加入自习室成功", "success")
    return redirect(url_for("room.room_detail", room_id=room.room_id))


@room_bp.route("/<int:room_id>")
@login_required
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)

    member = check_room_member(room_id)
    if not member:
        flash("你还没有加入该自习室，不能查看详情", "danger")
        return redirect(url_for("room.room_list"))

    range_type = request.args.get("range_type", "week")

    if range_type not in ["week", "month"]:
        range_type = "week"

    start_date, end_date = get_range(range_type)

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

    total_seconds_expr = func.coalesce(func.sum(FocusSession.duration_seconds), 0)

    ranking_rows = (
        db.session.query(
            User.user_id,
            User.username,
            User.nickname,
            total_seconds_expr.label("total_seconds")
        )
        .join(RoomMember, RoomMember.user_id == User.user_id)
        .outerjoin(
            FocusSession,
            and_(
                FocusSession.user_id == User.user_id,
                FocusSession.end_time.isnot(None),
                FocusSession.start_time >= start_datetime,
                FocusSession.start_time < end_datetime
            )
        )
        .filter(RoomMember.room_id == room_id)
        .group_by(User.user_id, User.username, User.nickname)
        .order_by(total_seconds_expr.desc())
        .all()
    )

    rankings = []

    for index, row in enumerate(ranking_rows, start=1):
        rankings.append({
            "rank": index,
            "user_id": row.user_id,
            "username": row.username,
            "nickname": row.nickname or row.username,
            "total_seconds": row.total_seconds or 0,
            "total_time_text": format_duration(row.total_seconds or 0)
        })

    wish_rows = (
        db.session.query(WishWall, User)
        .join(User, WishWall.user_id == User.user_id)
        .filter(
            WishWall.room_id == room_id,
            WishWall.is_public == 1
        )
        .order_by(WishWall.created_at.desc())
        .all()
    )

    wishes = []

    for wish, user in wish_rows:
        wishes.append({
            "wish_id": wish.wish_id,
            "content": wish.content,
            "created_at": wish.created_at.strftime("%Y-%m-%d %H:%M:%S") if wish.created_at else "",
            "nickname": user.nickname or user.username,
            "user_id": user.user_id
        })

    member_count = RoomMember.query.filter_by(room_id=room_id).count()

    return render_template(
        "room_detail.html",
        room=room,
        range_type=range_type,
        start_date=start_date,
        end_date=end_date,
        rankings=rankings,
        wishes=wishes,
        member_count=member_count
    )


@room_bp.route("/<int:room_id>/wish", methods=["POST"])
@login_required
def add_wish(room_id):
    room = Room.query.get_or_404(room_id)

    member = check_room_member(room_id)
    if not member:
        flash("你还没有加入该自习室，不能发布心愿", "danger")
        return redirect(url_for("room.room_list"))

    content = request.form.get("content", "").strip()

    if not content:
        flash("心愿内容不能为空", "danger")
        return redirect(url_for("room.room_detail", room_id=room.room_id))

    wish = WishWall(
        user_id=current_user.user_id,
        room_id=room.room_id,
        content=content,
        is_public=1,
        created_at=datetime.now()
    )

    db.session.add(wish)
    db.session.commit()

    flash("心愿发布成功", "success")
    return redirect(url_for("room.room_detail", room_id=room.room_id))


@room_bp.route("/<int:room_id>/leave", methods=["POST"])
@login_required
def leave_room(room_id):
    room = Room.query.get_or_404(room_id)

    member = RoomMember.query.filter_by(
        room_id=room.room_id,
        user_id=current_user.user_id
    ).first()

    if not member:
        flash("你还没有加入该自习室", "warning")
        return redirect(url_for("room.room_list"))

    db.session.delete(member)
    db.session.commit()

    flash("已退出自习室", "success")
    return redirect(url_for("room.room_list"))