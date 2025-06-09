# app/blueprints/user/routes
from .schemas import member_schema, members_schema
from flask import request, jsonify
from app.blueprints.member import member_bp
from app.models import Member
from app.extensions import limiter
from .schemas import member_schema, members_schema
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Member
from . import members_bp


@member_bp.route("/members", methods=["POST"])
@limiter.limit("3 per hour")  # A client can only attempt to make 3 members per hour
def create_member():
    try:
        # Deserialize and validate input data
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # use data to create an instance of Member
    new_member = Member(
        name=member_data["name"], email=member_data["email"], password=member_data["password"]
    )

    # save new_member to the database
    db.session.add(new_member)
    db.session.commit()

    # Use schema to return the serialized data of the created member
    return member_schema.jsonify(new_member), 201


#  ---

# ADD CUSTOMER and GET ALL CUSTOMERS
@customers_bp.route("/", methods=["POST", "GET"])
def customers():
    if request.method == "POST":
        try:
            customer_data = customer_schema.load(request.json)

        except ValidationError as e:
            return jsonify(e.messages), 400

        query = select(Customer).where(Customer.email == customer_data["email"])
        existing_customer = db.session.execute(query).scalars().all()
        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

        new_customer = Customer(**customer_data)
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201

    elif request.method == "GET":
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()

        return customers_schema.jsonify(customers), 200


# GET SPECIFIC CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


# UPDATE CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new email, verify does not already exist in DB
    if customer_data.get("email") != customer.email:
        query = select(Customer).where(Customer.email == customer_data["email"])
        existing_customer = db.session.execute(query).scalars().first()
        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# DELETE CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return (
        jsonify({"message": f"Customer id: {customer_id} deleted successfully."}),
        200,
    )
