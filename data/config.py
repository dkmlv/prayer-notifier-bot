from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN = env.str("ADMIN")

HOST = env.str("HOST")
PORT = env.str("PORT")
DB_USER = env.str("DATABASE_ROOT_USERNAME")
DB_PSSWD = env.str("DATABASE_ROOT_PASSWORD")

