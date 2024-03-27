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

def add_relationship(person_id1, person_id2, relationship_type):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO relationships (person_id1, person_id2, relationship_type)
        VALUES (%s, %s, %s);
    """, (person_id1, person_id2, relationship_type))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Relationship added between {person_id1} and {person_id2} as {relationship_type}.")

def view_family_members():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT person_id, first_name, last_name FROM persons;")
    for row in cur.fetchall():
        print(f"ID: {row[0]}, Name: {row[1]} {row[2]}")
    cur.close()
    conn.close()

def show_tree_structure(person_id):
    conn = connect_to_db()
    cur = conn.cursor()
    # Fetch the person's details
    cur.execute("SELECT first_name, last_name FROM persons WHERE person_id = %s;", (person_id,))
    person = cur.fetchone()
    if person:
        print(f"\nFamily Tree for {person[0]} {person[1]}:\n")
    else:
        print("Person not found.")
        return

    # Fetch and display relationships
    cur.execute("""
        SELECT p.person_id, p.first_name, p.last_name, r.relationship_type
        FROM relationships r
        JOIN persons p ON p.person_id = r.person_id2
        WHERE r.person_id1 = %s;
    """, (person_id,))
    for row in cur.fetchall():
        print(f"{row[3].capitalize()}: {row[1]} {row[2]} (ID: {row[0]})")

    cur.close()
    conn.close()

def main_menu():
    while True:
        print("\nFamily Tree App")
        print("1. Add person")
        print("2. Add relationship")
        print("3. View family members")
        print("4. Show tree structure")
        print("5. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            first_name = input("Enter first name: ")
            middle_name = input("Enter middle name: ")
            last_name = input("Enter last name: ")
            gender = input("Enter gender: ")
            add_person(first_name, middle_name, last_name, gender)
        elif choice == '2':
            person_id1 = input("Enter first person ID: ")
            person_id2 = input("Enter second person ID: ")
            relationship_type = input("Enter relationship type: ")
            add_relationship(person_id1, person_id2, relationship_type)
        elif choice == '3':
            view_family_members()
        elif choice == '4':
            person_id = input("Enter person ID to show tree structure: ")
            show_tree_structure(person_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":
    main_menu()
