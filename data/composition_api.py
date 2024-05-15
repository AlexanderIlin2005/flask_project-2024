import flask
from flask import jsonify
from sqlalchemy import func, cast
from sqlalchemy.sql.operators import or_
from sqlalchemy.testing import db

from . import db_session
from .compositions import MainTable

blueprint = flask.Blueprint('composition_api', __name__, template_folder='templates')

@blueprint.route('/api/compositions')
def get_all_compositions():
    db_sess = db_session.create_session()
    composition = db_sess.query(MainTable).all()
    l1 = []
    for item in composition:
        l1.append(item.to_dict(only=('Name', 'Author')))
    return jsonify(
        {
            'compositions': l1
        }
    )


@blueprint.route('/api/<name>')
def get_one_composition(request):
    db_sess = db_session.create_session()
    #composition = db_sess.query(MainTable).filter(MainTable.Name == name).one()
    #composition = db_sess.query(MainTable).filter(
    #    any([column.like('%' + request + '%') for column in MainTable.__table__.columns])
    #).all()

    composition = db_sess.query(MainTable).filter(
        any([func.lower(column).like('%' + request.lower() + '%') for column in MainTable.table.columns])).all()



    return jsonify(
        {
            'composition': composition.to_dict()
        }
    )
