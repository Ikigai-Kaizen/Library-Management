import mysql.connector
from datetime import date, timedelta

# --- Database Connection ---
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="Your_Pass",  
        database="library_db"
    )

FINE_PER_DAY = 2
DEFAULT_BORROW_DAYS = 14

#--- Functions ---
def add_book(title, author, total_copies=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO books (title, author, total_copies, available_copies) VALUES (%s, %s, %s, %s)",
                (title, author, total_copies, total_copies))
    conn.commit()
    conn.close()
    print("✅ Book added successfully.")

def add_member(name, email, max_books_allowed=3):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO members (name, email, join_date, max_books_allowed) VALUES (%s, %s, %s, %s)",
                (name, email, date.today(), max_books_allowed))
    conn.commit()
    conn.close()
    print("✅ Member added successfully.")

def issue_book(book_id, member_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT available_copies FROM books WHERE book_id=%s", (book_id,))
    book = cur.fetchone()
    if not book or book['available_copies'] <= 0:
        print("❌ Book unavailable.")
        return

    cur.execute("SELECT COUNT(*) as cnt FROM transactions WHERE member_id=%s AND return_date IS NULL", (member_id,))
    issued = cur.fetchone()['cnt']
    cur.execute("SELECT max_books_allowed FROM members WHERE member_id=%s", (member_id,))
    limit = cur.fetchone()
    if not limit:
        print("❌ Member not found.")
        return
    if issued >= limit['max_books_allowed']:
        print("❌ Borrow limit reached.")
        return

    issue = date.today()
    due = issue + timedelta(days=DEFAULT_BORROW_DAYS)

    cur.execute("INSERT INTO transactions (book_id, member_id, issue_date, due_date) VALUES (%s, %s, %s, %s)",
                (book_id, member_id, issue, due))
    cur.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id=%s", (book_id,))
    conn.commit()
    conn.close()
    print(f"✅ Book issued successfully! Due date: {due}")

def return_book(book_id, member_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT trans_id, due_date FROM transactions WHERE book_id=%s AND member_id=%s AND return_date IS NULL",
                (book_id, member_id))
    trans = cur.fetchone()
    if not trans:
        print("❌ No active issue found for this member and book.")
        return

    today = date.today()
    due = trans['due_date']
    fine = 0
    if today > due:
        fine = (today - due).days * FINE_PER_DAY

    cur.execute("UPDATE transactions SET return_date=%s, fine_paid=%s WHERE trans_id=%s",
                (today, fine, trans['trans_id']))
    cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=%s", (book_id,))
    conn.commit()
    conn.close()
    print(f"✅ Book returned successfully! Fine: ₹{fine}")

def view_books():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    for row in cur.fetchall():
        print(row)
    conn.close()

def view_members():
    conn = get_conn()
    cur = conn.cursor()
    sql=("SELECT * FROM members")
    cur.execute(sql)
    for i in cur.fetchall():
        print("Member_ID:",i[0])
        print("Name:",i[1])
        print("Email:",i[2])
        print("Join_Date:",i[3])
        print("Max_Books_Allowed:",i[4])
    conn.close()

def view_transactions():
    conn = get_conn()
    cur = conn.cursor()
    sql=("SELECT * FROM transactions")
    cur.execute(sql)
    for i in cur.fetchall():
        print("Trans_Id:",i[0])
        print("Book_Id:",i[1])
        print("Member_Id:",i[2])
        print("Issue_Date:",i[3])
        print("Due_Date:",i[4])
        print("Return_Date:",i[5])
        print("Fine_Paid:",i[6])
    conn.close()

# --- Menu ---
def menu():
    while True:
        print("-"*68)
        print("\n=== Library Management System ===")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. View All Books")
        print("6. View All Members")
        print("7. View All Transactions")
        print("-"*68)
        print("8. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            copies = int(input("Enter total copies: "))
            add_book(title, author, copies)
            print("-"*68)
        elif choice == '2':
            name = input("Enter member name: ")
            email = input("Enter member email: ")
            add_member(name, email)
            print("-"*68)
        elif choice == '3':
            book_id = int(input("Enter Book ID: "))
            member_id = int(input("Enter Member ID: "))
            issue_book(book_id, member_id)
            print("-"*68)
        elif choice == '4':
            book_id = int(input("Enter Book ID: "))
            member_id = int(input("Enter Member ID: "))
            return_book(book_id, member_id)
            print("-"*68)
        elif choice == '5':
            view_books()
            print("-"*68)
        elif choice == '6':
            view_members()
            print("-"*68)
        elif choice == '7':
            view_transactions()
            print("-"*68)
        elif choice == '8':
            print("Goodbye!")
            print("-"*68)
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
