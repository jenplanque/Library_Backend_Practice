from app.extensions import ma
from app.models import Loan


class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loan
        # load_instance = True


loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
