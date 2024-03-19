from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mysql.connector
from mysql.connector import Error


def connect():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='stock',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


def add_product(connection, product_name, description, category, unit_price, quantity, attributes=None):
    try:
        cursor = connection.cursor()
        query = ("INSERT INTO products (product_name, description, category, unit_price, quantity) VALUES (%s, %s, %s, "
                 "%s, %s)")
        data = (product_name, description, category, unit_price, quantity)
        cursor.execute(query, data)
        product_id = cursor.lastrowid
        if attributes:
            for attr_name, attr_value in attributes.items():
                add_product_attribute(connection, product_id, attr_name, attr_value)

        connection.commit()
        print("Product added successfully")
        return True
    except Error as e:
        print("Error while adding product to MySQL", e)
        return False


def add_product_attribute(connection, product_id, attribute_name, attribute_value):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO product_attributes (product_id, attribute_name, attribute_value) VALUES (%s, %s, %s)"
        data = (product_id, attribute_name, attribute_value)
        cursor.execute(query, data)
        connection.commit()
        print("Attribute added successfully")
    except Error as e:
        print("Error while adding attribute to MySQL", e)


def update_product(connection, product_id, product_name, description, category, unit_price, quantity):
    try:
        cursor = connection.cursor()
        query = ("UPDATE products SET product_name = %s, description = %s, category = %s, unit_price = %s, quantity = "
                 "%s WHERE product_id = %s")
        data = (product_name, description, category, unit_price, quantity, product_id)
        cursor.execute(query, data)
        connection.commit()
        print("Product updated successfully")
        return True
    except Error as e:
        print("Error while updating product in MySQL", e)
        return False


def fetch_categories(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT category_id, category_name FROM categories")
        categories = cursor.fetchall()
        category_list = [{"category_id": category[0], "category_name": category[1]} for category in categories]
        return category_list
    except Error as e:
        print("Error while fetching categories from MySQL", e)
        return []


def delete_product(connection, product_id):
    try:
        cursor = connection.cursor()
        query = "DELETE FROM products WHERE product_id = %s"
        data = (product_id,)
        cursor.execute(query, data)
        connection.commit()
        print("Product deleted successfully")
        return True
    except Error as e:
        print("Error while deleting product from MySQL", e)
        return False


def track_inventory(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT product_id, product_name, quantity FROM products"
        cursor.execute(query)
        inventory = cursor.fetchall()
        print("Current Inventory:")
        inventory_list = []
        for product in inventory:
            inventory_list.append({"product_id": product[0], "product_name": product[1], "quantity": product[2]})
            print(f"Product ID: {product[0]}, Product Name: {product[1]}, Quantity: {product[2]}")
        return inventory_list
    except Error as e:
        print("Error while tracking inventory in MySQL", e)
        return []


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Convert POST data to dictionary
        data = json.loads(post_data)

        if self.path == '/add_product':
            success = add_product(self.connection, **data)
            if success:
                self.send_response(200)
            else:
                self.send_response(500)
            self.end_headers()

        elif self.path == '/update_product':
            success = update_product(self.connection, **data)
            if success:
                self.send_response(200)
            else:
                self.send_response(500)
            self.end_headers()

        elif self.path == '/delete_product':
            success = delete_product(self.connection, data['product_id'])
            if success:
                self.send_response(200)
            else:
                self.send_response(500)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/fetch_categories':
            categories = fetch_categories(self.connection)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(categories).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')


def main():
    # connection = None
    httpd = None
    try:
        connection = connect()
        if not connection:
            return

        # Specify the server port
        port = 8000

        server_address = ('', port)
        httpd = HTTPServer(server_address, RequestHandler)
        print(f'Starting server on port {port}...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the server')
        httpd.socket.close()
    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    main()
