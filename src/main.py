import re
from search_by_number import search_by_course_number, get_term_filepath, create_session
from optimal_schedule import optimize_schedule
from parsing import parse_input

# ────────────────────────────────────────────────────────────────
# INPUT/ADJUSTMENTS
# ────────────────────────────────────────────────────────────────

COURSES = {"COMP 2108", "COMP 2109"}
EXCLUDE_PROFS = {""}

# Term codes: last 2 digits determine season
# 10 = winter, 20 = summer, 30 = fall
TERM = "202610"  # Winter 2026

SHOW_LOCATION = True
DARK_MODE = False

# ────────────────────────────────────────────────────────────────


def get_term_filename(term):
    """Get just the filename based on term code."""
    suffix = term[-2:]
    if suffix == "10":
        return "winter.txt"
    elif suffix == "20":
        return "summer.txt"
    elif suffix == "30":
        return "fall.txt"
    return f"term_{term}.txt"


def get_term_filepath(term):
    """Get full filepath based on term code."""
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    return os.path.join(project_root, "terms", get_term_filename(term))


def fetch_courses():
    """Fetch course data from Carleton Central and save to term file."""
    course_numbers = [re.search(r'\d+', c).group() for c in COURSES if re.search(r'\d+', c)]
    print(f"Fetching course numbers: {course_numbers}")
    
    filepath = get_term_filepath(TERM)
    
    # Create a single session for all searches
    session, sess_id = create_session(TERM)
    if session is None:
        print("Failed to create session")
        return
    
    with open(filepath, "w") as f:
        f.write("")
    
    for course_num in course_numbers:
        print(f"\nFetching {course_num}...")
        result = search_by_course_number(course_num, TERM, session, sess_id)
        if result:
            with open(filepath, "a") as f:
                f.write(result + "\n")
            print(f"{course_num} done")
        else:
            print(f"{course_num} failed")
    
    print(f"\nSaved to {filepath}")


def generate_schedule():
    """Parse saved course data and generate optimal schedule."""
    import optimal_schedule as opt
    opt.EXCLUDE_PROFS = EXCLUDE_PROFS
    
    term_file = get_term_filename(TERM)
    courses = parse_input(COURSES, term_file)
    optimize_schedule(courses, show_location=SHOW_LOCATION, dark_mode=DARK_MODE)


if __name__ == "__main__":
    fetch_courses()
    generate_schedule()
