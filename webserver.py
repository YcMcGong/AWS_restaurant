# Python 3+
# from http.server import BaseHTTPRequestHandler, HTTPServer
# import html

# Python 2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# from HTMLParser import HTMLParser

import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Init Database
import lotsofmenus

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += "<p> Please add the restaurant name below</p>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                <h2>What is the name of the new restaurant?</h2>
                <input name="restaurant_name" type="text" placeholder = 'New Restaurant Name'>
                <input type="submit" value="Create"> </form>'''
                output += "</body></html>"
                self.wfile.write(output.encode())
                # print output
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurantIDPath = self.path.split("/")[2]
                restaurant_name = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                output = ""
                output += "<html><body>"
                output += "<h1>Please Edit the name for restaurant: %s</h1>" % restaurant_name.name
                output += "<p> Please add the restaurant name below</p>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>
                <h2>What is the name of the new restaurant?</h2>
                <input name="new_restaurant_name" type="text" placeholder = 'New Restaurant Name'>
                <input type="submit" value="Update"> </form>''' % restaurantIDPath
                output += "</body></html>"
                self.wfile.write(output.encode())
                # print output
                return

            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                <h2>What would you like me to say?</h2>
                <input name="message" type="text" >
                <input name="name" type="text" >
                <input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output.encode())
                # print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                <h2>What would you like me to say?</h2>
                <input name="message" type="text" >
                <input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output.encode())
                # print output
                return

            if self.path.endswith("/restaurants"):
                
                # Init of page
                output = ""
                output += "<b><a href='restaurants/new'> Add a new restaurant </a></b>"
                # Generate Results
                sql_result = session.query(Restaurant).all()
                sql_message = ''
                for res in sql_result:
                    sql_message += res.name + '<br/>'
                    sql_message += '<a href="/restaurants/%s/edit">Edit</a><br/>'%res.id
                    sql_message += '<a href="/restaurants/%s/delete">Delete</a><br/>'%res.id
                    sql_message += '<br/><br/><br/>'
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '<h2>List all restaurant</h2>'+sql_message
                output += "</body></html>"
                self.wfile.write(output.encode())
                # print output
                return

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
                    output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantIDPath
                    output += "<input type = 'submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        # try:
        if self.path.endswith("/restaurants/new"):
            ctype, pdict = cgi.parse_header(
                self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('restaurant_name')

                # DB
                new_restaurant = Restaurant(name=messagecontent[0])
                session.add(new_restaurant)
                session.commit()

                # Refresh the restaurant page
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        if self.path.endswith("/edit"):
            
            # Find the name of the restaurant being edit
            restaurantIDPath = self.path.split("/")[2]
            ctype, pdict = cgi.parse_header(
                self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('new_restaurant_name')

                # DB
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    myRestaurantQuery.name = messagecontent[0]
                    session.add(myRestaurantQuery)
                    session.commit()

                    # Refresh the restaurant page
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        if self.path.endswith("/delete"):
            
            # Find the name of the restaurant being edit
            restaurantIDPath = self.path.split("/")[2]
            
            # DB
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery != []:
                session.delete(myRestaurantQuery)
                session.commit()

                # Refresh the restaurant page
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        # except:
        #     print('nothing')
        #     pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print ("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()