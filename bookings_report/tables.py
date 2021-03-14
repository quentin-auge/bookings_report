from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

MappedTable = declarative_base()


def get_bookings_table(table_name: str) -> MappedTable:
    """
    Get sqlalchemy's booking table mapper

    Args:
        table_name: table name
    """

    class Bookings(MappedTable):
        __tablename__ = table_name
        booking_id = Column(UUID, primary_key=True)
        restaurant_id = Column(UUID, nullable=False)
        restaurant_name = Column(String, nullable=False)
        client_id = Column(UUID, nullable=False)
        client_name = Column(String, nullable=False)
        amount = Column(Numeric(5, 2), nullable=False)
        currency = Column(String, nullable=False)
        guests = Column(Integer, nullable=False)
        date = Column(Date, nullable=False)
        country = Column(String, nullable=False)

    return Bookings