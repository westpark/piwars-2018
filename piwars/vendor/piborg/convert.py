import os, sys

filepath = sys.argv[1]

with open(filepath) as f:
    lines = f.read().splitlines()

lines2 = []
for line in lines:
    if line.strip().startswith("print "):
        line = line.replace("print ", "print(")
        line += ")"
    lines2.append(line)

with open(filepath, "w") as f:
    f.write("\n".join(lines2))
