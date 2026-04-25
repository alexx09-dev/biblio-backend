from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.usuario import Usuario
from models.libro import Libro
from models import Base

# 🔹 CONEXIONES

MYSQL_URL = "mysql://root:XgOZkLjgBYRPnosTmQPqeVehItiKdVLO@junction.proxy.rlwy.net:41896/railway"

POSTGRES_URL = "postgresql://neondb_owner:npg_V28NgfcnLZrH@ep-purple-rice-anhi6b0a-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

mysql_engine = create_engine(MYSQL_URL)
postgres_engine = create_engine(POSTGRES_URL)

MySQLSession = sessionmaker(bind=mysql_engine)
PostgresSession = sessionmaker(bind=postgres_engine)


# 🔹 CREAR TABLAS EN POSTGRES
Base.metadata.create_all(bind=postgres_engine)


def migrate():
    mysql = MySQLSession()
    postgres = PostgresSession()

    try:
        # 🔸 MIGRAR USUARIOS
        usuarios = mysql.query(Usuario).all()

        for u in usuarios:
            nuevo = Usuario(
                id=u.id,
                nombre=u.nombre,
                email=u.email
            )
            postgres.add(nuevo)

        postgres.commit()
        print("✅ Usuarios migrados")

        # 🔸 MIGRAR LIBROS
        libros = mysql.query(Libro).all()

        for l in libros:
            nuevo = Libro(
                id=l.id,
                titulo=l.titulo,
                autor=l.autor
            )
            postgres.add(nuevo)

        postgres.commit()
        print("✅ Libros migrados")

    except Exception as e:
        postgres.rollback()
        print("❌ Error:", e)

    finally:
        mysql.close()
        postgres.close()


if __name__ == "__main__":
    migrate()