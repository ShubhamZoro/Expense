from flask_restful import Resource, reqparse
from flask_login import login_required
from models import db, User

class UserResource(Resource):
    @login_required
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return {'email': user.email, 'name': user.name, 'mobile_number': user.mobile_number}