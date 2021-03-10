"""
This is the air module and supports all the REST actions for the
air data

We do not check for duplicate entries, or support modifying entries,
as that is not applicable to air data.

We might need to support deleting entries for clean-up of old data purposes,
but we do not support it for now.
"""

from flask import make_response, abort
from config import db
from models import Air, AirSchema


def read_all():
    """
    This function responds to a request for /api/air
    with the complete lists of air

    :return:        json string of list of air
    """
    # Create the list of air from our data
    air = Air.query.order_by(Air.timestamp).all()

    # Serialize the data for the response
    air_schema = AirSchema(many=True)
    data = air_schema.dump(air).data
    return data, 200


def read_by_zipcode(zipcode):
    """
    This function responds to a request for /api/air/{zipcode}
    with all matching air entries from Air

    :param zipcode:   zipcode of air to find
    :return:          all air entries matching the zipcode
    """
    # Get the person requested
    air = Air.query.filter(Air.zipcode == zipcode).all()

    # Did we find a person?
    if air is not None:

        # Serialize the data for the response
        air_schema = AirSchema()
        data = air_schema.dump(air).data
        return data, 200

    # Otherwise, nope, didn't find air in that zipcode
    else:
        abort(
            404,
            "Air not found for zipcode: {zipcode}".format(zipcode=zipcode),
        )

def read_zipcodes():
    """
    This function responds to a request for /api/air
    with the complete list of zipcodes

    :return:        json string of list of zipcodes
    """
    '''
    # Create the list of air from our data
    zipcodes = Air.query(Air.zipcode).distinct()
    print ("\n\n {} \n\n".format(zipcodes))

    # Serialize the data for the response
    air_schema = AirSchema(many=True)
    data = air_schema.dump(air).data
    '''
    return data, 200


def create(air):
    """
    This function creates a new air entry in the Air structure
    based on the passed in air data

    :param air:  air entry to create in Air structure
    :return:        201 on success
    """
    # Create an air instance using the schema and the passed in air
    schema = AirSchema()
    new_air = schema.load(air, session=db.session).data
    print ("SSSSSSS")
    print (type(new_air))
    print (new_air)
    print ("SSSSSSS")

    # Add the air instance to the database
    db.session.add(new_air)
    db.session.commit()

    # Serialize and return the newly created air instance in the response
    data = schema.dump(new_air).data

    return data, 201


'''
def read_one(person_id):
    """
    This function responds to a request for /api/people/{person_id}
    with one matching person from people

    :param person_id:   Id of person to find
    :return:            person matching id
    """
    # Get the person requested
    person = Person.query.filter(Person.person_id == person_id).one_or_none()

    # Did we find a person?
    if person is not None:

        # Serialize the data for the response
        person_schema = PersonSchema()
        data = person_schema.dump(person).data
        return data

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Person not found for Id: {person_id}".format(person_id=person_id),
        )

def create(air):
    """
    This function creates a new air entry in the Air structure
    based on the passed in air data

    :param air:  air entry to create in Air structure
    :return:        201 on success
    """
    # Create an air instance using the schema and the passed in air
    schema = AirSchema()
    new_air = schema.load(air, session=db.session).data

    # Add the air instance to the database
    db.session.add(new_air)
    db.session.commit()

    # Serialize and return the newly created air instance in the response
    data = schema.dump(new_air).data

    return data, 201


'''
