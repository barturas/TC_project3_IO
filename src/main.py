import os, sys, time, random, datetime
import csv, tabulate

class Questions: # should be @dataclass
    """Base class"""
    def __init__(self, question_id, text):
        self.id = question_id
        self.text = text
        self.is_active = True
        self.times_shown = 0
        self.times_correct = 0
        self.times_answered = 0

class QuizQuestions(Questions):
    """ Sub-class for quiz questions"""
    def __init__(self, question_id, text, choices, correct_answer):
        super().__init__(question_id, text)
        self.choices = choices
        self.correct_answer = correct_answer

class FreeFormQuestions(Questions):
    """ Sub-class for freeform questions"""
    def __init__(self, question_id, text, correct_answer):
        super().__init__(question_id, text)
        self.correct_answer = correct_answer

class QuestionManager:
    """ Class to manage questions """
    last_id = 0 # class variable shared across all instances

    def __init__(self):
        self.questions = []
        self.load_questions()

    def add_question(self):
        while True:
            question_id = QuestionManager.last_id
            question_type = input("Enter question type (quiz/freeform): ").lower()
            if question_type not in ["quiz", "freeform"]:
                print(red_text("Invalid question type"))
                continue
            question_text = input("Enter question text: ")

            if question_type == "quiz":
                choices = input("Enter the choices separated by commas: ").split(",")
                correct_answer = input("Enter the correct answer: ")

                while correct_answer not in choices:
                    print(red_text("The correct answer must be one of the choices. Please enter again."))
                    correct_answer = input("Enter the correct answer: ")

                question = QuizQuestions(question_id + 1, question_text, choices, correct_answer)
                QuestionManager.last_id += 1
            else:
                correct_answer = input("Enter the correct answer: ")
                question = FreeFormQuestions(question_id + 1, question_text, correct_answer)
                QuestionManager.last_id += 1

            self.questions.append(question)
            break

    def load_questions(self):
        self.questions.clear()
        try:
            with open("questions.csv", mode="r", newline="") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if len(row) == 8:
                        question_id, q_type, text, choices_str, correct_answer, is_active_str, times_answered_str, times_correct_str = row
                    elif len(row) == 7:
                        question_id, q_type, text, correct_answer, is_active_str, times_answered_str, times_correct_str = row
                        choices_str = ""  # no choices for FreeFormQuestions
                    else:
                        continue  # skip malformed rows

                    is_active = is_active_str.lower() == "true"
                    times_answered = int(times_answered_str)
                    times_correct = int(times_correct_str)

                    if q_type == "Quiz":
                        choices = choices_str.split(";") if choices_str else []
                        question = QuizQuestions(int(question_id), text, choices, correct_answer)
                    elif q_type == "FreeForm":
                        question = FreeFormQuestions(int(question_id), text, correct_answer)

                    question.is_active = is_active
                    question.times_answered = times_answered
                    question.times_correct = times_correct
                    self.questions.append(question)

                if self.questions:
                    QuestionManager.last_id = max(q.id for q in self.questions)

        except FileNotFoundError:
            print(red_text("\nThere are no questions yet"))

    def save_questions(self):

        with open("questions.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Type", "Text", "Choices", "CorrectAnswer", "IsActive", "TimesAnswered", "TimesCorrect"])

            for question in self.questions:
                if isinstance(question, QuizQuestions):
                    choices_str = ";".join(question.choices)
                    row = [question.id, "Quiz", question.text, choices_str, question.correct_answer, question.is_active, question.times_answered, question.times_correct]
                elif isinstance(question, FreeFormQuestions):
                    row = [question.id, "FreeForm", question.text, "", question.correct_answer, question.is_active, question.times_answered, question.times_correct]
                writer.writerow(row)

    def toggle_question_active(self, question_id):

            # question_to_toggle = next((q for q in self.questions if q.id == question_id), None)
            question_to_toggle = None
            for question in self.questions:
                if question.id == question_id:
                    question_to_toggle = question
                    break
            if question_to_toggle:
                question_to_toggle.is_active = not question_to_toggle.is_active
                status = f"Question ID {question_id} active status toggled."
                return True, green_text(status)
            else:
                status = f"No question found with ID {question_id}."
                return False, red_text(status)

    def delete_question(self, question_id):
        question_to_delete = next((q for q in self.questions if q.id == question_id), None)

        if question_to_delete:
            self.questions.remove(question_to_delete)
            status = f"Question with ID {question_id} has been deleted."
            return True, green_text(status)
        else:
            status = f"No question found with ID {question_id}."
            return False, red_text(status)

def weighted_question_choice(questions):
    weights = [(1 + q.times_answered - q.times_correct) for q in questions]
    return random.choices(questions, weights=weights, k=1)[0]

def red_text(text):
    return f"\033[91m{text}\033[0m"

def pause():
    while True:
        if input() == '':
            break

def green_text(text):
    return f"\033[92m{text}\033[0m"

def add_q(qm):

    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\33[1m\33[101m            Adding new questions            \33[0m")
        print("\33[3mUse Ctrl+D to stop and exit to Main Menu\n\33[0m")
        print("""
    Usage:
    <add> initiate adding
    <save> save and exit to main menu
              """)
        while True:
            control = input("Action?: ").lower()
            if control == "add":
                qm.add_question()
            elif control == "save":
                qm.save_questions()
                break
            else:
                continue

    except EOFError:
        main()

def modify_q(qm):
    status = green_text("Ready")
    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\33[1m\33[101m            Modify existing questions            \33[0m")
            print("\33[3mUse Ctrl + D to stop and exit to Main Menu\33[0m")
            print(f"""
    Usage:
    <delete [ID]> to delete a question
    <toggle [ID]> to toggle Active status

    Status: {status}
                """)
            qm.load_questions()
            if not qm.questions:
                print(red_text("\nMoving you to Main Menu\n"))
                for i in [".", ".", ".", "."]:
                    sys.stdout.write(str(i)+' ')
                    sys.stdout.flush()
                    time.sleep(1)
                break
            else:
                qm.load_questions()
                table_data = []
                for question in qm.questions:
                        question_type = "Quiz" if isinstance(question, QuizQuestions) else "FreeForm"
                        table_data.append([question.id, question_type, question.text, question.is_active])
                headers = ["ID", "Type", "Text", "Active"]
                create_table(table_data, headers)
                while True:
                    try:
                        control, id_str = input("Action?: ").lower().split()
                        question_id = int(id_str)
                        if control == "delete":
                            _, status = qm.delete_question(question_id)
                            qm.save_questions()
                            break
                        elif control == "toggle":
                            _, status = qm.toggle_question_active(question_id)
                            qm.save_questions()
                            break
                    except ValueError:
                        status = red_text("Invalid input format. Please use the format '<command> [ID]'.")
                        break
                    except EOFError:
                        return
                    except Exception as e:
                        status = red_text(f"An error occurred: {e}")
                        break
        except EOFError:
            break

def create_table(data, header):
    print(tabulate.tabulate(data, header, tablefmt='grid'))

def view_statistics(qm):
    try:
        qm.load_questions()
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\33[1m\33[101m                      Statistics mode                     \33[0m")
        print("\33[3mUse Ctrl+D or press 'Enter' to get back to main menu.\33[0m\n")
        if not qm.questions:
            print(red_text("No questions available for statistics."))
            return

        table_data = []
        for question in qm.questions:
            question_type = "Quiz" if isinstance(question, QuizQuestions) else "FreeForm"
            active_status = "Active" if question.is_active else "Inactive"

            if question.times_answered > 0:
                percentage_correct = (question.times_correct / question.times_answered) * 100
            else:
                percentage_correct = 0  # avoid division by zero

            table_data.append([
                question.id,
                question_type,
                question.text,
                active_status,
                question.times_answered,
                f"{percentage_correct:.2f}%"
            ])

        headers = ["ID", "Type", "Text", "Status", "Times Shown", "Percentage Correct"]
        create_table(table_data, headers)
        pause()
    except EOFError:
        pass

def practice_mode(qm):
    qm.load_questions()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\33[1m\33[101m                      Practice mode                     \33[0m")
    print("\33[3mUse Ctrl+D at any time to stop practicing.\33[0m\n")
    try:

        while True:

            question = weighted_question_choice(qm.questions)
            print(f"Question: {question.text}\n")

            if isinstance(question, QuizQuestions):
                for i, choice in enumerate(question.choices, 1):
                    print(f"{i}. {choice}")

                choice_number = None
                while choice_number is None:
                    try:
                        choice_number = int(input("\nChoice no: "))
                        if choice_number < 1 or choice_number > len(question.choices):
                            raise ValueError
                        user_answer = question.choices[choice_number - 1]  # Adjust index
                    except (IndexError, ValueError):
                        print(red_text("Invalid choice. Please enter a valid number."))
                        choice_number = None
            else:
                user_answer = input("Your answer: ").strip()

            correct_answer = question.correct_answer
            is_correct = user_answer.lower() == correct_answer.lower()

            if is_correct:
                print(green_text("Correct!"))
            else:
                print(red_text(f"Incorrect. The correct answer is: {correct_answer}"))

            question.times_answered += 1
            if is_correct:
                question.times_correct += 1
            qm.save_questions()

            print("")

    except EOFError:
        print("\nExiting practice mode.")

def test_mode(qm):
    qm.load_questions()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\33[1m\33[101m                      Test mode                     \33[0m")

    # Filter to include only active questions
    active_questions = [q for q in qm.questions if q.is_active]

    num_questions = 0
    while num_questions <= 0 or num_questions > len(active_questions):
        try:
            num_questions = int(input(f"How many questions would you like to attempt (max {len(active_questions)})? "))
        except ValueError:
            print(red_text("Please enter a valid number."))

    if not active_questions:
        print(red_text("There are no active questions available for the test."))
        return

    selected_questions = random.sample(active_questions, num_questions)
    score = 0

    for i, question in enumerate(selected_questions, 1):
        print(f"\nQuestion {i}: {question.text}")
        if isinstance(question, QuizQuestions):
            for idx, choice in enumerate(question.choices, 1):
                print(f"{idx}. {choice}")
            user_answer = question.choices[int(input("\nChoice no: ")) - 1]
        else:
            user_answer = input("Your answer: ").strip()

        if user_answer.lower() == question.correct_answer.lower():
            score += 1
            print(green_text("Correct!"))
        else:
            print(red_text(f"Incorrect. The correct answer is: {question.correct_answer}"))

    print("\nTest completed.")
    print(f"Your score: {score}/{num_questions}")
    print(f"\nPress Enter to save your score to file /results.txt")
    pause()
    with open("results.txt", "a") as file:
        file.write(f"{datetime.datetime.now()}: Score: {score}/{num_questions}\n")

    print(green_text("Your score has been saved. Press Enter to exit"))
    pause()

def main():
    try:
        alert = ""
        qm = QuestionManager()
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\33[1m\33[101m            Main menu            \33[0m")
            print(
                """\33[94m
        1. Add Questions\n
        2. View Statistics\n
        3. Modify Questions\n
        4. Practice Mode\n
        5. Test Mode\n
        6. Exit\n\33[0m"""
            )
            choice = input(f"Enter your choice {alert}: ")
            if choice == "1":
                alert = ""
                add_q(qm)
            elif choice == "2":
                alert = ""
                view_statistics(qm)
            elif choice == "3":
                alert = ""
                modify_q(qm)
            elif choice in ["4", "5"]:
                qm.load_questions()
                if len(qm.questions) < 5:
                    alert = red_text("At least 5 questions are required to enter this mode.")
                    # time.sleep(2)
                    continue
                else:
                    if choice == "4":
                        practice_mode(qm)
                    elif choice == "5":
                        test_mode(qm)

            elif choice == "6":
                alert = ""
                sys.exit(green_text("Exited."))
            else:
                alert = red_text("Invalid choice, please try again")
    except EOFError:
        sys.exit("This exit mode works as well :P")

if __name__ == "__main__":
    main()

# https://github.com/barturas/war_project.git