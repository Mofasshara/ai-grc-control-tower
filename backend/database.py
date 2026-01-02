import os

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from models import Base

DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_DATABASE_URL = DATABASE_URL
MANAGED_IDENTITY_ENABLED = os.getenv("MANAGED_IDENTITY_ENABLED", "false").lower() == "true"
AZURE_PG_SCOPE = os.getenv(
    "AZURE_PG_SCOPE",
    "https://ossrdbms-aad.database.windows.net/.default",
)


def _create_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    if not MANAGED_IDENTITY_ENABLED:
        return create_engine(DATABASE_URL, pool_pre_ping=True)

    try:
        from azure.identity import DefaultAzureCredential
        import psycopg2
    except ImportError as exc:
        raise RuntimeError(
            "Managed identity enabled but dependencies are missing. "
            "Install azure-identity and psycopg2-binary."
        ) from exc

    credential = DefaultAzureCredential()
    url = make_url(DATABASE_URL)

    def connect_with_token():
        token = credential.get_token(AZURE_PG_SCOPE).token
        return psycopg2.connect(
            host=url.host,
            port=url.port or 5432,
            user=url.username,
            dbname=url.database,
            password=token,
            sslmode="require",
        )

    return create_engine(DATABASE_URL, creator=connect_with_token, pool_pre_ping=True)


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
