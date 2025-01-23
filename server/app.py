from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class ClearSession(Resource):
    def get(self):
        session.clear()
        return {}, 204


class Login(Resource):
    def post(self):
        try:
            # Get the username from the request body
            username = request.json.get('username')
            if not username:
                return {'error': 'Username is required'}, 400

            # Find the user by username
            user = User.query.filter_by(username=username).first()
            if user:
                # Store user_id in the session
                session['user_id'] = user.id
                return {'id': user.id, 'username': user.username}, 200

            return {'error': 'Invalid username'}, 401
        except Exception as e:
            return {'error': str(e)}, 500


class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {}, 401

        # Use db.session.get() to fetch the user by ID
        user = db.session.get(User, user_id)
        if user:
            return {'id': user.id, 'username': user.username}, 200

        return {}, 401



api.add_resource(ClearSession, '/clear')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
