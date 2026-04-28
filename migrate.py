from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

# ✅ IMPORTAR MODELOS CORRECTAMENTE
from models.usuario import Usuario
from models.libro import Libro

# 🔴 BD antigua (MySQL)
old_engine = create_engine(settings.OLD_DATABASE_URL)

# 🟢 BD nueva (Neon)
new_engine = create_engine(settings.DATABASE_URL)

OldSession = sessionmaker(bind=old_engine)
NewSession = sessionmaker(bind=new_engine)

old_db = OldSession()
new_db = NewSession()


def migrar_usuarios():
    usuarios = old_db.execute(text("SELECT * FROM usuarios")).fetchall()

    for u in usuarios:
        nuevo = Usuario(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            password_hash=u.password_hash,
            fecha_nacimiento=u.fecha_nacimiento,
            foto_perfil=u.foto_perfil,
            avatar_config=u.avatar_config,
            bio=u.bio,
            generos_favoritos=u.generos_favoritos,
        )
        new_db.add(nuevo)

    new_db.commit()
    print(f"Usuarios migrados: {len(usuarios)}")


def migrar_libros():
    libros = old_db.execute(text("SELECT * FROM libros")).fetchall()

    for l in libros:
        nuevo = Libro(
            id=l.id,
            titulo=l.titulo,
            autor=l.autor,
            rating=l.rating,
            isbn=l.isbn,
            genero=l.genero,
            anio=l.anio,
            sinopsis=l.sinopsis,
            es_favorito=bool(l.es_favorito),
            usuario_id=l.usuario_id,
        )
        new_db.add(nuevo)

    new_db.commit()
    print(f"Libros migrados: {len(libros)}")


if __name__ == "__main__":
    migrar_usuarios()
    migrar_libros()
    print("Migración completada 🚀")