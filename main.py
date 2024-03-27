from graphviz import Digraph
import psycopg2

def connect_to_db():
    conn = psycopg2.connect(
        dbname="family-tree-db", user="postgres",
        password="qrc135zx", host="localhost"
    )
    return conn

# def add_person(first_name, middle_name, last_name, gender, mother_id=None, father_id=None):
#     conn = connect_to_db()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO persons (first_name, middle_name, last_name, gender, mother_id, father_id)
#         VALUES (%s, %s, %s, %s, %s, %s) RETURNING person_id;
#     """, (first_name, middle_name, last_name, gender, mother_id, father_id))
#     person_id = cur.fetchone()[0]
#     conn.commit()
#     cur.close()
#     conn.close()
#     print(f"Person added with ID: {person_id}")

def add_child(first_name, middle_name, last_name, gender, parent_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # Add the new child to the database
    cur.execute("""
        INSERT INTO persons (first_name, middle_name, last_name, gender, mother_id, father_id)
        VALUES (%s, %s, %s, %s, NULL, %s) RETURNING person_id;
    """, (first_name, middle_name, last_name, gender, parent_id))

    new_child_id = cur.fetchone()[0]
    conn.commit()

    # Automatically update sibling relationships
    update_sibling_relationships(new_child_id, parent_id)

    cur.close()
    conn.close()
    print(f"Child added with ID: {new_child_id}. Sibling relationships have been updated.")

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


def update_sibling_relationships(new_child_id, parent_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # Fetch existing children of the parent
    cur.execute("""
        SELECT person_id FROM persons
        WHERE mother_id = %s OR father_id = %s;
    """, (parent_id, parent_id))

    existing_children_ids = [row[0] for row in cur.fetchall() if row[0] != new_child_id]

    # For each existing child, create a sibling relationship with the new child
    for child_id in existing_children_ids:
        add_relationship(child_id, new_child_id, 'sibling')
        add_relationship(new_child_id, child_id, 'sibling')

    cur.close()
    conn.close()

def view_family_members():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT person_id, first_name, last_name FROM persons;")
    for row in cur.fetchall():
        print(f"ID: {row[0]}, Name: {row[1]} {row[2]}")
    cur.close()
    conn.close()


def generate_tree_graph(person_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # Fetch the root person's details
    cur.execute("SELECT first_name, last_name FROM persons WHERE person_id = %s;", (person_id,))
    person = cur.fetchone()

    dot = Digraph(comment='Family Tree')
    if person:
        root_label = f"{person[0]} {person[1]}"
        dot.node(str(person_id), root_label)
    else:
        print("Root person not found.")
        return

    # Fetch and add relationships
    cur.execute("""
        SELECT p.person_id, p.first_name, p.last_name, r.relationship_type
        FROM relationships r
        JOIN persons p ON p.person_id = r.person_id2
        WHERE r.person_id1 = %s;
    """, (person_id,))
    for row in cur.fetchall():
        child_label = f"{row[1]} {row[2]}"
        dot.node(str(row[0]), child_label)
        dot.edge(str(person_id), str(row[0]), label=row[3])

    # Save the dot file and render it to a PDF
    dot.render('family_tree.gv', view=True)

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
            generate_tree_graph(person_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":
    main_menu()
