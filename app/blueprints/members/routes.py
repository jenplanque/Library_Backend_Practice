# app/blueprints/user/routes
from .schemas import member_schema, members_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Member
from . import members_bp

# from app.blueprints.member import member_bp
# from app.models import Member
# from app.extensions import limiter
# from .schemas import member_schema, members_schema


# ADD MEMBER AND GET ALL MEMBERS
@members_bp.route("/", methods=["POST", "GET"])
# @limiter.limit("3 per hour")  # A client can only attempt to make 3 members per hour
def create_member():
    if request.method == "POST":
        try:
            member_data = member_schema.load(request.json)

        except ValidationError as e:
            return jsonify(e.messages), 400

        query = select(Member).where(Member.email == member_data["email"])
        existing_member = db.session.execute(query).scalars().all()
        if existing_member:
            return jsonify({"error": "Email already exists"}), 400

        new_member = Member(**member_data)  # Unpack the JSON data into the Member model
        db.session.add(new_member)
        db.session.commit()
        return member_schema.jsonify(new_member), 201

    elif request.method == "GET":
        query = select(Member)
        members = db.session.execute(query).scalars().all()

        return members_schema.jsonify(members), 200

    # try:
    #     # Deserialize and validate input data
    #     member_data = member_schema.load(request.json)
    # except ValidationError as e:
    #     return jsonify(e.messages), 400

    # use data to create an instance of Member
    # new_member = Member(
    #     name=member_data["name"],
    #     email=member_data["email"],
    #     password=member_data["password"],
    # )


# GET SPECIFIC MEMBER
@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = db.session.get(Member, member_id)

    if member:
        return member_schema.jsonify(member), 200
    return jsonify({"error": "Member not found"}), 404


# UPDATE MEMBER
@members_bp.route("/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found"}), 404

    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new email, verify does not already exist in DB
    if member_data.get("email") != member.email:
        query = select(Member).where(Member.email == member_data["email"])
        existing_member = db.session.execute(query).scalars().first()
        if existing_member:
            return jsonify({"error": "Email already exists"}), 400

    for key, value in member_data.items():
        setattr(member, key, value)

    db.session.commit()
    return member_schema.jsonify(member), 200


# DELETE MEMBER
@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found"}), 404

    db.session.delete(member)
    db.session.commit()
    return (
        jsonify({"message": f"Member id: {member_id} deleted successfully"}),
        200,
    )
