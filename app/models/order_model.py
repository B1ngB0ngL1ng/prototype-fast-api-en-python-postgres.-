# # Dit principe heet ORM (Object-Relational Mapping): de koppeling tussen objecten in Python en tabellen in een relationele database zoals PostgreSQL.


# from datetime import datetime

# from sqlalchemy import DateTime, Integer, String, func
# from sqlalchemy.orm import Mapped, mapped_column

# from app.databases.base import Base


# class Order(Base):

#     __tablename__ = "orders"

#     # Mapped[type] geeft aan welk Python-type het attribuut heeft
#     # en dat SQLAlchemy het koppelt aan een databasekolom.
#     #
#     # mapped_column() bepaalt hoe de kolom wordt opgeslagen,
#     # bijvoorbeeld het SQL-datatype en de beperkingen.

#     # Uniek ID voor iedere order.
#     id: Mapped[int] = mapped_column(
#         Integer,             # SQL-datatype INTEGER.
#         primary_key=True,    # Primaire sleutel: identificeert iedere order.
#         autoincrement=True   
#     )

#     # Unieke referentie waarmee we een order kunnen herkennen.
#     reference: Mapped[str] = mapped_column(
#         String(100),         # Tekst met maximaal 100 tekens.
#         unique=True,         # Dezelfde referentie mag niet dubbel voorkomen.
#         nullable=False       # Dit veld mag niet NULL zijn.
#     )

#     # De huidige status van de order.
#     status: Mapped[str] = mapped_column(
#         String(50),          # Tekst met maximaal 50 tekens.
#         default="pending",   # SQLAlchemy gebruikt deze standaardwaarde
#                              # als er geen status wordt meegegeven.
#         nullable=False       # De status mag niet NULL zijn.
#     )

#     # Datum en tijd waarop de order wordt aangemaakt.
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),  # Datum en tijd met tijdzoneondersteuning.
#         server_default=func.now(), # PostgreSQL vult automatisch de tijd in.
#         nullable=False            # Dit veld mag niet NULL zijn.
#     )
