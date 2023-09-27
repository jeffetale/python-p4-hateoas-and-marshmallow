#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

ma = Marshmallow(app)

class NewsletterSchema(ma.SQLAlchemySchema):
    
    class Meta:
        model = Newsletter

    title = ma.auto_field()
    published_at = ma.auto_field()
    body = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "newsletterbyid",
                values = dict(id='<id>')),
        }
    )

newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many = True)

class Index(Resource):

    def get(self):
        
        newsletter_schema = {
            "index": "Welcome to the Newsletter RESTful API",
        }
        
        response = make_response(
            newsletter_schema,
            200,
        )

        return response

api.add_resource(Index, '/')

class Newsletters(Resource):

    def get(self):
        
        newsletters = Newsletter.query.all()

        response = make_response(
            newsletter_schema.dump(newsletters),
            200,
        )

        return response

    def post(self):
        
        new_newsletter = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )

        db.session.add(new_newsletter)
        db.session.commit()

        response = make_response(
            newsletter_schema.dump(new_newsletter),
            201,
        )

        return response

api.add_resource(Newsletters, '/newsletters')

class NewsletterByID(Resource):

    def get(self, id):

        newsletter = Newsletter.query.filter_by(id=id).first()

        response = make_response(
            newsletter_schema.dump(newsletter),
            200,
        )

        return response

    def patch(self, id):

        newsletter = Newsletter.query.filter_by(id=id).first()
        for attr in request.form:
            setattr(newsletter, attr, request.form[attr])

        db.session.add(newsletter)
        db.session.commit()

        response = make_response(
            newsletter_schema,
            200
        )

        return response

    def delete(self, id):

        newsletter = Newsletter.query.filter_by(id=id).first()
        
        db.session.delete(newsletter)
        db.session.commit()

        response_dict = {"message": "newsletter successfully deleted"}

        response = make_response(
            jsonify(response_dict),
            200
        )

        return response

api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)