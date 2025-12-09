import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="localhost", user="root", password="", database="student_db", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                print("✅ Connected")
        except Error as e:
            print(f"❌ Not Connected {e}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Connection Closed")

    # CRUD Operations

    def insert_student(self, name, age, grade):
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, age, grade))
            self.connection.commit()
            print("🟢 Student inserted successfully!")
        except Error as e:
            print(f"❌ Error inserting student: {e}")

    def fetch_students(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"❌ Error fetching students: {e}")
            return []

    def delete_student(self, student_id):
        try:
            cursor = self.connection.cursor()
            sql = "DELETE FROM students WHERE id = %s"
            cursor.execute(sql, (student_id,))
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"🗑️ Student with ID {student_id} deleted successfully!")
            else:
                print(f"⚠️ No student found with ID {student_id}.")
        except Error as e:
            print(f"❌ Error deleting student: {e}")

    def update_student(self, student_id, name=None, age=None, grade=None):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if age is not None:
                updates.append("age = %s")
                params.append(age)
            if grade is not None:
                updates.append("grade = %s")
                params.append(grade)

            if not updates:
                print("⚠️ Nothing to update.")
                return

            sql = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
            params.append(student_id)

            cursor.execute(sql, tuple(params))
            self.connection.commit()

            if cursor.rowcount > 0:
                print(f"✏️ Student with ID {student_id} updated successfully!")
            else:
                print(f"⚠️ No student found with ID {student_id}.")

        except Error as e:
            print(f"❌ Error updating student: {e}")
