import psycopg2

def connect_to_db():
    conn = psycopg2.connect(
        dbname="family-tree-db", user="postgres",
        password="qrc135zx", host="localhost"
    )
    return conn

def add_person(first_name, middle_name, last_name, gender, mother_id=None, father_id=None):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO persons (first_name, middle_name, last_name, gender, mother_id, father_id)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING person_id;
    """, (first_name, middle_name, last_name, gender, mother_id, father_id))
    person_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    print(f"Person added with ID: {person_id}")

def view_family_members():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT person_id, first_name, last_name FROM persons;")
    for row in cur.fetchall():
        print(f"ID: {row[0]}, Name: {row[1]} {row[2]}")
    cur.close()
    conn.close()

def main_menu():
    while True:
        print("\nFamily Tree App")
        print("1. Add person")
        print("2. View family members")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            first_name = input("Enter first name: ")
            middle_name = input("Enter middle name: ")
            last_name = input("Enter last name: ")
            gender = input("Enter gender: ")
            # For simplicity, we skip entering mother and father ID here
            add_person(first_name, middle_name, last_name, gender)
        elif choice == '2':
            view_family_members()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":
    main_menu()

