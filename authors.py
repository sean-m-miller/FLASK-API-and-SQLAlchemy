"""from sqlalchemy import Table, Column, Integer, ForeignKey, desc, asc
from sqlalchemy.orm import relationship
from flask_restful import Resource, reqparse

from db import db

class AuthorModel(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    books = relationship(
        "BookModel",
        secondary=association_table1,
        back_populates='contributors'
    )
"""
