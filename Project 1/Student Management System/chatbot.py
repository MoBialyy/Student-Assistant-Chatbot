from database import Database

class Chatbot:
    def __init__(self):
        self.db = Database()
        self.db.connect()
        print("🤖 Chatbot ready! Type 'help' to see available commands.\n")

    def respond(self, user_input, role="user"): 
        user_input = user_input.lower().strip()

        # --------------- BASIC COMMANDS ---------------
        if user_input in ["hi", "hello"]:
            return "👋 Hi! I'm Lilo, your Student Assistant Bot. Type 'help' to see what I can do!"
        
        elif user_input == "help":
            if role == "admin":
                return (
                    "🧭 **Admin Commands:**\n"
                    "- show all students\n"
                    "- find student [name] OR find student [id]\n"
                    "- add student [name] [age] [grade]\n"
                    "- update student [id] [name] [age] [grade]\n"
                    "- delete student [id]\n"
                    "- bye to exit"
                )
            else: # regular user
                return (
                    "🧭 **User Commands:**\n"
                    "- show all students\n"
                    "- find student [name] OR find student [id]\n"
                    "- bye to exit"
                )

        # Show Students
        elif user_input.lower() == "show all students":
            students = self.db.fetch_students()
            if not students:
                return "😕 No students found."

            response = "📋 **Students List:**\n\n"
            response += "| 🆔 ID | 👤 Name | 🎂 Age | 🎓 Grade |\n"
            response += "|:----:|:--------|:----:|:------:|\n"
            for s in students:
                response += f"| {s['id']} | {s['name']} | {s['age']} | {s['grade'].upper()} |\n"

            return response


        # Find Student by Name or ID
        elif user_input.startswith("find student"):
            query = user_input.replace("find student", "").strip()
            if not query:
                return "❌ Please specify a name or ID. Example: find student Ahmed OR find student 3"
            students = self.db.fetch_students()
            # Check if user entered a numeric ID
            if query.isdigit():
                student_id = int(query)
                matches = [s for s in students if s['id'] == student_id]
            else:
                matches = [s for s in students if query.lower() in s['name'].lower()]
            
            if matches:
                result = "\n".join([
                    f"ID: {s['id']}, Name: {s['name']}, Age: {s['age']}, Grade: {s['grade'].upper()}"
                    for s in matches
                ])
                return f"🔍 Found:\n{result}"
            else:
                return f"🙅 No student found matching '{query}'."

        # Add Student
        elif user_input.startswith("add student"):
            if role != "admin":
                return "🚫 You don't have permission to add students."
            try:
                parts = user_input.split()
                if len(parts) < 5:
                    return "❌ Format error. Use: add student [name] [age] [grade]"
                
                # remove 'add' and 'student'
                parts = parts[2:]
                age = int(parts[-2])
                grade = parts[-1].lower()
                name = " ".join(parts[:-2])
                
                # Validate grade
                valid_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F','a+', 'a', 'a-', 'b+', 'b', 'b-', 'c+', 'c', 'c-', 'd+', 'd', 'f']
                if grade not in valid_grades:
                    return "❌ Invalid grade. Valid grades are: A+, A, A-, B+, B, B-, C+, C, C-, D+, D, F"
                
                self.db.insert_student(name, age, grade)
                return f"✅ Student '{name}' added successfully!"
            except ValueError:
                return "❌ Format error. Age must be a number."
            except Exception as e:
                return f"⚠️ Error adding student: {e}"

        # Update Student
        elif user_input.startswith("update student"):
            if role != "admin":
                return "🚫 You don't have permission to update students."
            try:
                _, _, sid, name, age, grade = user_input.split(" ", 5)
                grade = grade.lower()
                
                # Validate grade
                valid_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F', 'a+', 'a', 'a-', 'b+', 'b', 'b-', 'c+', 'c', 'c-', 'd+', 'd', 'f']
                if grade not in valid_grades:
                    return "❌ Invalid grade. Valid grades are: A+, A, A-, B+, B, B-, C+, C, C-, D+, D, F"
                
                self.db.update_student(int(sid), name, int(age), grade)
                return f"✏️ Student ID {sid} updated successfully!"
            except ValueError:
                return "❌ Format error. Use: update student [id] [name] [age] [grade]"
            except Exception as e:
                return f"⚠️ Error updating student: {e}"

        # Delete Student
        elif user_input.startswith("delete student"):
            if role != "admin":
                return "🚫 You don’t have permission to delete students."
            try:
                _, _, sid = user_input.split(" ", 2)
                self.db.delete_student(int(sid))
                return f"🗑️ Student ID {sid} deleted successfully!"
            except ValueError:
                return "❌ Format error. Use: delete student [id]"
            except Exception as e:
                return f"⚠️ Error deleting student: {e}"

        elif user_input in ["bye", "exit", "quit"]:
            self.db.close()
            return "👋 Goodbye! Have a nice day."

        else:
            return "🤔 Sorry, I didn’t understand that. Type 'help' to see available commands."
