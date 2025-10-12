from database import Database

db = Database()
db.connect()

# Insert a student
db.insert_student("Ahmed Ali", 20, "A")

# Fetch and display all students
print("\n📋 All Students:")
students = db.fetch_students()
for s in students:
    print(s)

# ✅ UPDATE TEST
if students:
    student_id = students[-1]['id']  # get the last inserted student's ID
    print(f"\n🔄 Updating student with ID {student_id}...")
    db.update_student(student_id, name="Ahmed Alaa", age=21, grade="A+")

    # Fetch again to confirm update
    print("\n📋 Students After Update:")
    updated_students = db.fetch_students()
    for s in updated_students:
        print(s)
else:
    print("⚠️ No students found to update.")

# Delete one by ID (optional)
# if students:
#    db.delete_student(students[-1]['id'])

db.close()
