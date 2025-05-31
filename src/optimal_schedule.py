import copy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict
from datetime import datetime, time
from itertools import combinations
from itertools import product
from parsing import parse_input


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DAY_TO_INDEX = {day: i for i, day in enumerate(DAYS)}

def _preferred_mains(mains):
    """
    Return a tuple (usable, force_flag).

    * usable – list of lecture slots we are allowed to schedule
    * force_flag – True  ⇢ every lecture is taught by an excluded prof
                   False ⇢ at least one good prof exists
    """
    good = [m for m in mains if m['prof'] not in EXCLUDE_PROFS]
    if good:                       # at least one acceptable professor
        return good, False
    # ‑‑ no alternative, keep the originals but mark them -------------
    for m in mains:
        m['forced_excluded'] = True
    return mains, True


# Helper: Convert "10:05 - 11:25" to (time(10,5), time(11,25))
def parse_time_range(time_str):
    if " - " not in time_str:
        # Handle missing or malformed time strings
        return None, None

    start_str, end_str = time_str.split(" - ")
    try:
        start = datetime.strptime(start_str.strip(), "%H:%M").time()
        end = datetime.strptime(end_str.strip(), "%H:%M").time()
        return start, end
    except ValueError:
        return None, None

# Helper: Convert "Mon Wed" → ["Mon", "Wed"]
def parse_days(days_str):
    return days_str.strip().split()

# Helper: Check for time conflict on the same day
def times_overlap(slot1, slot2):
    # If either slot is online, they can't conflict
    if not slot1['start'] or not slot2['start']:
        return False

    for day in slot1['days']:
        if day in slot2['days']:
            if not (slot1['end'] <= slot2['start'] or slot2['end'] <= slot1['start']):
                return True
    return False

# Build structured slots
def build_slots(course_list):
    slots = []
    for item in course_list:
        (has_number, course_code, section, prof, days_str, time_str, building, room) = item
        if prof == "No No" or prof == "Yes Yes" or prof == "term course":
            prof = "N/A"

        if time_str.strip() == "Unknown":
            start, end = None, None
            days = []
        else:
            start, end = parse_time_range(time_str)
            if not start or not end:
                print(f"⚠️  Skipping invalid time: {time_str} (Course: {course_code} {section})")
                continue  # Skip this entry
            days = parse_days(days_str)

        slot = {
            'has_number': has_number,
            'course': course_code,
            'section': section,
            'prof': prof,
            'days': days,
            'start': start,
            'end': end,
            'building': building,     # NEW
            'room': room,
            'original': item
        }
        slots.append(slot)
    return slots

# Group by course and section prefix
def group_by_course(slots):
    from collections import defaultdict
    course_groups = defaultdict(list)
    for slot in slots:
        course_groups[slot['course']].append(slot)
    return course_groups

# Generate all valid schedule combinations
def generate_valid_schedules(course_groups):
    course_keys = list(course_groups.keys())
    all_course_options = []

    for course in course_keys:
        sections = course_groups[course]
        mains_raw = [s for s in sections if not s['has_number']]
        tutorials       = [s for s in sections if s['has_number']]

        main_sections, forced_only_choice = _preferred_mains(mains_raw)

        course_options = []

        for main in main_sections:
            # Find matching tutorials for this lecture
            matching_tutorials = [tut for tut in tutorials if tut['section'].startswith(main['section'])]

            if matching_tutorials:
                for tut in matching_tutorials:
                    course_options.append([main, tut])
            else:
                # No tutorials for this lecture — allow lecture alone
                course_options.append([main])

        if not course_options:
            # If somehow no lectures at all exist, skip course
            continue

        all_course_options.append(course_options)

    if not all_course_options:
        return []

    # Try all combinations of course options
    all_combos = product(*all_course_options)
    valid_schedules = []

    for combo in all_combos:
        flat = [s for group in combo for s in group]  # flatten all sections
        conflict = False
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if times_overlap(flat[i], flat[j]):
                    conflict = True
                    break
            if conflict:
                break
        if not conflict:
            valid_schedules.append(flat)

    return valid_schedules

# Score Formula: (#days * 1000) + total_gap_minutes + early class penalty + prof
# Lower Score is better
def score_schedule(schedule):
    daily_slots = defaultdict(list)
    early_penalty = 0
    total_gap_minutes = 0
    prof_penalty = 0

    for slot in schedule:
        if not slot['start'] or not slot['end']:
            continue

        if slot['start'].hour < 9:
            early_penalty += 20

        # if slot['prof'] in AVOID_PROFS:
        #     prof_penalty += 1000

        for day in slot['days']:
            daily_slots[day].append(slot)

    total_days = len(daily_slots)

    for day, slots in daily_slots.items():
        slots.sort(key=lambda x: x['start'])
        for i in range(len(slots) - 1):
            gap = datetime.combine(datetime.today(), slots[i + 1]['start']) - datetime.combine(datetime.today(), slots[i]['end'])
            total_gap_minutes += max(0, gap.total_seconds() / 60)

    return total_days * 1000 + total_gap_minutes + early_penalty + prof_penalty

# Format for display
def display_schedule(schedule):
    print("\n--- Optimal Schedule ---")
    for s in sorted(schedule, key=lambda x: (x['days'], x['start'])):
        print(f"{s['course']} {s['section']} | {s['prof']} | Days: {' '.join(s['days'])} | Time: {s['start']} - {s['end']}")

# Display top 3 schedules
def display_top_schedules(scored_schedules, top_n=3):
    for idx, (score, sched) in enumerate(scored_schedules[:top_n]):
        print(f"\n--- Schedule #{idx + 1} | Score: {score:.2f} ---")
        for s in sorted(sched, key=lambda x: (x['days'], x['start'])):
            print(f"{s['course']} {s['section']} | {s['prof']} | Days: {' '.join(s['days'])} | Time: {s['start']} - {s['end']}")

def plot_schedule(schedule, *, show_location=True):
    # one‑time map: does this course appear with an OK professor anywhere?
    has_good_prof = {}
    for s in schedule:
        if s['prof'] not in EXCLUDE_PROFS:
            has_good_prof[s['course']] = True

    fig, ax = plt.subplots(figsize=(10, 8))

    # Grid: 5 days (Mon–Fri), 8am–6pm
    ax.set_xlim(0, 5)
    ax.set_ylim(8, 22)
    ax.invert_yaxis()

    ax.set_xticks(range(5))
    ax.set_xticklabels(DAYS)
    ax.set_yticks(range(8, 23))
    ax.set_yticklabels([f"{h:02d}:00" for h in range(8, 23)])
    ax.grid(True, linestyle='--', alpha=0.5)

    for slot in schedule:
        # Skip online courses (no time data)
        if not slot['start'] or not slot['end']:
            continue

        course = f"{slot['course']} {slot['section']}"
        prof = slot['prof']
        start_hour = slot['start'].hour + slot['start'].minute / 60
        end_hour = slot['end'].hour + slot['end'].minute / 60
        duration = end_hour - start_hour

        for day in slot['days']:
            if day not in DAY_TO_INDEX:
                continue
            x = DAY_TO_INDEX[day]
            y = start_hour

            # --------- choose colour ----------
            if (slot['prof'] in EXCLUDE_PROFS and
                not has_good_prof.get(slot['course'], False)):
                fill_colour = 'lightcoral'   # red – mandatory, no alternative
            else:
                fill_colour = 'skyblue'      # normal
            # ----------------------------------

            rect = patches.Rectangle((x, y), 0.95, duration,
                                     color=fill_colour, edgecolor='black')
            ax.add_patch(rect)

            # Display course and prof on separate lines
            location = f"{slot['building']}\nRoom Number: {slot['room']}".strip()
            if show_location and location not in ("", "Unknown"):
                label = f"{course}\n{prof}\n{location}"
            else:
                label = f"{course}\n{prof}"
            ax.text(x + 0.02, y + duration / 2, label,
                    va='center', ha='left', fontsize=9)

    ax.set_title("Your Optimal Weekly Schedule")
    plt.tight_layout()
    plt.show()

# Main function
def optimize_schedule(course_list, *, show_location=True):
    slots = build_slots(course_list)
    course_groups = group_by_course(slots)
    valid_schedules = generate_valid_schedules(course_groups)

    if not valid_schedules:
        print("No valid schedules found.")
        print("Please check for conflicting class times or missing tutorials.")
        return

    # Score and sort
    scored = [(score_schedule(sched), sched) for sched in valid_schedules]
    scored.sort(key=lambda x: x[0])

    # Show top 3
    display_top_schedules(scored, top_n=3)

    # Alter 0-3 for first index to change which schedule is plotted
    best_schedule = scored[0][1]
    plot_schedule(best_schedule, show_location=show_location)

EXCLUDE_PROFS = {""}

# basically a legacy variable but I don't want the code to break so don't delete
AVOID_PROFS = EXCLUDE_PROFS

if __name__ == "__main__":
    fall   = "fall.txt"
    winter = "winter.txt"
    summer = "summer.txt"

    # ────────────────────────────────────────────────────────────────
    # INPUT/ADJUSTMENTS
    # ----------------------------------------------------------------
    # COURSES        = {""}      # list‑of‑courses the student wants
    COURSES        = {""}
    TERM_FILE      = winter      # fall / winter / summer
    SHOW_LOCATION  = False      # ← set False to hide building + room
    # ────────────────────────────────────────────────────────────────

    courses = parse_input(COURSES, TERM_FILE)
    optimize_schedule(courses, show_location=SHOW_LOCATION)

# User Input Fields: Courses, Prof Exclusions, Summer/Fall/Winter term?