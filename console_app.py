from datetime import date

import mysql.connector
from mysql.connector import Error


# Function to establish database connection
def connect_to_database():
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


# Function to add a product to the database
def add_product(connection, product_name, description, category, unit_price, quantity):
    try:
        cursor = connection.cursor()
        query = ("INSERT INTO products (product_name, description, category, unit_price, quantity) "
                 "VALUES (%s, %s, %s, %s, %s)")
        data = (product_name, description, category, unit_price, quantity)
        cursor.execute(query, data)
        connection.commit()
        print("Product added successfully")
        return True
    except Error as e:
        print("Error while adding product to MySQL", e)
        return False


def add_sale(connection, product_id, customer_name, quantity, payment):
    try:
        cursor = connection.cursor()
        # Fetch product details
        query_product = "SELECT product_name, unit_price, quantity FROM products WHERE product_id = %s"
        cursor.execute(query_product, (product_id,))
        product_details = cursor.fetchone()
        if product_details:
            product_name, unit_price, available_quantity = product_details
            if available_quantity >= quantity:
                # Calculate total price
                total_price = unit_price * quantity
                # Subtract sold quantity from available quantity
                new_quantity = available_quantity - quantity
                # Update product quantity
                update_query = "UPDATE products SET quantity = %s WHERE product_id = %s"
                cursor.execute(update_query, (new_quantity, product_id))
                # Add sale to the sales table
                query = (
                    "INSERT INTO sales (product_id, customer_name, quantity, sale_date, unit_price, total_price, payment) "
                    "VALUES (%s, %s, %s, CURDATE(), %s, %s, %s)")
                data = (product_id, customer_name, quantity, unit_price, total_price, payment)
                cursor.execute(query, data)
                connection.commit()
                print("Sale added successfully")
                return True
            else:
                print("Error: Insufficient quantity available for sale")
                return False
        else:
            print("Error: Product not found")
            return False
    except Error as e:
        print("Error while adding sale to MySQL", e)
        return False


# Function to remove a product from the database
def remove_product(connection, product_id):
    try:
        cursor = connection.cursor()

        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

        query = "DELETE FROM products WHERE product_id = %s"
        data = (product_id,)
        cursor.execute(query, data)

        # Enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

        connection.commit()
        print("Product deleted successfully")
        return True
    except Error as e:
        print("Error while deleting product from MySQL:", e)
        return False


# Function to update a product in the database
def update_product(connection, product_id, **kwargs):
    try:
        cursor = connection.cursor()
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE products SET {set_clause} WHERE product_id = %s"

        # Append product_id to data tuple
        data = tuple(kwargs.values()) + (product_id,)

        cursor.execute(query, data)
        connection.commit()
        print("Product updated successfully")
        return True
    except Error as e:
        print("Error while updating product in MySQL", e)
        return False


def login(connection, username, password):
    try:
        cursor = connection.cursor()
        query = "SELECT username, role FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user_data = cursor.fetchone()
        return user_data  # Returns (username, role) if login is successful, else returns None
    except Error as e:
        print("Error while fetching user from MySQL", e)
        return None


def fetch_categories(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT DISTINCT category_name FROM categories"
        cursor.execute(query)
        categories = [row[0] for row in cursor.fetchall()]
        return categories
    except Error as e:
        print("Error while fetching categories from MySQL", e)
        return []


# Function to fetch all products from the database
def fetch_products(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT product_id, product_name, quantity FROM products"
        cursor.execute(query)
        products = cursor.fetchall()
        return products
    except Error as e:
        print("Error while fetching products from MySQL", e)
        return []


# Main function
def main():
    connection = connect_to_database()
    if connection is None:
        print("Error: Unable to connect to the database.")
        return

    try:
        # Login
        while True:
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_data = login(connection, username, password)
            if user_data:
                username, role = user_data
                print("Login successful. Welcome,", username)
                break
            else:
                print("Invalid username or password. Please try again.")

        # System operations
        while True:
            print("\nSelect Operation:")
            if role == 'admin':
                print("1. Add Product")
                print("2. Remove Product")
                print("3. Update Product")
                print("4. Fetch Products")
                print("5. Make Sale")
            elif role == 'staff':
                print("1. Fetch Products")
                print("2. Make Sale")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if role == 'admin':
                if choice == '1':
                    # Add product
                    categories = fetch_categories(connection)
                    product_name = input("Enter product name: ")
                    description = input("Enter description: ")
                    print("Available categories:")
                    for idx, category in enumerate(categories, start=1):
                        print(f"{idx}. {category}")
                    category_number = input("Enter category: ")
                    category = categories[int(category_number) - 1] if category_number.isdigit() and 1 <= int(
                        category_number) <= len(categories) else ''
                    unit_price = input("Enter unit price: ")
                    quantity = input("Enter quantity: ")
                    add_product(connection, product_name, description, category, unit_price, quantity)
                    print("Product Added Successfully")

                elif choice == '2':
                    # Remove product operation
                    products = fetch_products(connection)
                    print("Available products:")
                    for product in products:
                        print(f"ID: {product[0]}, Name: {product[1]}")

                    product_id = input("Select product ID to remove: ")
                    if product_id.isdigit():
                        product_id = int(product_id)
                        if any(product[0] == product_id for product in products):
                            remove_product(connection, product_id)
                            print("Product deleted successfully.")
                        else:
                            print("Product with the entered ID does not exist.")
                    else:
                        print("Invalid input. Please enter a valid product ID.")

                elif choice == '3':
                    # Update product operation
                    products = fetch_products(connection)
                    print("Available products:")
                    for product in products:
                        print(f"ID: {product[0]}, Name: {product[1]}")
                    product_id = input("Select product ID to update: ")
                    if product_id.isdigit():
                        product_id = int(product_id)
                        if any(product[0] == product_id for product in products):
                            print("Select attribute to update:")
                            print("1. Product Name")
                            print("2. Description")
                            print("3. Category")
                            print("4. Unit Price")
                            print("5. Quantity")
                            attribute_choice = input("Enter your choice: ")
                            if attribute_choice.isdigit() and 1 <= int(attribute_choice) <= 5:
                                attribute_index = int(attribute_choice) + 1  # Adjusting index for tuple access
                                new_value = input("Enter the new value: ")
                                # Mapping the attribute index to the corresponding attribute name
                                attribute_names = {
                                    1: "product_name",
                                    2: "description",
                                    3: "category",
                                    4: "unit_price",
                                    5: "quantity"
                                }
                                attribute_name = attribute_names[attribute_index]
                                # Update the product with the new value
                                update_product(connection, product_id, **{attribute_name: new_value})
                                print("Product updated successfully.")
                            else:
                                print("Invalid attribute choice.")
                        else:
                            print("Product with the entered ID does not exist.")
                    else:
                        print("Invalid input. Please enter a valid product ID.")

                elif choice == '4':
                    # Fetch products operation
                    products = fetch_products(connection)
                    for product in products:
                        print(product)

                elif choice == '5':
                    # Make sale
                    products = fetch_products(connection)
                    print("Available products:")
                    for product in products:
                        print(f"ID: {product[0]}, Name: {product[1]}, Quantity: {product[2]}")
                    product_id = input("Enter product ID: ")
                    customer_name = input("Enter customer name: ")
                    quantity = int(input("Enter quantity: "))
                    payment = input("Enter payment method (cash, mobile money, card): ")
                    if add_sale(connection, product_id, customer_name, quantity, payment):
                        print("Sale Added Successfully")

                elif choice == '6':
                    # Exit the program
                    break

            elif role == 'staff':
                if choice == '1':
                    # Fetch products operation
                    products = fetch_products(connection)
                    for product in products:
                        print(product)

                elif choice == '2':
                    # Make sale for staff
                    products = fetch_products(connection)
                    print("Available products:")
                    for product in products:
                        print(f"ID: {product[0]}, Name: {product[1]}, Quantity: {product[2]}")
                    product_id = input("Enter product ID: ")
                    customer_name = input("Enter customer name: ")
                    quantity = int(input("Enter quantity: "))
                    payment = input("Enter payment method (cash, mobile money, card): ")
                    if add_sale(connection, product_id, customer_name, quantity, payment):
                        print("Sale Added Successfully")

                elif choice == '6':
                    # Exit the program
                    break

            else:
                print("Invalid choice. Please select a valid option.")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Close the database connection
        if connection:
            connection.close()


if __name__ == '__main__':
    main()

