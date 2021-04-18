from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from random import choice

API_KEY = "TopSecretAPIKey"

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        new_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return new_dict


def find_all_cafes():
    cafes = Cafe.query.all()

    cafe_list = []
    for cafe in cafes:
        cafe_list.append(cafe.to_dict())

    return cafe_list


@app.route("/")
def home():
    return render_template('index.html')
    # return redirect(url_for('all_cafes'))


# HTTP GET - Read Record
@app.route('/random')
def random():
    cafes = Cafe.query.all()
    cafe = choice(cafes)

    return jsonify(cafe.to_dict())


@app.route("/all")
def all_cafes():
    return jsonify(find_all_cafes())


@app.route("/search")
def search():
    location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=location).all()

    if cafes:
        return jsonify([cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price"),
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch(cafe_id):
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    if cafe:
        cafe.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify({'success': 'Successfully updated the price'}), 200

    else:
        return jsonify(error={'Not Found': 'Sorry a cafe with that id was not found in the database'}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    print(request.method)

    if request.headers.get("api-key") == API_KEY:

        cafe = Cafe.query.filter_by(id=cafe_id).first()

        if cafe:
            db.session.delete(cafe)
            db.session.commit()

            return jsonify({"success": "The cafe with that id has been removed"}), 200
        else:
            return jsonify(error={'Not Found': 'Sorry a cafe with that id was not found in the database'}), 404

    return jsonify(error={'Unauthorized': 'Please provide the correct API Key'}), 401


if __name__ == '__main__':
    app.run(debug=True)
