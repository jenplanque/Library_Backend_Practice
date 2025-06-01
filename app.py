from datetime import date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy import select

# from marshmallow import Marshmallow


app = Flask(__name__)

# sets the DB URI to use a SQLite database named users.db.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"


# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     "mysql+mysqlconnector://root:MYPASSWORD@localhost/library_db"
# )


# Create a base class for our models
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
ma = Marshmallow()

db.init_app(app)  # adding our db extension to our app
ma.init_app(app)  # adding our marshmallow extension to our app

loan_book = db.Table(
    "loan_book",
    Base.metadata,
    db.Column("loan_id", db.ForeignKey("loans.id")),
    db.Column("book_id", db.ForeignKey("books.id")),
)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    DOB: Mapped[date]
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = db.relationship(
        back_populates="member"
    )  # New relationship attribute


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date] = mapped_column(db.Date)
    member_id: Mapped[int] = mapped_column(db.ForeignKey("members.id"))

    member: Mapped["Member"] = db.relationship(
        back_populates="loans"
    )  # New relationship attribute
    books: Mapped[List["Book"]] = db.relationship(
        secondary=loan_book, back_populates="loans"
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(255), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = db.relationship(
        secondary=loan_book, back_populates="books"
    )


# ------SCHEMAS------


class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member  # using the SQLAlchemy model to create fields used in serialization, deserialization, and validation


member_schema = MemberSchema()
members_schema = MemberSchema(
    many=True
)  # variant that allows for the serialization of many Members


# _____ROUTES_____
# specific routes using the Flask app instance


# CREATE MEMBER
@app.route("/members", methods=["POST"])
def create_member():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400  # Return validation errors if any

    query = select(Member).where(
        Member.email == member_data["email"]
    )  # checking DB for existing email
    existing_member = db.session.execute(query).scalars().all()
    if existing_member:
        return jsonify({"error": "Email already exists"}), 400

    new_member = Member(**member_data)  # Unpack the JSON data into the Member model
    db.session.add(new_member)
    db.session.commit()
    return member_schema.jsonify(new_member), 201


# GET ALL MEMBERS
@app.route("/members", methods=["GET"])
def get_members():
    query = select(Member)
    members = db.session.execute(query).scalars().all()

    return members_schema.jsonify(members)


# GET SPECIFIC MEMBER
@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = db.session.get(Member, member_id)

    if member:
        return member_schema.jsonify(member), 200
    return jsonify({"error": "Member not found."}), 404


@app.route("/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 400

    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check if the email is being changed and if the new email already exists
    new_email = member_data.get("email")
    if new_email != member.email:
        query = select(Member).where(Member.email == new_email)
        existing_member = db.session.execute(query).scalars().first()
        if existing_member:
            return jsonify({"error": "Email already exists"}), 400

    for key, value in member_data.items():
        setattr(member, key, value)

    db.session.commit()
    return member_schema.jsonify(member), 200


# DELETE SPECIFIC MEMBER
@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 400

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": f"Member id: {member_id}, successfully deleted."}), 200


# Create the database tables
with app.app_context():
    db.create_all()


app.run()
