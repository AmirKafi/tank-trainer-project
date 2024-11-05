from domains.models.City import City
from sqlalchemy import UUID, Column, String,ForeignKey
from sqlalchemy.orm import declarative_base,relationship
import uuid

Base = declarative_base()
#Author is an Entity that has a City along with it's other datas
class Author(Base):
    __tablename__  = "Authors"
    _id = Column("Id",UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _first_name = Column("FirstName",String, nullable=False)
    _last_name = Column("LastName",String,nullable=False)
    _city_id = Column("CityId", UUID(as_uuid=True), ForeignKey("Cities.Id"), nullable=False)  # ForeignKey to City

    # Define relationship with City
    _city = relationship("City", back_populates="_authors")
    
    def __init__(self,first_name:str,last_name:str,city:City):
        self._id = uuid.uuid4()
        self._first_name = first_name
        self._last_name = last_name
        self._city = city

    def __str__(self):
        return self._first_name + ' ' + self._last_name

    @property
    def first_name(self) ->str:
        return self._first_name

    @property
    def last_name(self)-> str:
        return self._last_name

    @property
    def city_name(self)-> str:
        return self._city