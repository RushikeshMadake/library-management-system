import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime
import pandas as pd


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* Main page */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Hero section */
.hero {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white !important;
    margin-bottom: 25px;
}

.hero h1 {
    color: white !important;
    font-size: 38px;
    margin-bottom: 5px;
}

.hero p {
    color: white !important;
    font-size: 17px;
    opacity: 0.95;
}

/* Section headings */
.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 15px;
}

/* Recently added book card */

<div class="book-card">
    <b>📕 {book['title']}</b>
    <br><br>
    <strong>Author:</strong> {book['author']}
    <br>
    <strong>Available:</strong> 
    {book['available_copies']} / {book['total_copies']}
    <br>
    <strong>Book ID:</strong> {book['id']}
    <br>
    <strong>Added On:</strong> {book['added_on']}
</div>
    
)

/* Book title */
.book-card b {
    color: var(--text-color) !important;
    font-size: 18px;
}

/* Book information */
.book-card div,
.book-card span,
.book-card p {
    color: var(--text-color) !important;
}

/* Make dataframe readable */
[data-testid="stDataFrame"] {
    border-radius: 10px;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}

/* Metric values */
[data-testid="stMetricValue"] {
    font-weight: 700;
}

/* Expander text */
[data-testid="stExpander"] {
    border-radius: 10px;
}

/* Input boxes */
input, textarea {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LIBRARY CLASS
# =========================================================

class Library:

    database = "library.json"

    data = {
        "books": [],
        "members": []
    }

    # -----------------------------------------------------
    # LOAD DATABASE
    # -----------------------------------------------------

    @classmethod
    def load_data(cls):

        path = Path(cls.database)

        if path.exists():

            try:

                with open(cls.database, "r") as f:

                    content = f.read().strip()

                    if content:
                        cls.data = json.loads(content)

                    else:
                        cls.data = {
                            "books": [],
                            "members": []
                        }

            except json.JSONDecodeError:

                cls.data = {
                    "books": [],
                    "members": []
                }

        else:

            cls.save_data()

    # -----------------------------------------------------
    # SAVE DATABASE
    # -----------------------------------------------------

    @classmethod
    def save_data(cls):

        with open(cls.database, "w") as f:

            json.dump(
                cls.data,
                f,
                indent=4
            )

    # -----------------------------------------------------
    # GENERATE ID
    # -----------------------------------------------------

    @staticmethod
    def gen_id(prefix="B"):

        random_id = ""

        for _ in range(5):

            random_id += random.choice(
                string.ascii_uppercase + string.digits
            )

        return f"{prefix}-{random_id}"

    # -----------------------------------------------------
    # ADD BOOK
    # -----------------------------------------------------

    @classmethod
    def add_book(cls, title, author, copies):

        book = {

            "id": cls.gen_id("B"),

            "title": title,

            "author": author,

            "total_copies": copies,

            "available_copies": copies,

            "added_on": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        cls.data["books"].append(book)

        cls.save_data()

    # -----------------------------------------------------
    # ADD MEMBER
    # -----------------------------------------------------

    @classmethod
    def add_member(cls, name, email):

        member = {

            "id": cls.gen_id("M"),

            "name": name,

            "email": email,

            "borrowed": []
        }

        cls.data["members"].append(member)

        cls.save_data()

    # -----------------------------------------------------
    # BORROW BOOK
    # -----------------------------------------------------

    @classmethod
    def borrow_book(cls, member_id, book_id):

        member = next(
            (
                m for m in cls.data["members"]
                if m["id"] == member_id
            ),
            None
        )

        if not member:

            return False, "Member not found."

        book = next(
            (
                b for b in cls.data["books"]
                if b["id"] == book_id
            ),
            None
        )

        if not book:

            return False, "Book not found."

        if book["available_copies"] <= 0:

            return False, "No copies available."

        # Prevent same member from borrowing same book twice
        for borrowed in member["borrowed"]:

            if borrowed["book_id"] == book_id:

                return False, "This member already borrowed this book."

        borrow_entry = {

            "book_id": book["id"],

            "title": book["title"],

            "borrow_on": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        member["borrowed"].append(borrow_entry)

        book["available_copies"] -= 1

        cls.save_data()

        return True, "Book borrowed successfully."

    # -----------------------------------------------------
    # RETURN BOOK
    # -----------------------------------------------------

    @classmethod
    def return_book(cls, member_id, book_id):

        member = next(
            (
                m for m in cls.data["members"]
                if m["id"] == member_id
            ),
            None
        )

        if not member:

            return False, "Member not found."

        borrowed_book = next(
            (
                b for b in member["borrowed"]
                if b["book_id"] == book_id
            ),
            None
        )

        if not borrowed_book:

            return False, "This book is not borrowed by this member."

        member["borrowed"].remove(borrowed_book)

        book = next(
            (
                b for b in cls.data["books"]
                if b["id"] == book_id
            ),
            None
        )

        if book:

            book["available_copies"] += 1

        cls.save_data()

        return True, "Book returned successfully."


# =========================================================
# LOAD DATA
# =========================================================

Library.load_data()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 📚 Library")

    st.markdown("---")

    page = st.radio(

        "Navigation",

        [
            "🏠 Dashboard",
            "📚 Books",
            "👥 Members",
            "📖 Borrow Book",
            "↩️ Return Book"
        ]
    )

    st.markdown("---")

    st.caption(
        "Library Management System"
    )

    st.caption(
        "Built with Python + OOP + Streamlit"
    )


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">

    <h1>📚 Library Management System</h1>

    <p>
    Manage books, members, borrowing and returns
    from one modern dashboard.
    </p>

    </div>
    """, unsafe_allow_html=True)

    books = Library.data["books"]

    members = Library.data["members"]

    total_books = sum(
        b["total_copies"]
        for b in books
    )

    available_books = sum(
        b["available_copies"]
        for b in books
    )

    borrowed_books = (
        total_books - available_books
    )

    total_members = len(members)

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📚 Total Books",
            total_books
        )

    with col2:

        st.metric(
            "✅ Available",
            available_books
        )

    with col3:

        st.metric(
            "📖 Borrowed",
            borrowed_books
        )

    with col4:

        st.metric(
            "👥 Members",
            total_members
        )

    st.markdown("---")

    # -----------------------------------------------------
    # CHARTS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Book Availability")

        chart_data = pd.DataFrame({

            "Status": [
                "Available",
                "Borrowed"
            ],

            "Books": [
                available_books,
                borrowed_books
            ]
        })

        st.bar_chart(
            chart_data.set_index("Status")
        )

    with col2:

        st.subheader("📚 Books by Author")

        if books:

            author_count = {}

            for book in books:

                author = book["author"]

                author_count[author] = (
                    author_count.get(author, 0) + 1
                )

            author_df = pd.DataFrame({

                "Author": author_count.keys(),

                "Books": author_count.values()
            })

            st.bar_chart(
                author_df.set_index("Author")
            )

        else:

            st.info("No books available.")

    # -----------------------------------------------------
    # RECENT BOOKS
    # -----------------------------------------------------

    st.subheader("🆕 Recently Added Books")

    if books:

        recent_books = books[-5:][::-1]

        for book in recent_books:

            st.markdown(
                f"""
                <div class="book-card">

                <b>📕 {book['title']}</b><br>

                Author: {book['author']}<br>

                Available:
                {book['available_copies']}
                /
                {book['total_copies']}

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info("No books added yet.")


# =========================================================
# BOOKS
# =========================================================

elif page == "📚 Books":

    st.title("📚 Book Management")

    tab1, tab2 = st.tabs(
        [
            "➕ Add Book",
            "🔎 Browse Books"
        ]
    )

    # -----------------------------------------------------
    # ADD BOOK
    # -----------------------------------------------------

    with tab1:

        st.subheader("Add New Book")

        with st.form("add_book_form"):

            title = st.text_input(
                "Book Title"
            )

            author = st.text_input(
                "Author"
            )

            copies = st.number_input(
                "Number of Copies",
                min_value=1,
                step=1
            )

            submitted = st.form_submit_button(
                "➕ Add Book"
            )

            if submitted:

                if not title or not author:

                    st.error(
                        "Please enter title and author."
                    )

                else:

                    Library.add_book(
                        title,
                        author,
                        copies
                    )

                    st.success(
                        "Book added successfully!"
                    )

                    st.rerun()

    # -----------------------------------------------------
    # BROWSE BOOKS
    # -----------------------------------------------------

    with tab2:

        search = st.text_input(
            "🔎 Search by title or author"
        )

        books = Library.data["books"]

        filtered_books = [

            b for b in books

            if search.lower() in b["title"].lower()
            or search.lower() in b["author"].lower()
        ]

        if filtered_books:

            book_df = pd.DataFrame(filtered_books)

            book_df = book_df[
                [
                    "id",
                    "title",
                    "author",
                    "total_copies",
                    "available_copies",
                    "added_on"
                ]
            ]

            st.dataframe(
                book_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No books found.")


# =========================================================
# MEMBERS
# =========================================================

elif page == "👥 Members":

    st.title("👥 Member Management")

    tab1, tab2 = st.tabs(
        [
            "➕ Add Member",
            "👥 Member List"
        ]
    )

    # -----------------------------------------------------
    # ADD MEMBER
    # -----------------------------------------------------

    with tab1:

        st.subheader("Register New Member")

        with st.form("member_form"):

            name = st.text_input(
                "Full Name"
            )

            email = st.text_input(
                "Email Address"
            )

            submitted = st.form_submit_button(
                "➕ Add Member"
            )

            if submitted:

                if not name or not email:

                    st.error(
                        "Please fill all fields."
                    )

                elif "@" not in email:

                    st.error(
                        "Please enter a valid email."
                    )

                else:

                    Library.add_member(
                        name,
                        email
                    )

                    st.success(
                        "Member added successfully!"
                    )

                    st.rerun()

    # -----------------------------------------------------
    # MEMBER LIST
    # -----------------------------------------------------

    with tab2:

        members = Library.data["members"]

        if members:

            for member in members:

                with st.expander(
                    f"👤 {member['name']} — {member['id']}"
                ):

                    st.write(
                        f"**Email:** {member['email']}"
                    )

                    borrowed = member["borrowed"]

                    st.write(
                        f"**Books borrowed:** {len(borrowed)}"
                    )

                    if borrowed:

                        for book in borrowed:

                            st.write(
                                f"📖 {book['title']} "
                                f"({book['book_id']})"
                            )

                    else:

                        st.info(
                            "No books currently borrowed."
                        )

        else:

            st.info("No members registered.")


# =========================================================
# BORROW BOOK
# =========================================================

elif page == "📖 Borrow Book":

    st.title("📖 Borrow a Book")

    members = Library.data["members"]

    books = [
        b for b in Library.data["books"]
        if b["available_copies"] > 0
    ]

    if not members:

        st.warning(
            "Please add a member first."
        )

    elif not books:

        st.warning(
            "No books are currently available."
        )

    else:

        member_options = {
            f"{m['name']} ({m['id']})": m["id"]
            for m in members
        }

        book_options = {

            f"{b['title']} — {b['author']} "
            f"({b['available_copies']} available)": b["id"]

            for b in books
        }

        selected_member = st.selectbox(
            "👤 Select Member",
            list(member_options.keys())
        )

        selected_book = st.selectbox(
            "📚 Select Book",
            list(book_options.keys())
        )

        if st.button(
            "📖 Borrow Book",
            type="primary"
        ):

            success, message = Library.borrow_book(

                member_options[selected_member],

                book_options[selected_book]
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)


# =========================================================
# RETURN BOOK
# =========================================================

elif page == "↩️ Return Book":

    st.title("↩️ Return Book")

    members = [

        m for m in Library.data["members"]

        if m["borrowed"]
    ]

    if not members:

        st.info(
            "No members currently have borrowed books."
        )

    else:

        member_options = {

            f"{m['name']} ({m['id']})": m["id"]

            for m in members
        }

        selected_member = st.selectbox(

            "👤 Select Member",

            list(member_options.keys())
        )

        member_id = member_options[
            selected_member
        ]

        member = next(

            m for m in Library.data["members"]

            if m["id"] == member_id
        )

        borrowed_books = member["borrowed"]

        book_options = {

            f"{b['title']} ({b['book_id']})":
            b["book_id"]

            for b in borrowed_books
        }

        selected_book = st.selectbox(

            "📖 Select Book to Return",

            list(book_options.keys())
        )

        if st.button(

            "↩️ Return Book",

            type="primary"
        ):

            success, message = Library.return_book(

                member_id,

                book_options[selected_book]
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)