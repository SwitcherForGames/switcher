import glob
import os
import subprocess
import sys
import time
import yaml
from typing import List

# Set working directory to the location of this script.
os.chdir(os.path.abspath(os.path.dirname(__file__)))

args = sys.argv[1:]
assert len(args) > 0, "New version must be supplied as an argument."

new_tag = args[0]
commit = "--commit" in args
build = "--build" in args

with open("manifest.yaml", "r") as f:
    tag = yaml.safe_load(f).get("version")


def mutate(lines: List[str]) -> List[str]:
    lines = lines.copy()

    for index, line in enumerate(lines):
        if tag in line:
            lines[index] = line.replace(tag, new_tag)

    return lines


print(f"------ MODIFYING FILES -----\n")

for filename in glob.glob("**/*", recursive=True):
    if os.path.isdir(filename):
        continue

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except:
        continue

    mutated = mutate(lines)

    if lines != mutated:
        for index, (l1, l2) in enumerate(zip(lines, mutated)):
            if l1 != l2:
                print(f"{filename}: Modifying version tag on line {index+1}.")

        with open(filename, "w") as f:
            f.writelines(mutated)


if commit:
    print(f"\n\n------ CREATING GIT COMMIT -----\n")
    time.sleep(1)

    # Commit twice, because commit hooks may prevent the first commit.
    for i in range(2):
        os.system(f"git commit -am \"Bump version to {new_tag}\"")

if build:
    print(f"\n\n------ BUILDING EXECUTABLE WITH PYINSTALLER ------\n")
    time.sleep(1)
    os.system("pyinstaller windows.spec --noconfirm")

    print(f"\n\n------ CREATING INSTALLER WITH INNO SETUP ------\n")
    time.sleep(1)
    os.system("iscc windows.iss")

    print(f"\n\n------ PRINTING RELEASE TEMPLATE ------\n")
    checksum = subprocess.check_output('bash -c "sha256sum Output/SwitcherSetup.exe"', shell=True).decode("utf-8")
    template = f"### New features\n\n\n\n" + \
               f"### Checksums\n\n" + \
               f"`sha256` checksums are used to verify the integrity of the installer.\n\n" + \
               f"`{checksum.strip()}`\n"

    print(template)
    
