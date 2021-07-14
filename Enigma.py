import json
import os
from typing import Iterator

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Key=Rotor name && Value=Rotor letters order
rotors_dict = {"I": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "II": "AJDKSIRUXBLHWTMCQGZNPYFVOE",
               "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "IV": "SBTMZDHYIACWNKEUOPRJLQXGFV",
               "V": "NMXPJCSUFGVIKREBTQAZOLHYDW"}


class Rotor:
    """
    A class used to represent an single Rotor in the machine

    Attributes
    ----------
    rotor : str
        a string represents the letters order in the rotor
    notch : str
        a letter represents the cipher

    Methods
    -------
    set_start(letter):
        Rotate the rotor until reach the letter given
    translate(letter):
        Return encoded letter
    reverse(letter):
        Return decoded letter
    rotate():
        Rotate the rotor if reached the cipher (notch)
    """
    def __init__(self, rotor, notch, letter):
        self.rotor = rotor
        self.notch = notch
        self.set_start(letter)

    def set_start(self, letter: str) -> None:
        while self.rotor[0] != letter:
            self.rotate()

    def translate(self, letter: str) -> str:
        spot = alphabet.find(letter)
        return self.rotor[spot]

    def reverse(self, letter: str) -> str:
        spot = self.rotor.find(letter)
        return alphabet[spot]

    def rotate(self) -> bool:
        turn_over = False
        if self.rotor[0] == self.notch:
            turn_over = True
        self.rotor = self.rotor[1:] + self.rotor[0]
        return turn_over


def encode_letter(letter: str, left: Rotor, middle: Rotor, right: Rotor, reflector) -> str:
    # Encode a single letter
    for r in (right, middle, left):
        letter = r.translate(letter)  # Forward
    letter = reflector[letter]  # Reflector
    for r in (left, middle, right):
        letter = r.reverse(letter)  # Backward
    return letter


def encode(message: str, left: Rotor, middle: Rotor, right: Rotor, reflector) -> str:
    # Encode a message given as a parameter
    secret = ""
    message = message.upper()

    for letter in message:
        if alphabet.find(letter) >= 0:
            letter = encode_letter(letter, left, middle, right, reflector)
            # turn_over: if the Rotor reached the notch then True returned
            turn_over = right.rotate()
            if turn_over:
                turn_over = middle.rotate()
            if turn_over:
                left.rotate()
        # Append the encoded letter to the secret (encoded
        secret = secret + letter
    return secret


def get_day_from_user() -> int:
    # Get a day number (in month) from the user
    day = -1
    while day < 1 or day > 31:
        try:
            day = int(input('Please enter a day (1 - 31): '))
        except ValueError:
            continue
    return day


def get_path_from_user(operation: str) -> str:
    # Get a path from the user
    path = input('Enter {} file path: '.format(operation))
    return path


def let_user_choose() -> int:
    # Let the user choose: encode input or files
    choose = -1
    while choose != 1 and choose != 2:
        try:
            choose = int(input("Press 1 to encode message or 2 to encode file: "))
        except ValueError:
            continue
    return choose


def read_json_file(path: str) -> dict:
    # Read the cipher book into dictionary
    try:
        with open(path) as file:
            # Return dictionary from the json in the "Cipher_Book"
            return json.load(file)
    except FileNotFoundError:
        print("File not found, program aborted...")
        return dict()


def read_txt_file(path: str) -> list:
    # Read the txt file given from the user
    try:
        with open(path) as file:
            lines = []
            # Read line by line and append to list
            for line in file:
                lines.append(line)
        return lines
    except FileNotFoundError:
        print("TXT file (to read) not found, program aborted...")
        return []


def split_to_groups(msg: str, n: int) -> Iterator[str]:
    # Split a message into a groups of n
    while msg:
        yield msg[:n]
        msg = msg[n:]


def set_rotors(data: dict, day: str) -> tuple:
    left = Rotor(rotors_dict[data[day]["rotors"][0]], data[day]["notch"][0], data[day]["start"][0])
    middle = Rotor(rotors_dict[data[day]["rotors"][1]], data[day]["notch"][1], data[day]["start"][1])
    right = Rotor(rotors_dict[data[day]["rotors"][2]], data[day]["notch"][2], data[day]["start"][2])
    return left, middle, right


def encode_user_input(data: dict, reflector) -> None:
    # Encode a message given from the user
    day = str(get_day_from_user())
    msg = input("Enter a message: ")

    # Set the rotors by the given day
    left, middle, right = set_rotors(data, day)

    # Encode message given by the user
    code = encode(msg, left, middle, right, reflector).replace(" ", "")
    # Print the secret in groups of 5 letters
    print(' '.join(list(split_to_groups(code, 5))))


def encode_file(data: dict, reflector) -> None:
    # Encode a file a write the secret to another file
    read_file = get_path_from_user("read")  # Test: ./to_encode.txt
    # Read the text in the given file
    lines = read_txt_file(read_file)
    # Exit program if file load has failed
    if not bool(lines):
        exit(1)

    write_file = get_path_from_user("write")  # Test: ./secret.txt
    # Remove file if already exists
    if os.path.exists(write_file):
        os.remove(write_file)

    with open(write_file, "a") as to_write:
        for line in lines:
            # Get the day from the line beginning
            day = line[0:2].strip()
            # Set the rotors by the day (Name, notch and start)
            left, middle, right = set_rotors(data, day)
            # Get the message to encode
            message = line[2:].strip()
            secret = encode(message, left, middle, right, reflector)
            # Write the secret to the file
            to_write.write(str(day) + " " + secret + "\n")

    print("Secret written to file...")


def main():
    data = read_json_file('./Cipher_Book.json')
    reflector = read_json_file('./Reflector.json')

    # Check if "Cipher book" successfully read"
    if not bool(data):
        return 1

    choose = let_user_choose()

    switch = {
        1: encode_user_input,
        2: encode_file
    }

    switch.get(choose)(data, reflector)


if __name__ == '__main__':
    main()
