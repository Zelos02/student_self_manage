# 大学生自我管理系统

一个基于 Python Flask + MySQL 开发的大学生自我管理 Web 系统。系统围绕大学生日常学习与生活计划管理展开，提供用户登录注册、待办事项管理、专注计时、数据统计、自习室排行榜、心愿墙、个人中心和帮助页面等功能。

## 项目简介

随着智能手机和网络应用的普及，大学生在学习和生活中容易受到碎片化信息影响，导致时间安排不清晰、任务完成效率下降。本系统旨在帮助大学生对学习生活进行计划、记录、统计和监督，通过待办事项和专注计时功能，让用户更清楚地了解自己的时间使用情况。

系统采用 B/S 架构，用户通过浏览器访问系统，后端使用 Flask 处理业务逻辑，数据库使用 MySQL 存储用户信息、待办事项、计时记录、自习室信息和心愿墙内容。

---

## 技术栈

| 类型 | 技术 |
|---|---|
| 后端框架 | Python Flask |
| 数据库 | MySQL |
| ORM | Flask-SQLAlchemy |
| 登录管理 | Flask-Login |
| 前端页面 | HTML、CSS、Bootstrap |
| 图表展示 | ECharts |
| 密码加密 | Werkzeug Security |
| 数据库驱动 | PyMySQL |
| 头像上传 | Flask 文件上传 |

---

## 主要功能

### 1. 用户登录注册

- 用户注册
- 用户登录
- 用户退出
- 密码加密存储
- 登录状态保护

### 2. 待办事项管理

- 添加待办事项
- 修改待办事项
- 删除待办事项
- 标记待办事项完成
- 设置事项分类
- 设置正向计时或倒计时
- 设置目标时间、截止时间和提醒时间

### 3. 专注计时

- 从待办事项开始计时
- 支持正向计时
- 支持倒计时
- 记录开始时间
- 记录结束时间
- 自动计算持续时长
- 将计时记录保存到数据库

### 4. 数据统计

- 查看指定日期的待办事项用时
- 使用柱状图展示每日任务用时
- 查看本周或本月分类时间占比
- 使用饼图展示时间分布比例
- 查看每日计时明细记录
- 显示开始时间、结束时间和持续时长

### 5. 自习室与排行榜

- 创建自习室
- 生成自习室邀请码
- 通过邀请码加入自习室
- 查看自习室成员
- 根据专注时长生成排行榜
- 支持本周排行榜和本月排行榜

### 6. 心愿墙

- 自习室成员可以发布心愿
- 展示发布人、发布时间和心愿内容
- 用于记录学习目标和鼓励语

### 7. 个人中心

- 查看个人信息
- 修改昵称
- 修改邮箱
- 上传本地头像
- 使用网络图片作为头像
- 修改登录密码
- 查看注册时间

### 8. 帮助页面

- 软件介绍
- 功能说明
- 基本操作流程说明

---

## 项目结构

```text
student_self_manage/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
│
├── blueprints/
│   ├── __init__.py
│   ├── auth.py
│   ├── todo.py
│   ├── focus.py
│   ├── stats.py
│   ├── room.py
│   └── profile.py
│
├── database/
│   └── schema.sql
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── todo_list.html
│   ├── todo_form.html
│   ├── focus_session.html
│   ├── statistics.html
│   ├── room_list.html
│   ├── room_detail.html
│   ├── profile.html
│   └── help.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── uploads/
│       └── avatars/
│
└── README.md
```

---

## 数据库设计

系统主要包含以下数据表：

| 数据表 | 说明 |
|---|---|
| users | 用户信息表 |
| categories | 待办事项分类表 |
| todos | 待办事项表 |
| focus_sessions | 专注计时记录表 |
| rooms | 自习室表 |
| room_members | 自习室成员表 |
| wish_wall | 心愿墙表 |

此外，系统还设计了统计视图和存储过程，例如：

- `v_daily_todo_time`：每日待办事项用时统计视图
- `v_daily_category_time`：每日分类用时统计视图
- `sp_room_ranking`：自习室排行榜存储过程

---

## 环境要求

建议使用以下环境：

```text
Python 3.10+
MySQL 8.0+
Windows / macOS / Linux
```

---

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/student-self-manage.git
cd student-self-manage
```

### 2. 创建虚拟环境

Windows：

```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux：

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

如果连接 MySQL 时报以下错误：

```text
RuntimeError: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
```

可以额外安装：

```bash
pip install cryptography
```

### 4. 创建 MySQL 数据库

进入 MySQL 后执行数据库脚本：

```sql
SOURCE database/schema.sql;
```

或者手动执行 `database/schema.sql` 中的建库建表语句。

### 5. 修改数据库配置

打开 `config.py`，根据自己的 MySQL 用户名和密码修改：

```python
class Config:
    SECRET_KEY = "student-self-manage-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:你的MySQL密码@localhost:3306/student_manage?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/uploads/avatars"
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
```

### 6. 启动项目

```bash
python app.py
```

启动成功后，在浏览器访问：

```text
http://127.0.0.1:5000
```

---

## 局域网访问

如果希望同一 Wi-Fi 下的朋友访问，可以将 `app.py` 最后一行改成：

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

然后朋友可以通过你的 IPv4 地址访问，例如：

```text
http://192.168.1.23:5000
```

注意：需要保证 Flask 和 MySQL 都在运行，并且 Windows 防火墙允许 Python 访问网络。

---

## 主要页面路径

| 页面 | 路径 |
|---|---|
| 登录 | `/login` |
| 注册 | `/register` |
| 首页 | `/dashboard` |
| 待办事项 | `/todos/` |
| 添加待办事项 | `/todos/add` |
| 数据统计 | `/statistics/` |
| 自习室 | `/rooms/` |
| 个人中心 | `/profile` |
| 帮助页面 | `/help` |

---

## 使用流程

1. 注册账号并登录系统。
2. 进入“待办事项”，添加学习或生活计划。
3. 为待办事项设置分类、计时方式、目标时间和提醒时间。
4. 点击“开始”进入专注计时页面。
5. 完成任务后点击“结束计时”。
6. 进入“数据统计”查看柱状图、饼图和计时明细。
7. 创建或加入自习室，与同学一起查看专注排行榜。
8. 在心愿墙发布学习目标。
9. 在个人中心修改个人资料和头像。

---

## 项目截图

可以在这里放项目运行截图：

```text
docs/images/login.png
docs/images/dashboard.png
docs/images/todo.png
docs/images/statistics.png
docs/images/room.png
docs/images/profile.png
```

示例：

```markdown
![首页](docs/images/dashboard.png)
![数据统计](docs/images/statistics.png)
```

---

## 注意事项

1. 第一次运行前需要先创建 MySQL 数据库。
2. `config.py` 中的数据库密码需要改成自己的 MySQL 密码。
3. 如果使用本地头像上传功能，需要确保目录存在：

```text
static/uploads/avatars/
```

4. 上传头像默认限制为 2MB。
5. 如果要上传到 GitHub，建议不要上传虚拟环境 `venv/`。
6. 如果项目要部署到公网环境，不建议使用 Flask 自带开发服务器直接运行。

---

## 推荐 `.gitignore`

建议在项目根目录创建 `.gitignore` 文件，并写入：

```gitignore
venv/
__pycache__/
*.pyc
*.pyo
*.pyd

.env
instance/

.DS_Store
Thumbs.db

.idea/
.vscode/

static/uploads/avatars/*
!static/uploads/avatars/.gitkeep

*.log
```

如果想保留头像上传目录，可以在：

```text
static/uploads/avatars/
```

里面新建一个空文件：

```text
.gitkeep
```

---

## 未来可改进方向

- 增加后台管理员功能
- 增加任务提醒弹窗
- 增加邮件提醒功能
- 增加任务优先级
- 增加数据导出功能
- 增加移动端适配
- 支持自习室聊天功能
- 支持头像裁剪和压缩
- 支持更丰富的数据可视化图表

---

## 作者

```text
作者：Zelos02
课程：数据库课程设计
项目名称：大学生自我管理系统
```

---

## License

本项目仅用于课程设计和学习交流。
