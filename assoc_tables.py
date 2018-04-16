"""from sqlalchemy import Table, Column, Integer, ForeignKey, or_
from sqlalchemy.orm import relationship
from flask_restful import Resource, reqparse

from db import db

association_table1 = db.Table('association',
    db.Column('isbn', db.Integer, db.ForeignKey('authors.author_id')),
    db.Column('author_id', db.Integer, db.ForeignKey('books.isbn'))
)
"""
