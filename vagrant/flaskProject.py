from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Restaurant, MenuItem
import pdb

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html',restaurants=restaurants)

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	#pdb.set_trace()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant=restaurant, items = items)


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], restaurant_id=
			restaurant_id)
		session.add(newItem)
		session.commit
		flash("New menu item created!")
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method =='POST':
		session.delete(itemToDelete)
		session.commit()
		flash(itemToDelete.name +" has been deleted!")
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('deleteMenuItem.html', item = itemToDelete)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id,menu_id):
	editedItem = session.query(MenuItem).filter_by(id = menu_id).one()

	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
			session.add(editedItem)
			session.commit()
			flash(editedItem.name + " has been edited")
			return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('editMenuItem.html', restaurant_id=restaurant_id,
			menu_id=menu_id, i=editedItem)

@app.route('/restaurants/JSON')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[i.serialize for i in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id,menu_id):
	item = session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItem = item.serialize)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)