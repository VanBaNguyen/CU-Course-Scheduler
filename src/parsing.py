import os
import re
from pprint import pprint

def parse_input(wanted_courses, term):
    # Store results
    results = []
    structured_results = []
    seen_courses = set()

    # --------------------------------------------------------------------- #
    # Locate the raw term file
    #
    # project/
    # ├── src/              ← parsing.py lives here
    # │   └── parsing.py
    # └── terms/            ← fall.txt, winter.txt, summer.txt
    #     ├── fall.txt
    #     ├── winter.txt
    #     └── summer.txt
    #
    # The code below climbs one directory up from src/ and
    # then descends into terms/<term>.
    # --------------------------------------------------------------------- #
    src_dir   = os.path.dirname(os.path.abspath(__file__))     # …/project/src
    project   = os.path.dirname(src_dir)                       # …/project
    terms_dir = os.path.join(project, "terms")                 # …/project/terms
    file_path = os.path.join(terms_dir, term)                  # …/project/terms/fall.txt

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Cannot find term file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for course code and section
        match = re.search(r"([A-Z]{4} \d{4})\s+([A-Z]+\d*)", line)
        if match:
            course_code = match.group(1)  # e.g., COMP 1005
            section = match.group(2)      # e.g., A or A1

            course_key = f"{course_code} {section}"
            if course_key in seen_courses:
                i += 1
                continue
            seen_courses.add(course_key)

            if course_code in wanted_courses:
                # Check if section contains a number
                has_number = bool(re.search(r"\d|T$", section))

                # Extract professor name
                parts = line.split()
                prof_name = " ".join(parts[-2:]) if len(parts) >= 2 else "Unknown"

                # Get next line for schedule info
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()

                    # Extract Days and Time
                    days_match = re.search(r"Days:\s*([A-Za-z ]+?)\s+Time:", next_line)
                    time_match = re.search(r"Time:\s*([\d:APM\- ]+)", next_line)

                    # Extract Building and Room
                    bldg_match = re.search(r"Building:\s*([^:]+?)\s+Room:", next_line)
                    room_match = re.search(r"Room:\s*([\w\- ]+)", next_line)

                    days  = days_match.group(1).strip()  if days_match else "Unknown"
                    time  = time_match.group(1).strip()  if time_match else "Unknown"
                    bldg  = bldg_match.group(1).strip()  if bldg_match else "Unknown"
                    room  = room_match.group(1).strip()  if room_match else "Unknown"

                    # Full course with section for display
                    full_course_code = f"{course_code} {section}"
                    formatted = f"{full_course_code} | {prof_name} | Days: {days} | Time: {time}"
                    results.append(formatted)

                    # Final structured result
                    structured_results.append([
                        has_number,
                        course_code,
                        section,
                        prof_name,
                        days,
                        time,
                        bldg,
                        room
                    ])

            i += 3
        else:
            i += 1

    # Optional: check structured results
    pprint(structured_results)

    return structured_results
