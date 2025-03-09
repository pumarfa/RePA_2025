from src.db.database import init_db, SessionLocal
from src.models.user_model import Role
from sqlalchemy.exc import IntegrityError

def seed_data():
    # Inicializa las tablas
    init_db()

    db = SessionLocal()
    try:
        # Verifica si ya existen roles
        if not db.query(Role).first():
            roles = [
                Role(rol="admin"),
                Role(rol="user")
            ]
            db.add_all(roles)
            db.commit()
            print("Seed de roles completado.")
        else:
            print("Los roles ya existen, saltando el seed.")
    except IntegrityError as e:
        db.rollback()
        print("Error insertando seed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()