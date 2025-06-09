import os

# sets the DB URI to use a SQLite database named users.db.
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://root:{os.getenv('DB_PW')}@localhost/library_db"
    )
    DEBUG = True


class TestingConfig:
    pass


class ProductionConfig:
    pass
