from app.extensions import ma
from app.models import Book


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        # load_instance = True


book_schema = BookSchema()
books_schema = BookSchema(many=True)
