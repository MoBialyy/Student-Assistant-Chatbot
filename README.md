
# Student Assistant Chatbot

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1)
![Made by Mo Bialy](https://img.shields.io/badge/Made_by-Mo_Bialy-lightgrey)

A simple **student management chatbot** built using **Python, Streamlit, and MySQL (XAMPP)**.  
The chatbot handles **predefined commands** such as:

- **Add new student** (Admin-only)
- **Update student** (Admin-only)
- **Delete student** (Admin-only)
- **View student list** (All)
- **Find student by name or ID** (All)

Designed as **Milestone 1** of a larger chatbot project — future versions may include **voice input, NLP, and AI-based question handling**.

---

## 🚀 Features

| Feature | Users | Admin |
|---------|--------|--------|
| View students | ✅ Yes | ✅ Yes |
| Search by ID / Name | ✅ Yes | ✅ Yes |
| Add / Delete / Update students | ❌ No | ✅ Yes |
| Voice input (Future) | 🔄 Planned | 🔄 Planned |
| AI-powered Answers (Future) | 🔄 Planned | 🔄 Planned |

Currently, the chatbot **only responds to fixed patterns** (not AI/NLP yet).  
Check `chatbot.py` to see the **command structure**.

---

## 🛠️ How to Run Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/MoBialyy/Student-Assistant-Chatbot.git
cd Student-Assistant-Chatbot
````

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install streamlit mysql-connector-python
```

*(More libraries may be added later — for now, these are enough.)*

### 4️⃣ Setup Database (XAMPP / phpMyAdmin)

* Start **XAMPP → MySQL → Admin**
* Start **Apache**
* Start **MySQL → Admin**
* Create a database named: `student_db`
* Create a table named: `students` with at least:

| id (INT, PK, AI) | name (VARCHAR) | age (INT) | grade (VARCHAR) |

* Or manually run this SQL script:

```bash
CREATE DATABASE student_db;
USE student_db;
CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  age INT,
  grade VARCHAR(50)
);
```

### 5️⃣ Run the Chatbot

```bash
streamlit run .\app.py
```

---

## 📌 Future Plans

* ✅ **Milestone 1:** Basic command-based chatbot with Streamlit UI
* 🔄 **Milestone 2, 3:** Upgrade to **AI-powered NLP responses**

---

Made with ❤️ by **Mo Bialy**
