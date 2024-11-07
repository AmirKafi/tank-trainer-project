import os

SQLALCHEMY_DATABASE_URL = "sqlite:///C:/Users/AmirKafi/PycharmProjects/tank-trainer-project/database.db"

def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"

QUEUE_NAMES = {
    'BookCreationQueue':'book_creation'
}
