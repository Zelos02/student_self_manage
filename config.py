class Config:
    SECRET_KEY = "student-self-manage-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:123456@localhost:3306/student_manage?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/uploads/avatars"
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024