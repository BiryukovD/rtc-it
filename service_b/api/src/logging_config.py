import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },

        "file_all": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "mode": "a",
        },
    },

    "loggers": {
        "book_app": {
            "level": "INFO",
            "handlers": ["console", "file_all"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file_all"]
    }
}
