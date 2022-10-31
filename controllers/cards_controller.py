from flask import Blueprint, request
from datetime import date
import flask_jwt_extended
from init import db
from models.card import Card, CardSchema
from models.comment import Comment, CommentSchema
from flask_jwt_extended import get_jwt_identity, jwt_required
from controllers.auth_controller import authorize

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

# ======================================get all cards==================================
 
@cards_bp.route('/')
# @jwt_required()
def get_all_cards():

    # if not authorize():
    #     return {'Error': 'You must be an admin'}, 401
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)

# ======================================get a single cards==================================
 
@cards_bp.route('/<int:card_id>/')
# @jwt_required()
def get_one_card(card_id):
    # create a statement to query the database with
    #find card where id = card_id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)

    if card:
        return CardSchema().dump(card)
    else:
        return {'error': f'Card id {card_id} not found'}

# ======================================UPDATE a single cards==================================
 
@cards_bp.route('/<int:card_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_one_card(card_id):
    # create a statement to query the database with
    #find card where id = card_id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)

    #if the card is found change the attributes that are entered in tje JSON body
    if card:
        card.title = request.json.get('title') or card.title
        card.description = request.json.get('description') or card.description
        card.status = request.json.get('status') or card.status
        card.priority = request.json.get('priority') or card.priority

        #commit changes to the cards to the DB
        db.session.commit()

        #return the updated card
        return CardSchema().dump(card)
    else:
        return {'error': f'Card id {card_id} not found'}

# ======================================creating a single cards==================================

@cards_bp.route('/', methods=['POST'])
@jwt_required()
def create_one_card():
    # Create a new Card model instance from the user_info
    card = Card(
        title = request.json['title'],
        description = request.json['description'],
        date = date.today(),
        status = request.json['status'],
        priority = request.json['priority'],
        user_id = get_jwt_identity()
    )

    # Add and commit card to DB
    db.session.add(card)
    db.session.commit()

    # Respond to client
    return CardSchema().dump(card), 201


# ======================================DELETE a single cards==================================
 
@cards_bp.route('/<int:card_id>/', methods=['DELETE'])
@jwt_required()
def delete_one_card(card_id):
    #call function to validate whether user is an admin
    authorize()

    # create a statement to query the database with
    #find card where id = card_id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)

    if card:
        db.session.delete(card)
        db.session.commit()
        return {'msg': f'Card {card_id} was successfully deleted'}, 200
    else:
        return {'error': f'Card {card_id} was not found'}, 404


# ======================================creating a single comment==================================

@cards_bp.route('/<int:card_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(card_id):
    # create a statement to query the database with
    #find card where id = card_id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)

    if card:
        # Create a new Card model instance from the user_info
        comment = Comment (
            message = request.json['message'],
            user_id = get_jwt_identity(),
            card = card,
            date = date.today()
        )

        # Add and commit card to DB
        db.session.add(comment)
        db.session.commit()

        # Respond to client
        return CommentSchema().dump(comment), 201
    else:
        return {'error': f'Card id {card_id} not found'}
    
    
    