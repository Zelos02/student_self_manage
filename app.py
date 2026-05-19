from flask import Flask
from sqlalchemy import text
from config import Config
from extensions import db, login_manager

from models import User, Category, Todo, FocusSession, Room, RoomMember, WishWall


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    from blueprints.todo import todo_bp
    app.register_blueprint(todo_bp)

    from blueprints.focus import focus_bp
    app.register_blueprint(focus_bp)

    from blueprints.stats import stats_bp
    app.register_blueprint(stats_bp)

    from blueprints.room import room_bp
    app.register_blueprint(room_bp)

    from blueprints.profile import profile_bp
    app.register_blueprint(profile_bp)

    @app.route("/db-test")
    def db_test():
        try:
            result = db.session.execute(text("SHOW TABLES;"))
            tables = [row[0] for row in result]

            html = "<h2>数据库连接成功！</h2>"
            html += "<p>当前数据库 student_manage 中的数据表：</p>"
            html += "<ul>"
            for table in tables:
                html += f"<li>{table}</li>"
            html += "</ul>"

            return html

        except Exception as e:
            return f"<h2>数据库连接失败</h2><p>{str(e)}</p>"

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)