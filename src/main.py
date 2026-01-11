import re
from search_by_number import search_by_course_number, create_session
from optimal_schedule import optimize_schedule
from parsing import parse_input_from_db
from database import init_db, course_exists, save_course, get_all_courses_for_term

# ────────────────────────────────────────────────────────────────
# INPUT/ADJUSTMENTS
# ────────────────────────────────────────────────────────────────

COURSES = {""}
EXCLUDE_PROFS = {""}

# Term codes: last 2 digits determine season
# 10 = winter, 20 = summer, 30 = fall
TERM = "202610"  # Winter 2026

SHOW_LOCATION = True
DARK_MODE = False

# ────────────────────────────────────────────────────────────────


def fetch_courses():
    """Fetch course data from Carleton Central and save to database."""
    course_numbers = [re.search(r'\d+', c).group() for c in COURSES if re.search(r'\d+', c)]
    
    # Check which courses need fetching
    to_fetch = [num for num in course_numbers if not course_exists(TERM, num)]
    
    if not to_fetch:
        print("All course data already cached")
        return
    
    print(f"Fetching course numbers: {to_fetch}")
    
    session, sess_id = create_session(TERM)
    if session is None:
        print("Failed to create session")
        return
    
    for course_num in to_fetch:
        print(f"Fetching {course_num}...")
        result = search_by_course_number(course_num, TERM, session, sess_id)
        if result:
            save_course(TERM, course_num, result)
            print(f"{course_num} done")
        else:
            print(f"{course_num} failed")


def generate_schedule():
    """Parse course data from database and generate optimal schedule."""
    import optimal_schedule as opt
    opt.EXCLUDE_PROFS = EXCLUDE_PROFS
    
    course_numbers = [re.search(r'\d+', c).group() for c in COURSES if re.search(r'\d+', c)]
    courses = parse_input_from_db(COURSES, TERM, course_numbers)
    optimize_schedule(courses, show_location=SHOW_LOCATION, dark_mode=DARK_MODE)


if __name__ == "__main__":
    init_db()
    fetch_courses()
    generate_schedule()
