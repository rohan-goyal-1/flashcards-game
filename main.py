import random
import signal

def read_file (file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

def timeout_handler (signum, frame):
    raise TimeoutError

def ask_question_with_timeout (question, answer, time_limit):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(time_limit)
    try:
        user_answer = input(f"{question}: ")
        signal.alarm(0)
        if user_answer == "stop":
            return "stop"
        elif user_answer.casefold() != answer.casefold():
            return False
        else:
            return True
    except TimeoutError:
        print("\nTime's up!")
        return False

def main ():
    switch = input("Enter 1 to flip questions and answers, anything else if not: ")
    
    list1 = []
    list2 = []
    if switch == "1":
        list2 = read_file("questions")
        list1 = read_file("answers")
    else:
        list1 = read_file("questions")
        list2 = read_file("answers")

    if len(list1) != len(list2):
        raise ValueError("Files do not have the same number of lines")

    tests = [[list1[i], list2[i]] for i in range(len(list1))]

    response = input("Enter 1 for easy, 0 for hard, anything else for unlimited: ")
    difficulty = 10 if response == "1" else 5 if response == "0" else 1 << 31 - 1

    stopped = False
    while not stopped:
        random.shuffle(tests)
        temp = tests.copy()
        while len(temp) > 0:
            top = temp.pop(0)
            result = ask_question_with_timeout(top[0], top[1], difficulty)
            if result == "stop":
                stopped = True
                break
            elif not result:
                print(f"Wrong. Correct answer is {top[1]}.")
                # temp.insert(4, top)
            else:
                print("Correct.")

if __name__ == "__main__":
    main()

