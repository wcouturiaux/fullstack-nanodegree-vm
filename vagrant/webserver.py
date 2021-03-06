import cgi

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

## import CRUD Ops from Lesson 1 ##
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#create session and connect to database
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:

			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body><a href='restaurants/new'>Make a New Restaurant</a></br></br>"
				for restaurant in restaurants:
					output += restaurant.name
					output += "</br>"
					output += "<a href='/resturants/%s/edit'>Edit</a>" % restaurant.id
					output += "&nbsp &nbsp <a href=/restaurants/%s/delete>Delete</a></br></br>" %restaurant.id

				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1>Create a New Restaurant</h1></br></br>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>\
							<input name='newRestaurantName' type='text'>&nbsp<input type='submit' value='Submit'></form>"

				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>Hello!</body></html>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?\
							</h2><input name="message" type="text"><input type="submit" value="Submit"> </form>'''
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>Hola! <a href='/hello'>Back to Hello</>\
				</body></html>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/edit"):
				restaurantIdPath = self.path.split("/")[2]
				restaurantToEdit = session.query(Restaurant).filter_by(id=restaurantIdPath).one()
				if restaurantToEdit != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>Rename %s </h1> </br></br>" %restaurantToEdit.name
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>\
								<input name='renamedRestaurant' type='text'>&nbsp<input type='submit' value='Submit'></form>"\
								% restaurantIdPath

					output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/delete"):
				restaurantIdPath = self.path.split("/")[2]
				restaurantToEdit = session.query(Restaurant).filter_by(id=restaurantIdPath).one()
				if restaurantToEdit != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>Delete %s ?</h1> </br></br>" %restaurantToEdit.name
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>\
								<input type='submit' value='Delete'></form>" % restaurantIdPath

					output += "</body></html>"
				self.wfile.write(output)
				return


		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)


	def do_POST(self):
		try:

			if self.path.endswith("/delete"):
					restaurantIdPath = self.path.split("/")[2]
					restaurantToEdit = session.query(Restaurant).filter_by(id=restaurantIdPath).one()

					if restaurantToEdit != []:
						session.delete(restaurantToEdit)
						session.commit()

						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('renamedRestaurant')
					restaurantIdPath = self.path.split("/")[2]
					restaurantToEdit = session.query(Restaurant).filter_by(id=restaurantIdPath).one()

					if restaurantToEdit != []:
						restaurantToEdit.name = messagecontent[0]
						session.add(restaurantToEdit)
						session.commit()

						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')

					newRestaurant = Restaurant(name=messagecontent[0])
					session.add(newRestaurant)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			# ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			# if ctype == 'multipart/form-data':
			# 	fields = cgi.parse_multipart(self.rfile, pdict)
			# 	messagecontent = fields.get('message')
			# output = ""
			# output += "<html><body>"
			# output += "<h2>Okay, how about this: </h2>"
			# output += "<h1> %s </h1>" % messagecontent[0]

			# self.send_header('Content-type', 'text/html')
			# output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
			# output += "</body></html>"
			# self.wfile.write(output)
			# print output
			# return

		except:
			pass
def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()


	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()


if __name__ == '__main__':
	main()













