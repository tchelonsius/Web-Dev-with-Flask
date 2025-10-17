# 📚 Library on the web

This web application demonstrates key concepts of Flask and its related modules.
It provides an interactive interface where each authenticated user can manage their own book collection — including adding, editing, and deleting books with their respective title, author, and rating.
Users must register and log in to access the application, and each user's data is isolated, ensuring that no one can view or modify another user's books.
---
![](library_v2.gif)
---

## 🆕 Update (v2.0)
- Added user authentication (registration and login) and techniques for keeping passwords secure in the DB
- Each user now has their own private book collection, meaning they can't access or edit each other's books
- Improved database structure using SQLAlchemy relationships
- Html files inheritance from jinja2 was used to make files more organized and clean
- Flash messages in login and registration pages are displayed when users try to authenticate incorrectly

---

When the user authenticate himself, the flask application interacts with a SQLite DB, where the books
from each user are stored. The interaction between the application and the DB is done via SQLAlchemy.
The forms used for logging in, registering, adding and editing a book are validated by WTForms.
The styling used in the html files was created using Bootstrap. The passwords are securely stored in the DB 
using hash functions (SHA256 with 8-character salt).


---

# 🛠️ Technologies Used

Flask — web framework

SQLAlchemy — ORM for database operations

SQLite — lightweight database

WTForms — form handling and validation

Flask Login — for authenticating users

Werkzeug Security — keeps the passwords safe

Bootstrap — Customization and Styling 

---
