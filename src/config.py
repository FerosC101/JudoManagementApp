import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "judo_management"),
    "user": os.getenv("DB_USER", "vince"),
    "password": os.getenv("DB_PASSWORD", "426999"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}
