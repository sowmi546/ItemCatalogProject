import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.schema import Sequence
from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

#creating class for User
class User(Base):
    __tablename__ = 'user'
    # id = Column(Integer, primary_key=True)
    id = Column(Integer, Sequence('user_id_seq', start=1001, increment=1), primary_key=True)
    name = Column(String(250),nullable=False,unique=True)
    uname=Column(String(250),unique=True)
    email = Column(String(250),nullable=False,unique=True)
    password_hash = Column(String(64))
    picture = Column(String(250))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    # def hash_password(self, password):
    #     self.password_hash = sha256_crypt.encrypt(password)
    #     print (isinstance(self.password_hash, (str)))
    #     print("Hello %s", self.password_hash)
    #
    #
    #
    # def verify_password(self, password):
    #     return sha256_crypt.verify(password, self.password_hash)

#creating class for category
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False,unique=True)
    user_name = Column(Integer,ForeignKey('user.uname'))
    user = relationship(User)
    @property
    def serialize(self):
        return{
            'name' : self.name,
            'id' : self.id,
        }

#creating class for Catalog Item
class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False,unique=True)
    description = Column(String(250))
    # category_id= Column(Integer, ForeignKey('category.id'))
    category_name= Column(String, ForeignKey('category.name'))
    category = relationship(Category)
    user_name = Column(Integer,ForeignKey('user.uname'))
    user = relationship(User)


    #serialize
    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,

        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
