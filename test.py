key_map = {
    "A Button": 0,
    "B Button": 1,
    "X Button": 2,
    "Y Button": 3,
    "- Button": 4,
    "Home Button": 5,
    "+ Button": 6,
    "L. Stick In": 7,
    "R. Stick In": 8,
    "Left Bumper": 9,
    "Right Bumper": 10,
    "D-pad Up": 11,
    "D-pad Down": 12,
    "D-pad Left": 13,
    "D-pad Right": 14,
    "Capture Button": 15,
}

second_key_map = {}
for thing in key_map:
    second_key_map[thing] = "nothing"
print(second_key_map)
