


from string import ascii_letters
size = len(ascii_letters)
goal = 7000000 // size

with open("large.txt", "w") as f:
    current = 0
    while current < goal:
        f.write(ascii_letters)
        current += 1
