import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if (not TURSO_AUTH_TOKEN) or (not TURSO_DATABASE_URL):
    raise RuntimeError("please pass db details in .env!")

class DatabaseManager:

    def __init__(self):
        # Secure configuration via environment variables
        self.url = TURSO_DATABASE_URL
        self.token = TURSO_AUTH_TOKEN
        self.db_path = "embedded.db"
        
        self.engine = create_engine(
            f"sqlite+libsql:///{self.db_path}",
            connect_args={
                "auth_token": self.token,
                "sync_url": self.url,
            },
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def sync_with_cloud(self) -> bool:
        """Attempts to sync local replica with Turso cloud. Returns True if successful."""
        with self.engine.connect() as conn:
            libsql_conn = conn.connection.dbapi_connection
            try:
                libsql_conn.sync()
                return True
            except Exception:
                # Silently fail for offline mode handling
                return False

    def get_session(self):
        """Context manager provider for sessions."""
        return self.SessionLocal()

# Singleton instance for the application lifecycle
db = DatabaseManager()