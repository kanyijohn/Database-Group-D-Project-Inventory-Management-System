import mysql.connector


def add_students(name, admission_no):
    try:
        # Try connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='students'
        )
        cursor = connection.cursor()
        # Sql query to add students
        insert_query = "INSERT INTO students (student_name, Adm_no) VALUES (%s, %s)"
        values = (name, admission_no)

        # execute query
        cursor.execute(insert_query, values)
        connection.commit()
        print("student added successfully")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        # close Connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def main():
    name = input("Enter your name here: ")
    admission_no = input("Enter your admission here: ")

    add_students(name, admission_no)


if __name__ == "__main__":
    main()
