# Python3.13
# views.py

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import current_user, login_required
from unicodedata import category

from .models import Note, Item
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return render_template("landing.html", user=current_user)
    if request.method == 'POST':
        note = request.form.get('note') #Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)  # providing the schema for the note
            db.session.add(new_note) # adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template("home.html", user=current_user, items=items)

@views.route('/post-product', methods=['GET', 'POST'])
@login_required
def post_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        category_id = request.form.get('category_id') # optional

        new_item = Item(
            title=title,
            description=description,
            price=float(price),
            image_url=image_url,
            seller=current_user,
            category_id=category_id
        )

        db.session.add(new_item)
        db.session.commit()

        flash('Product was successfully posted! Upload a new one or keep searching', category='success')
        return redirect(url_for('views.home'))

    return render_template("post_product.html", user=current_user)


""" # Let's not call it yet as I have not downloaded js.
@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
"""