import json
import random
import string
from pathlib import Path
from datetime import datetime


class Library:

    database = "library.json"
    data = {"books": [], "members": []}

    # Load existing data if file exists
    if Path(database).exists():
        with open(database, "r") as f:
            content = f.read().strip()

            if content:
                data = json.loads(content)

    else:
        with open(database, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def gen_id(prefix="B"):
        random_id = ""

        for i in range(5):
            random_id += random.choice(
                string.ascii_uppercase + string.digits
            )

        return prefix + "-" + random_id

    @classmethod
    def save_data(cls):
        with open(cls.database, "w") as f:
            json.dump(cls.data, f, indent=4, default=str)


    def add_book(self):

        title = input("Enter the book title: ")
        author = input("Enter the book author: ")
        copies = int(input("How many copies: "))

        book = {
            "id": Library.gen_id(),
            "title": title,
            "author": author,
            "total_copies": copies,
            "available_copies": copies,
            "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        Library.data["books"].append(book)
        Library.save_data()

        print("Book added successfully!")


    def list_books(self):

        if not Library.data["books"]:
            print("Sorry, no books found.")
            return

        print("\nBooks:")
        print("-" * 80)

        for b in Library.data["books"]:

            print(
                f"{b['id']:12} "
                f"{b['title'][:24]:25} "
                f"{b['author'][:19]:20} "
                f"{b['total_copies']} / {b['available_copies']:>3}"
            )

        print()


    def add_member(self):

        name = input("Enter the name: ")
        email = input("Please enter the email: ")

        member = {
            "id": Library.gen_id("M"),
            "name": name,
            "email": email,
            "borrowed": []
        }

        Library.data["members"].append(member)
        Library.save_data()

        print("Member added successfully!")


    def list_members(self):

        if not Library.data["members"]:
            print("There are no members.")
            return

        for m in Library.data["members"]:

            print(
                f"{m['id']:12} "
                f"{m['name'][:24]:25} "
                f"{m['email'][:29]:30}"
            )

            print("Currently borrowed:")

            if m["borrowed"]:
                for b in m["borrowed"]:
                    print(f"  - {b['title']} ({b['book_id']})")
            else:
                print("  No books borrowed.")

            print()


    def borrow(self):

        member_id = input("Enter the member ID: ").strip()

        members = [
            m for m in Library.data["members"]
            if m["id"] == member_id
        ]

        if not members:
            print("No such member ID exists.")
            return

        member = members[0]

        book_id = input("Enter the book ID: ").strip()

        books = [
            b for b in Library.data["books"]
            if b["id"] == book_id
        ]

        if not books:
            print("Sorry, no such book ID exists.")
            return

        book = books[0]

        if book["available_copies"] <= 0:
            print("Sorry, no copies of this book are available.")
            return

        borrow_entry = {
            "book_id": book["id"],
            "title": book["title"],
            "borrow_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        member["borrowed"].append(borrow_entry)

        book["available_copies"] -= 1

        Library.save_data()

        print("Book borrowed successfully!")


    def return_book(self):

        member_id = input("Enter the member ID: ").strip()

        members = [
            m for m in Library.data["members"]
            if m["id"] == member_id
        ]

        if not members:
            print("No such member ID exists.")
            return

        member = members[0]

        if not member["borrowed"]:
            print("No borrowed books.")
            return

        print("\nBorrowed books:")

        for i, b in enumerate(member["borrowed"], start=1):
            print(f"{i}. {b['title']} ({b['book_id']})")

        try:
            choice = int(input("Enter number to return: "))

            if choice < 1 or choice > len(member["borrowed"]):
                print("Invalid choice.")
                return

            selected = member["borrowed"].pop(choice - 1)

        except ValueError:
            print("Please enter a valid number.")
            return

        books = [
            bk for bk in Library.data["books"]
            if bk["id"] == selected["book_id"]
        ]

        if books:

            books[0]["available_copies"] += 1

            Library.save_data()

            print("Book returned successfully!")

        else:
            print("Book not found in library database.")




hello = Library()

while True:

    print("=" * 50)
    print("Library Management System")
    print("=" * 50)

    print("1. Add Book")
    print("2. List Books")
    print("3. Add Member")
    print("4. List Members")
    print("5. Borrow Book")
    print("6. Return Book")
    print("0. Exit the portal")

    print("=" * 50)

    choice = input("What task you want to do: ").strip()

    if choice == "1":
        hello.add_book()

    elif choice == "2":
        hello.list_books()

    elif choice == "3":
        hello.add_member()

    elif choice == "4":
        hello.list_members()

    elif choice == "5":
        hello.borrow()

    elif choice == "6":
        hello.return_book()

    elif choice == "0":
        print("Thank you for using Library Management System!")
        break

    else:
        print("Invalid choice. Please try again.")