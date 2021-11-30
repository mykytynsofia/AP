from marshmallow import ValidationError
from flask import jsonify, request, Blueprint, Response
from flask_bcrypt import Bcrypt
from demo import *
from schemas import *
from flask_httpauth import HTTPBasicAuth
session = sessionmaker(bind=engine)
s = session()
query = Blueprint("query", __name__)

b = Bcrypt()
auth = HTTPBasicAuth()

# User
User_array = [1 , 2, 3 , 4 , 5]
@auth.verify_password
def verify_password(username, password):
    id = int(username);
    if not id in User_array:
        return ({"message": "you are not login"}, 401)
    user = s.query(User).filter(User.id == id).first()
    if b.check_password_hash(user.authorization, password):
        return (id, 200)
    else:
        return ({"message": "wrong password or id"}, 401)
@query.route('/login', methods=['GET'])
def login():
    info = request.authorization
    if not info or not info.username or not info.password:
        return {"message": "mised information"} , 401
    id = int(info.username)
    password = info.password
    user = s.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "User could not be found."}, 404
    if id in User_array:
        return {"message": "already login"}, 401

    if b.check_password_hash(user.authorization, password):
        User_array.append(id)
        print(User_array)
        return {"message": "success login"}, 200
    else:
        print(User_array)
        return {"message": "wrong password or id"}, 401

@query.route('/logout', methods=['GET'])
def logout():
    info = request.authorization
    if not info or not info.username or not info.password:
        return {"message": "mised information"} , 401
    id = int(info.username)
    password = info.password
    if not id in User_array:
        return ({"message": "you are not login"}, 401)
    user = s.query(User).filter(User.id == id).first()
    if not b.check_password_hash(user.authorization, password):
        return ({"message": "wrong password or id"}, 401)
    User_array.pop(User_array.index(id))
    print(User_array)
    return ({"message": "you logout"}, 401)




@query.route('/user', methods=['POST'])
def user_create():
    print('create')
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
    print('create')
    s.add(new_user)
    s.commit()
    return {"message": "User was successfully created."}, 200


@query.route('/user/<int:id>', methods=['GET'])
@auth.login_required
def user_get(id):
    res = auth.current_user()
    print(res)
    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if res[0] != id and check_admin.properties != "Admin":
        return {"message": "You can see only your information"}, 406
    user = s.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "User could not be found."}, 404
    print(user.id != res[0],user.properties == "Admin")
    if user.id != res[0] and user.properties == "Admin":
        return {"message": "You can not see anther Admin"}, 406
    schema = UserSchema()
    return schema.dump(user), 200


@query.route('/user', methods=['GET'])
@auth.login_required
def user_get_all():
    res = auth.current_user()
    print(res)
    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if check_admin.properties != "Admin":
        return {"message": "Only Admin can do it"}, 406
    users = s.query(User).all()
    if not users:
        return {"message": "Users could not be found."}, 404
    schema = UserSchema()
    return jsonify(schema.dump(users, many=True)), 200


@query.route('/user/<int:id>', methods=['PUT'])
@auth.login_required
def user_update(id):
    data = request.json
    schema = UserSchema()
    if 'id' in data:
        return {"message": "You can not change id"}, 400
    if not data:
        return {"message": "Empty request body"}, 400
    res = auth.current_user()

    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if res[0] != id and check_admin.properties != "Admin":
        return {"message": "You can updeta only your information"}, 406
    check_id = s.query(User).filter(User.id == id).first()
    if not check_id:
        return {"message": "User with provided id does not exists"}, 400
    if check_id.id != res[0] and check_id.properties == "Admin":
        return {"message": "You can not updeta Admin"} , 406
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
@auth.login_required
def user_delete(id):
    res = auth.current_user()

    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if res[0] != id and check_admin.properties != "Admin":
        return {"message": "You can delete only your User"}, 406
    user = s.query(User).filter_by(id=id).first()
    if not user:
        return {"message": "User could not be found."}, 404
    if user.id != res[0] and user.properties == "Admin":
        return {"message": "You can not delete Admin"} ,406
    # s.query(Book).filter(Book.book_user == User.id).delete(synchronize_session="fetch")
    s.delete(user)
    s.commit()
    User_array.pop(User_array.index(id))
    return {"message": "User was successfully  deleted."}, 200


# Class
@query.route('/class', methods=['POST'])
@auth.login_required
def add_class():
    res = auth.current_user()

    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if check_admin.properties != "Admin":
        return {"message": "Only Admin can do it"}, 406
    new_class = request.json
    if not new_class:
        return {"message": "Empty request body."}, 400
    new_class['class_user'] = res[0];
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
@auth.login_required
def update_class(class_id):
    res = auth.current_user()

    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if check_admin.properties != "Admin":
        return {"message": "Only Admin can do it"}, 406
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
    if res[0] != params['class_user']:
        return {"message": "You can updeta only your class"}, 406
    user = s.query(User).filter(User.id == request.json.get('class_user')).first()
    '''if user is None:
        return {"message": "User could not be found."}, 404
    if user.properties != 'Admin':
        return {"message": "This user is not admin."}, 406'''
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
@auth.login_required
def delete_class(id):
    res = auth.current_user()

    if res[1] != 200:
        return res
    check_admin = s.query(User).filter(User.id == res[0]).first()
    if check_admin.properties != "Admin":
        return {"message": "Only Admin can do it"}, 406
    class_list = s.query(Class).filter_by(id=id).first()
    if not class_list:
        return {"message": "Class could not be found."}, 404
    # s.query(Book).filter(Book.classId == Class.id).delete(synchronize_session="fetch")
    if res[0] != class_list.class_user:
        return {"message": "You can delete only your class"}, 406
    s.delete(class_list)
    s.commit()
    return {"message": "Class and all bookings were deleted."}, 200


# Booking
@query.route('/booking', methods=['POST'])
@auth.login_required
def create_booking():
    res = auth.current_user()

    if res[1] != 200:
        return res

    data = request.json
    check_admin = s.query(User).filter(User.id == res[0]).first()
    check_user = s.query(User).filter(User.id == data['book_user']).first()
    if not check_user:
        return {"message": 'User with provided id was not found.'}, 404
    if (check_admin.properties == "Admin" and check_user.properties == "Admin" and check_user.id != res[0]) or \
            (check_user.id != res[0] and check_admin.properties != "Admin" ):
        return {"message": "wrong book_user"}, 401

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
@auth.login_required
def get_booking(id):

    booking_get = s.query(Book).filter(Book.id == id).first()
    if not booking_get:
        return {"message": "Booking could not be found."}, 404
    '''res = auth.current_user()
    if res[1] != 200:
        return res



    check_admin = s.query(User).filter(User.id == res[0]).first()
    check_user = s.query(User).filter(User.id == booking_get.book_user).first()
    if not check_user:
        return {"message": 'User with provided id was not found.'}, 404
    if check_admin.properties == "Admin" and check_user.properties == "Admin" and check_user.id != res[0]:
        return {"message": "now properties "}, 406
    if check_user.id != res[0] and check_admin.properties != "Admin":
        return {"message": "now properties "}, 406'''

    schema = BookSchema()
    return schema.dump(booking_get), 200


@query.route('/booking/<int:id>', methods=['PUT'])
@auth.login_required
def update_booking(id):
    res = auth.current_user()
    data = request.json
    if res[1] != 200:
        return res

    all_bookings = s.query(Book).filter_by(id=id).first()
    if not all_bookings:
        return {"message ": "A booking with provided ID was not found"}, 404


    if not data:
        return {"message": ":((("},404

    check_admin = s.query(User).filter(User.id == res[0]).first()
    check_user = s.query(User).filter(User.id == all_bookings.book_user).first()
    if not check_user:
        return {"message": 'User with provided id was not found.'}, 404
    if check_admin.properties == "Admin" and check_user.properties == "Admin" and check_user.id != res[0]:
        return {"message": "now properties "}, 406
    if check_user.id != res[0] and check_admin.properties != "Admin":
        return {"message": "now properties "}, 406
    check_user = s.query(User).filter(User.id == data['book_user']).first()
    if not check_user:
        return {"message": 'User with provided id was not found.'}, 404
    if check_admin.properties == "Admin" and check_user.properties == "Admin" and check_user.id != res[0]:
        return {"message": "wrong book_user"}, 401
    if check_user.id != res[0] and check_admin.properties != "Admin":
        return {"message": "wrong book_user"}, 401

    try:
        BookSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400


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
@auth.login_required
def delete_booking(id):
    res = auth.current_user()
    if res[1] != 200:
        return res

    booking = s.query(Book).filter_by(id=id).first()
    if not booking:
        return Response(status=404, response='A booking with provided ID was not found.')

    check_admin = s.query(User).filter(User.id == res[0]).first()
    check_user = s.query(User).filter(User.id == booking.book_user).first()
    if check_admin.properties == "Admin" and check_user.properties == "Admin" and check_user.id != res[0]:
        return {"message": "now properties "}, 406
    if check_user.id != res[0] and check_admin.properties != "Admin":
        return {"message": "now properties "}, 406





    s.delete(booking)
    s.commit()
    schema = BookSchema()
    return schema.dump(booking), 200
