"""本地测试配置：用 sqlite 代替 postgres，便于无数据库环境跑测试。"""

from config.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
