from marshmallow import ValidationError
from flask import jsonify, request, Blueprint, Response
from flask_bcrypt import Bcrypt
from demo import *
from schemas import *

session = sessionmaker(bind=engine)
s = session()
query = Blueprint("query", __name__)

b = Bcrypt()


# User
@query.route('/user', methods=['POST'])
def user_create():
    data = request.json
    if not data:
        return {"message": "Empty request body."}, 400
    if 'properties' not in data:
        return {"message": "You should set a correct property."}, 400
    try:
        UserSchema().load(data)
    except ValidationError as err:
        return err.messages, 422
    user_check_id = s.query(User).filter(User.id == request.json.get('id')).first()
    if user_check_id is not None:
        return {"message": "User with provided id already exists."}, 406
    hashed_password = b.generate_password_hash(data['authorization'])
    new_user = User(id=data['id'], Firstname=data['Firstname'], Lastname=data['Lastname'],
                    properties=data['properties'], authorization=hashed_password)
    s.add(new_user)
    s.commit()
    return {"message": "User was successfully created."}, 200


@query.route('/user/<int:id>', methods=['GET'])
def user_get(id):
    user = s.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "User could not be found."}, 404
    schema = UserSchema()
    return schema.dump(user), 200


@query.route('/user', methods=['GET'])
def user_get_all():
    users = s.query(User).all()
    if not users:
        return {"message": "Users could not be found."}, 404
    schema = UserSchema()
    return jsonify(schema.dump(users, many=True)), 200


@query.route('/user/<int:id>', methods=['PUT'])
def user_update(id):
    data = request.json
    schema = UserSchema()
    if 'id' in data:
        return {"message": "You can not change id"}, 400
    if not data:
        return {"message": "Empty request body"}, 400
    check_id = s.query(User).filter(User.id == id).first()
    if not check_id:
        return {"message": "User with provided id does not exists"}, 400
    try:
        schema.load(data)
    except ValidationError as err:
        return err.messages, 400
    for key, value in data.items():
        if key == 'authorization':
            value = Bcrypt().generate_password_hash(value).decode('utf - 8')
        setattr(check_id, key, value)
    s.commit()
    return {"message": "User was successfully updated. "}, 200


@query.route('/user/<int:id>', methods=['DELETE'])
def user_delete(id):
    user = s.query(User).filter_by(id=id).first()
    if not user:
        return {"message": "User could not be found."}, 404
    # s.query(Book).filter(Book.book_user == User.id).delete(synchronize_session="fetch")
    s.delete(user)
    s.commit()
    return {"message": "User was successfully  deleted."}, 200


# Class
@query.route('/class', methods=['POST'])
def add_class():
    new_class = request.json
    if not new_class:
        return {"message": "Empty request body."}, 400
    try:
        res = ClassSchema().load(new_class)
    except ValidationError as err:
        return err.messages, 422
    user_admin = s.query(User).filter(User.id == request.json.get('class_user')).first()
    if user_admin is None:
        return {"message": "User could not be found."}, 404
    if user_admin.properties != 'Admin':
        return {"message": "This user is not an Admin."}, 406
    check_id = s.query(Class).filter(Class.id == request.json.get('id')).first()
    if check_id is not None and request.json.get('id') != id:
        return {"message": "Class with provided id already exists"}, 406
    s.add(res)
    s.commit()
    return {"message": "Class was successfully created. "}, 200


@query.route('/class', methods=['GET'])
def get_classes():
    class_find = s.query(Class).all()
    if not class_find:
        return {"message": "Classes could not be found."}, 404
    schema = ClassSchema()
    return jsonify(schema.dump(class_find, many=True)), 200


@query.route('/class/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    class_update = s.query(Class).filter(Class.id == class_id).first()
    if class_update is None:
        return {"message": "Class with provided id could not be found."}, 404
    params = request.json
    if not params:
        return {"message": "Empty request body."}, 400
    if 'id' in params:
        return {"message": "You can not change id"}, 400
    schema = ClassSchema()
    try:
        data = schema.load(params)
    except ValidationError as err:
        return err.messages, 422
    user = s.query(User).filter(User.id == request.json.get('class_user')).first()
    if user is None:
        return {"message": "User could not be found."}, 404
    if user.properties != 'Admin':
        return {"message": "This user is not admin."}, 406
    for key, value in params.items():
        setattr(class_update, key, value)
    s.commit()
    return {"message": "Class was successfully updated. "}, 200


@query.route('/class/<int:id>', methods=['GET'])
def get_class(id):
    class_get = s.query(Class).filter(Class.id == id).first()
    if not class_get:
        return {"message": "Class could not be found."}, 404
    schema = ClassSchema()
    return schema.dump(class_get), 200


@query.route('/class/<int:id>', methods=['DELETE'])
def delete_class(id):
    class_list = s.query(Class).filter_by(id=id).first()
    if not class_list:
        return {"message": "Class could not be found."}, 404
    # s.query(Book).filter(Book.classId == Class.id).delete(synchronize_session="fetch")
    s.delete(class_list)
    s.commit()
    return {"message": "Class and all bookings were deleted."}, 200


# Booking
@query.route('/booking', methods=['POST'])
def create_booking():
    data = request.json
    try:
        BookSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    check_book = s.query(Book).filter(Book.id == request.json.get('id')).first()
    if check_book is not None and request.json.get('id') != id:
        return {"message": "Book with provided id already exists"}, 406
    check_user = s.query(User).filter(User.id == request.json.get('book_user')).first()
    if not check_user:
        return {"message": 'User with provided id was not found.'}, 404
    check_class = s.query(Class).filter(Class.id == request.json.get('classId')).first()
    if not check_class:
        return {"message": "Class with provided id was not found."}, 404

    if datetime.strptime(data['StartDateTime'], '%Y-%m-%d %H:%M:%S') > datetime.strptime(data['ENDDateTime'],
                                                                                         '%Y-%m-%d %H:%M:%S'):
        return {"message": "Invalid data input. "}
    dfrom = datetime.strptime(data['StartDateTime'], '%Y-%m-%d %H:%M:%S')
    dto = datetime.strptime(data['ENDDateTime'], '%Y-%m-%d %H:%M:%S')
    time = dto - dfrom
    totsec = time.total_seconds()
    h = totsec // 3600
    if h < 1 or time.days > 5:
        return {"message": "Class cannot be reserved for that period of time."}, 400
    all_booked = s.query(Book).filter_by(classId=data['classId'])
    for k in all_booked:
        if k.StartDateTime <= dfrom <= k.ENDDateTime:
            return {"message": "Class is already reserved for this time."}, 400
            break
        if k.StartDateTime <= dto <= k.ENDDateTime:
            return {"message": "Class is already reserved for this time."}, 400
            break

        if dfrom <= k.StartDateTime and dto >= k.ENDDateTime:
            return {"message": "Class is already reserved for this time."}, 400
            break
    schema = BookSchema()
    s.add(schema.load(data))
    s.commit()
    return {"message": "New booking was successfully created. "}, 200


@query.route('/booking', methods=['GET'])
def get_bookings():
    booking_find = s.query(Book).all()
    if not booking_find:
        return {"message": "Bookings could not be found."}, 404
    schema = BookSchema()
    return jsonify(schema.dump(booking_find, many=True)), 200


@query.route('/booking/<int:id>', methods=['GET'])
def get_booking(id):
    booking_get = s.query(Book).filter(Book.id == id).first()
    if not booking_get:
        return {"message": "Booking could not be found."}, 404
    schema = BookSchema()
    return schema.dump(booking_get), 200


@query.route('/booking/<int:id>', methods=['PUT'])
def update_booking(id):
    data = request.json
    try:
        BookSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    all_bookings = s.query(Book).filter_by(id=id).first()
    if not all_bookings:
        return {"message ": "A booking with provided ID was not found"}, 404

    if 'StartDateTime' in data.keys():
        d1 = datetime.strptime(data['StartDateTime'], '%Y-%m-%d %H:%M:%S')
    else:
        d1 = all_bookings.StartTimeDate
    if 'ENDDateTime' in data.keys():
        d2 = datetime.strptime(data['ENDDateTime'], '%Y-%m-%d %H:%M:%S')
    else:
        d2 = all_bookings.ENDDateTime
    if 'StartDateTime' in data.keys() or 'ENDDateTime' in data.keys() or 'classId' in data.keys():
        if d1 > d2:
            return {"message": "Invalid dates input."}, 400

        diff = d2 - d1
        if (diff.total_seconds() / 3600) < 1 or diff.days > 5:
            return {"message": "Class cannot be reserved for that period of time."}, 400

        if 'classId' in data.keys():
            class_find = s.query(Class).filter_by(id=data['classId']).first()
        else:
            class_find = s.query(Class).filter_by(id=all_bookings.classId).first()

        bookings = s.query(Book).filter_by(classId=class_find.id)

        for k in bookings:
            if k.StartDateTime <= d1 <= k.ENDDateTime:
                return {"message": "Class is already reserved for this time."}, 400
                break
            if k.StartDateTime <= d2 <= k.ENDDateTime:
                return {"message": "Class is already reserved for this time."}, 400
                break

            if d1 <= k.StartDateTime and d2 >= k.ENDDateTime:
                return {"message": "Class is already reserved for this time."}, 400
                break

    for key, value in data.items():
        setattr(all_bookings, key, value)
    s.commit()
    s.commit()
    final = s.query(Book).filter_by(id=id).first()
    serialized_booking = BookSchema().dump(final)
    return jsonify(serialized_booking)


@query.route('/booking/<int:id>', methods=['DELETE'])
def delete_booking(id):
    booking = s.query(Book).filter_by(id=id).first()
    if not booking:
        return Response(status=404, response='A booking with provided ID was not found.')
    s.delete(booking)
    s.commit()
    schema = BookSchema()
    return schema.dump(booking), 200
##
