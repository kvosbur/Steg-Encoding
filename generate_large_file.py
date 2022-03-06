


from string import ascii_letters
new_append = ascii_letters + "\n"
size = len(new_append)
goal = 500000000 // size

with open("large.txt", "w") as f:
    current = 0
    while current < goal:
        f.write(new_append)
        current += 1
