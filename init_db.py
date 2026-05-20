from rifa_db import get_db_path, init_database

init_database()
print("Banco criado:", get_db_path())
