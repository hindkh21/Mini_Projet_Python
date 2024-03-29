import tkinter
from tkinter import messagebox
import sqlite3

window = tkinter.Tk()
window.title("Login form")
window.geometry('340x440')
window.configure(bg='#333333')

# Create or connect to the SQLite database
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS Department (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS College (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    department_id INTEGER,
                    FOREIGN KEY (department_id) REFERENCES Department(id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Person (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Teacher (
                    id INTEGER PRIMARY KEY,
                    person_id INTEGER,
                    department_id INTEGER,
                    FOREIGN KEY (person_id) REFERENCES Person(id),
                    FOREIGN KEY (department_id) REFERENCES Department(id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Course (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    teacher_id INTEGER,
                    salle_id INTEGER,
                    hour TEXT,  -- Adding hour attribute
                    FOREIGN KEY (teacher_id) REFERENCES Teacher(id),
                    FOREIGN KEY (salle_id) REFERENCES Salle(id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Salle (
                    id INTEGER PRIMARY KEY,
                    number TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Student (
                    id INTEGER PRIMARY KEY,
                    person_id INTEGER,
                    FOREIGN KEY (person_id) REFERENCES Person(id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Note (
                    id INTEGER PRIMARY KEY,
                    student_id INTEGER,
                    course_id INTEGER,
                    grade INTEGER,
                    FOREIGN KEY (student_id) REFERENCES Student(id),
                    FOREIGN KEY (course_id) REFERENCES Course(id)
                )''')

cursor.execute("INSERT INTO Department (name) VALUES ('Computer Science')")
cursor.execute("INSERT INTO Department (name) VALUES ('Mathematics')")
cursor.execute("INSERT INTO Department (name) VALUES ('Physics')")
conn.commit()

# Insert data into College table
cursor.execute("INSERT INTO College (name, department_id) VALUES ('College of Engineering', 1)")
cursor.execute("INSERT INTO College (name, department_id) VALUES ('College of Sciences', 2)")
conn.commit()

# Insert data into Person table (for teachers and students)
cursor.execute("INSERT INTO Person (name, email) VALUES ('Teacher1', 'teacher1@example.com')")
cursor.execute("INSERT INTO Person (name, email) VALUES ('Teacher2', 'teacher2@example.com')")
cursor.execute("INSERT INTO Person (name, email) VALUES ('Student1', 'student1@example.com')")
cursor.execute("INSERT INTO Person (name, email) VALUES ('Student2', 'student2@example.com')")
conn.commit()

# Insert data into Teacher table
cursor.execute("INSERT INTO Teacher (person_id, department_id) VALUES (1, 1)")
cursor.execute("INSERT INTO Teacher (person_id, department_id) VALUES (2, 2)")
conn.commit()

# Insert data into Salle table
cursor.execute("INSERT INTO Salle (number) VALUES ('101')")
cursor.execute("INSERT INTO Salle (number) VALUES ('102')")
cursor.execute("INSERT INTO Salle (number) VALUES ('103')")
conn.commit()

# Insert data into Course table
cursor.execute("INSERT INTO Course (name, teacher_id, salle_id, hour) VALUES ('Introduction to Programming', 1, 1, '9:00 - 11:00')")
cursor.execute("INSERT INTO Course (name, teacher_id, salle_id, hour) VALUES ('Linear Algebra', 2, 2, '11:00 - 13:00')")
conn.commit()

# Insert data into Student table
cursor.execute("INSERT INTO Student (person_id) VALUES (3)")
cursor.execute("INSERT INTO Student (person_id) VALUES (4)")
conn.commit()

# Insert data into Note table
cursor.execute("INSERT INTO Note (student_id, course_id, grade) VALUES (1, 1, 10)")
cursor.execute("INSERT INTO Note (student_id, course_id, grade) VALUES (2, 2, 13)")
conn.commit()

def teacher_login():
    login("teacher")

def student_login():
    login("student")

def login(user_type):
    # Get email from entry field
    email = email_entry.get()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Search for the user in the database
    cursor.execute("SELECT * FROM Person WHERE email = ?", (email,))
    user = cursor.fetchone()

    # Close the database connection
    conn.close()
    
    if user is not None:
        # Determine user type based on the interface they should be directed to
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Teacher WHERE person_id = ?", (user[0],))
        teacher = cursor.fetchone()
        conn.close()

        if teacher is not None:
            messagebox.showinfo(title="Login Success", message="Teacher login successful.")
            open_teacher_interface(user[1])
        else:
            messagebox.showinfo(title="Login Success", message="Student login successful.")
            open_student_interface(user[1])
    else:
        messagebox.showerror(title="Error", message="Invalid login.")


def open_teacher_interface(username):
    teacher_window = tkinter.Toplevel(window)
    teacher_window.title("Teacher Interface")
    teacher_window.geometry('300x200')
    
    timetable_button = tkinter.Button(teacher_window, text="View Timetable", command=lambda: open_timetable_interface(username))
    timetable_button.pack(pady=10)

    marks_button = tkinter.Button(teacher_window, text="Insert Marks", command=lambda: open_marks_interface(username))
    marks_button.pack(pady=10)


def open_marks_interface(username):
    marks_window = tkinter.Toplevel(window)
    marks_window.title("Insert Marks")
    marks_window.geometry('300x200')
    
    # Connect to the SQLite database
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Query student IDs taught by the teacher from the Note table
    cursor.execute("SELECT DISTINCT n.student_id, p.name FROM Note n JOIN Student s ON n.student_id = s.id JOIN Person p ON s.person_id = p.id WHERE n.course_id IN (SELECT id FROM Course WHERE teacher_id = (SELECT id FROM Teacher WHERE person_id = (SELECT id FROM Person WHERE name = ?)))", (username,))
    students = cursor.fetchall()

    # Query courses taught by the teacher
    cursor.execute("SELECT id, name FROM Course WHERE teacher_id = (SELECT id FROM Teacher WHERE person_id = (SELECT id FROM Person WHERE name = ?))", (username,))
    courses = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Student selection label and dropdown menu
    student_label = tkinter.Label(marks_window, text="Select Student:", bg='#333333', fg='white')
    student_label.pack(pady=5)
    student_var = tkinter.StringVar(marks_window)
    student_var.set(students[0][0])  # Default to the first student
    student_dropdown = tkinter.OptionMenu(marks_window, student_var, *[student[0] for student in students])
    student_dropdown.pack(pady=5)

    # Course selection label and dropdown menu
    course_label = tkinter.Label(marks_window, text="Select Course:", bg='#333333', fg='white')
    course_label.pack(pady=5)
    course_var = tkinter.StringVar(marks_window)
    course_var.set(courses[0][0])  # Default to the first course
    course_dropdown = tkinter.OptionMenu(marks_window, course_var, *[course[0] for course in courses])
    course_dropdown.pack(pady=5)

    # Mark entry label and entry field
    mark_label = tkinter.Label(marks_window, text="Enter Mark:", bg='#333333', fg='white')
    mark_label.pack(pady=5)
    mark_entry = tkinter.Entry(marks_window)
    mark_entry.pack(pady=5)

    # Function to insert mark into the Note table
    def insert_mark():
        student_id = student_var.get()
        course_id = course_var.get()
        mark = mark_entry.get()
        
        if mark.isdigit() and 0 <= int(mark) <= 100:
            # Connect to the SQLite database
            conn = sqlite3.connect('school.db')
            cursor = conn.cursor()

            # Insert mark into Note table
            cursor.execute("INSERT INTO Note (student_id, course_id, grade) VALUES (?, ?, ?)", (student_id, course_id, mark))
            conn.commit()

            # Close the database connection
            conn.close()

            messagebox.showinfo(title="Success", message="Mark inserted successfully.")
        else:
            messagebox.showerror(title="Error", message="Please enter a valid mark (0-100).")

    # Button to insert mark
    insert_button = tkinter.Button(marks_window, text="Insert Mark", command=insert_mark)
    insert_button.pack(pady=10)

# Rest of the code remains unchanged

# Rest of the code remains unchanged

# Rest of the code remains unchanged

def open_student_marks(username):
    student_marks_window = tkinter.Toplevel(window)
    student_marks_window.title("Student Marks")
    student_marks_window.geometry('400x300')

    # Connect to the SQLite database
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Query marks for the student
    cursor.execute("SELECT c.name, n.grade FROM Course c JOIN Note n ON c.id = n.course_id JOIN Student st ON n.student_id = st.id JOIN Person p ON st.person_id = p.id WHERE p.name = ?", (username,))
    marks_data = cursor.fetchall()

    # Frame for displaying marks
    marks_frame = tkinter.Frame(student_marks_window)
    marks_frame.pack(padx=10, pady=10)

    # Marks label
    marks_label = tkinter.Label(marks_frame, text="Your Marks", font=("Arial", 12, "bold"))
    marks_label.pack(pady=10)

    # Display marks data
    for data in marks_data:
        course_name, grade = data
        mark_entry = tkinter.Label(marks_frame, text=f"{course_name}: {grade}")
        mark_entry.pack(pady=5)

    # Close the database connection
    conn.close()

    # Rest of the code remains unchanged


def open_timetable_interface(username):

    teacher_window = tkinter.Toplevel(window)
    teacher_window.title("Teacher Interface")
    teacher_window.geometry('600x300')
    
    # Connect to the SQLite database
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Query timetable data for the teacher
    cursor.execute("SELECT c.name, s.number, c.hour FROM Course c JOIN Salle s ON c.salle_id = s.id JOIN Teacher te ON c.teacher_id = te.id JOIN Person p ON te.person_id = p.id WHERE p.name = ?", (username,))
    timetable_data = cursor.fetchall()

    # Frame for the timetable
    timetable_frame = tkinter.Frame(teacher_window, bg='#333333')
    timetable_frame.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)
    
    # Timetable label
    timetable_label = tkinter.Label(timetable_frame, text="Teacher Timetable", font=("Arial", 12, "bold"), bg='#333333', fg='white')
    timetable_label.pack(pady=10)
    
    # Display timetable data
    for data in timetable_data:
        course_name, salle_number, hour = data
        timetable_entry = tkinter.Label(timetable_frame, text=f"{course_name} - {salle_number} ({hour})", bg='#333333', fg='white')
        timetable_entry.pack(padx=5, pady=2, fill=tkinter.BOTH, expand=True)

    # Close the database connection
    conn.close()



def open_student_interface(username):
    student_window = tkinter.Toplevel(window)
    student_window.title("Student Interface")
    student_window.geometry('600x400')

    # Button to view marks
    view_marks_button = tkinter.Button(student_window, text="View Marks", command=lambda: open_student_marks(username))
    view_marks_button.pack(pady=10)
    # Query timetable data for the student
    cursor.execute("SELECT c.name, s.number, c.hour FROM Course c JOIN Salle s ON c.salle_id = s.id JOIN Note n ON c.id = n.course_id JOIN Student st ON n.student_id = st.id JOIN Person p ON st.person_id = p.id WHERE p.name = ?", (username,))
    timetable_data = cursor.fetchall()

    # Frame for the timetable
    timetable_frame = tkinter.Frame(student_window, bg='#333333')
    timetable_frame.pack(padx=10, pady=10, fill=tkinter.BOTH, expand=True)

    # Timetable label
    timetable_label = tkinter.Label(timetable_frame, text="Student Timetable", font=("Arial", 12, "bold"), bg='#333333', fg='white')
    timetable_label.pack(pady=10)

    # Display timetable data
    for data in timetable_data:
        course_name, salle_number, hour = data
        timetable_entry = tkinter.Label(timetable_frame, text=f"{course_name} - {salle_number} ({hour})", bg='#333333', fg='white')
        timetable_entry.pack(padx=5, pady=2, fill=tkinter.BOTH, expand=True)

    # Close the database connection
    conn.close()



# Email label and entry field
email_label = tkinter.Label(window, text="Email:", bg='#333333', fg='white')
email_label.grid(column=0, row=0, padx=10, pady=10)
email_entry = tkinter.Entry(window, width=30)
email_entry.grid(column=1, row=0, padx=10, pady=10)

# Login buttons for teacher and student
teacher_login_button = tkinter.Button(window, text="Teacher Login", command=teacher_login)
teacher_login_button.grid(column=0, row=1, padx=10, pady=10)

student_login_button = tkinter.Button(window, text="Student Login", command=student_login)
student_login_button.grid(column=1, row=1, padx=10, pady=10)

window.mainloop()

# Close the database connection when the application closes
conn.close()
