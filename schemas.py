from marshmallow import Schema, fields, validate, post_load
from models import User, Class, Book


class UserSchema(Schema):
    id = fields.Integer()
    Firstname = fields.Str(validate=validate.Length(max=45), nullable=False)
    Lastname = fields.Str(validate=validate.Length(max=45), nullable=False)
    properties = fields.Str(validate=validate.OneOf(["Admin", "User"]), required=True)
    authorization = fields.Str(validate=validate.Length(max=45), required=True)

    @post_load
    def make_user(self, data,**kwargs):
        return User(**data)


class ClassSchema(Schema):
    id = fields.Integer()
    adress = fields.Str(validate=validate.Length(max=45), nullable=False)
    name = fields.Str(validate=validate.Length(max=45), nullable=False)
    class_user = fields.Integer(required=True)
    info = fields.Str(validate=validate.Length(max=45), nullable=False)

    @post_load
    def make_class(self, data,**kwargs):
        return Class(**data)


class BookSchema(Schema):
    __tablename__ = "Book"
    id = fields.Integer()
    classId = fields.Integer(required=True)
    StartDateTime = fields.DateTime()
    ENDDateTime = fields.DateTime()
    book_user = fields.Integer(required=True)

    @post_load
    def make_book(self, data,**kwargs):
        return Book(**data)
