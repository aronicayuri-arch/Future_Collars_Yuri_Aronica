# ─────────────────────────────────────────
#  School Management Software
# ─────────────────────────────────────────

# --- Data Storage ---
students = []           # list of dicts: {first, last, class_name}
teachers = []           # list of dicts: {first, last, subject, classes}
homeroom_teachers = []  # list of dicts: {first, last, class_name}


# ─────────────────────────────────────────
#  CREATE FUNCTIONS
# ─────────────────────────────────────────

def create_student():
    first = input("  First name: ").strip()
    last  = input("  Last name:  ").strip()
    class_name = input("  Class (e.g. 3C): ").strip()
    students.append({"first": first, "last": last, "class_name": class_name})
    print(f"  ✔ Student {first} {last} added to class {class_name}.\n")


def create_teacher():
    first   = input("  First name: ").strip()
    last    = input("  Last name:  ").strip()
    subject = input("  Subject:    ").strip()
    classes = []
    print("  Enter class names one by one (empty line to finish):")
    while True:
        class_name = input("    Class: ").strip()
        if class_name == "":
            break
        classes.append(class_name)
    teachers.append({"first": first, "last": last, "subject": subject, "classes": classes})
    print(f"  ✔ Teacher {first} {last} added.\n")


def create_homeroom_teacher():
    first      = input("  First name: ").strip()
    last       = input("  Last name:  ").strip()
    class_name = input("  Leads class (e.g. 3C): ").strip()
    homeroom_teachers.append({"first": first, "last": last, "class_name": class_name})
    print(f"  ✔ Homeroom teacher {first} {last} added for class {class_name}.\n")


def create_menu():
    options = "  [student | teacher | homeroom teacher | end]"
    while True:
        print("\n── Create User ──")
        print(options)
        choice = input("  > ").strip().lower()

        if choice == "student":
            create_student()
        elif choice == "teacher":
            create_teacher()
        elif choice == "homeroom teacher":
            create_homeroom_teacher()
        elif choice == "end":
            print("  Returning to main menu.\n")
            break
        else:
            print("  ✖ Unknown option. Try again.\n")


# ─────────────────────────────────────────
#  MANAGE FUNCTIONS
# ─────────────────────────────────────────

def manage_class():
    class_name = input("  Class name (e.g. 3C): ").strip()

    # Find students in this class
    class_students = [s for s in students if s["class_name"] == class_name]

    # Find homeroom teacher for this class
    hr_teacher = next((t for t in homeroom_teachers if t["class_name"] == class_name), None)

    if not class_students and hr_teacher is None:
        print(f"  ✖ No data found for class '{class_name}'.\n")
        return

    print(f"\n  Class {class_name}:")
    if class_students:
        print("  Students:")
        for s in class_students:
            print(f"    - {s['first']} {s['last']}")
    else:
        print("  Students: (none)")

    if hr_teacher:
        print(f"  Homeroom Teacher: {hr_teacher['first']} {hr_teacher['last']}")
    else:
        print("  Homeroom Teacher: (none)")
    print()


def manage_student():
    first = input("  Student first name: ").strip()
    last  = input("  Student last name:  ").strip()

    # Find the student
    student = next((s for s in students if s["first"] == first and s["last"] == last), None)
    if student is None:
        print(f"  ✖ Student '{first} {last}' not found.\n")
        return

    class_name = student["class_name"]

    # Find teachers who teach this student's class
    student_teachers = [t for t in teachers if class_name in t["classes"]]

    print(f"\n  Student: {first} {last}")
    print(f"  Class:   {class_name}")
    if student_teachers:
        print("  Teachers:")
        for t in student_teachers:
            print(f"    - {t['first']} {t['last']} ({t['subject']})")
    else:
        print("  Teachers: (none assigned)")
    print()


def manage_teacher():
    first = input("  Teacher first name: ").strip()
    last  = input("  Teacher last name:  ").strip()

    teacher = next((t for t in teachers if t["first"] == first and t["last"] == last), None)
    if teacher is None:
        print(f"  ✖ Teacher '{first} {last}' not found.\n")
        return

    print(f"\n  Teacher: {first} {last} — {teacher['subject']}")
    if teacher["classes"]:
        print("  Classes:")
        for c in teacher["classes"]:
            print(f"    - {c}")
    else:
        print("  Classes: (none assigned)")
    print()


def manage_homeroom_teacher():
    first = input("  Homeroom teacher first name: ").strip()
    last  = input("  Homeroom teacher last name:  ").strip()

    hr_teacher = next((t for t in homeroom_teachers if t["first"] == first and t["last"] == last), None)
    if hr_teacher is None:
        print(f"  ✖ Homeroom teacher '{first} {last}' not found.\n")
        return

    class_name = hr_teacher["class_name"]
    led_students = [s for s in students if s["class_name"] == class_name]

    print(f"\n  Homeroom Teacher: {first} {last} — Class {class_name}")
    if led_students:
        print("  Students:")
        for s in led_students:
            print(f"    - {s['first']} {s['last']}")
    else:
        print("  Students: (none in this class yet)")
    print()


def manage_menu():
    options = "  [class | student | teacher | homeroom teacher | end]"
    while True:
        print("\n── Manage ──")
        print(options)
        choice = input("  > ").strip().lower()

        if choice == "class":
            manage_class()
        elif choice == "student":
            manage_student()
        elif choice == "teacher":
            manage_teacher()
        elif choice == "homeroom teacher":
            manage_homeroom_teacher()
        elif choice == "end":
            print("  Returning to main menu.\n")
            break
        else:
            print("  ✖ Unknown option. Try again.\n")


# ─────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────

def main():
    print("=" * 40)
    print("   School Management Software")
    print("=" * 40)
    options = "  Commands: [create | manage | end]"

    while True:
        print(options)
        command = input("  > ").strip().lower()

        if command == "create":
            create_menu()
        elif command == "manage":
            manage_menu()
        elif command == "end":
            print("\n  Goodbye!\n")
            break
        else:
            print("  ✖ Unknown command. Try: create, manage, or end.\n")


# ─────────────────────────────────────────
main()
