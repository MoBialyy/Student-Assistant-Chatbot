class Student:
    def __init__(self, student_id=None, name=None, age=None, grade=None):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_age(self):
        return self.age
    
    def set_age(self, age):
        # to check if age is a positive integer
        if isinstance(age, int) and age > 0:
            self.age = age
        else:
            raise ValueError("Age must be a positive integer")
    
    def get_grade(self):
        return self.grade
    
    def set_grade(self, grade):
        self.grade = grade
    
    def update(self, name=None, age=None, grade=None):
        """Update student information"""
        if name:
            self.set_name(name)
        if age:
            self.set_age(age)
        if grade:
            self.set_grade(grade)
    
    def __str__(self):
        """String representation of the student"""
        return f"Student(ID: {self.student_id}, Name: {self.name}, Age: {self.age}, Grade: {self.grade})"
