import sys

from app import create_app, db
from config import get_current_config

app = create_app(
    get_current_config()
)


"""
This method will generate necessary tables from models
"""
def create_db():
    db.init_app(app)
    db.create_all()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'createdb':
        create_db()
    else:
        app.run(host='0.0.0.0', port=8000)