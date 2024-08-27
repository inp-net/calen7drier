from os import getenv
from pathlib import Path
import typed_dotenv
from pydantic import BaseModel


class Environment(BaseModel):
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str
    ORIGIN: str
    LOGIN_AS: str
    PASSWORD: str
    ADE_PROJECT_ID: str


dotenv_file = Path(__file__).parent.parent / ".env"
env: Environment

if dotenv_file.exists():
    env = typed_dotenv.load_into(Environment, filename=dotenv_file)
else:
    env = Environment(
        OAUTH_CLIENT_ID=getenv("OAUTH_CLIENT_ID"),
        OAUTH_CLIENT_SECRET=getenv("OAUTH_CLIENT_SECRET"),
        ORIGIN=getenv("ORIGIN"),
        LOGIN_AS=getenv("LOGIN_AS"),
        PASSWORD=getenv("PASSWORD"),
        ADE_PROJECT_ID=getenv("ADE_PROJECT_ID"),
    )
