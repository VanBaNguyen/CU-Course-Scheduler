import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from collections import defaultdict
from datetime import datetime, time
from itertools import combinations
from itertools import product
from parsing import parse_input
matplotlib.use("Agg") # Use non-interactive backend for plotting

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DAY_TO_INDEX = {day: i for i, day in enumerate(DAYS)}
ONLINE_BUILDING = "ON"
ONLINE_ROOM     = "LINE"

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
        (has_number, course_code, section,
         prof, days_str, time_str, building, room) = item

        if prof in ("No No", "Yes Yes", "term course"):
            prof = "N/A"

        #  first find out whether this is an ON-LINE offering
        is_online = (building == ONLINE_BUILDING and room == ONLINE_ROOM)

        # normalise the raw strings
        days_trim  = days_str.strip()
        time_trim  = time_str.strip()

        # (a) no day / time given  → asynchronous ON-LINE or “Unknown”
        if days_trim in ("", "Unknown"):
            days = []                # keep it empty so it never plots
        else:
            days = parse_days(days_trim)

        if time_trim in ("", "Unknown"):
            start, end = None, None  # unscheduled (async) slot
        else:
            start, end = parse_time_range(time_trim)
            if start is None or end is None:
                # bad clock format → skip *unless* it’s ON-LINE async
                if not is_online:                      # offline garbage
                    print(f"⚠️  Skipping invalid time: {time_trim}"
                          f" (Course: {course_code} {section})")
                    continue
                start, end = None, None

        # ---------------- online flags ----------------
        is_async             = is_online and start is None and end is None
        is_online_scheduled  = is_online and not is_async

        #build the slot
        slot = {
            'has_number': has_number,
            'course':     course_code,
            'section':    section,
            'prof':       prof,
            'days':       days,
            'start':      start,
            'end':        end,
            'building':   building,
            'room':       room,
            'original':   item,
            'is_online':            is_online,
            'is_async':             is_async,
            'is_online_scheduled':  is_online_scheduled,
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

    active_days = 0
    for day, slots in daily_slots.items():
        if any(not s['is_online_scheduled'] for s in slots):
            active_days += 1

        # gaps are still relevant whenever >=2 scheduled things share that day
        slots.sort(key=lambda x: x['start'])
        for i in range(len(slots) - 1):
            gap = (datetime.combine(datetime.today(), slots[i + 1]['start']) -
                   datetime.combine(datetime.today(), slots[i    ]['end']))
            total_gap_minutes += max(0, gap.total_seconds() / 60)

    return active_days * 1000 + total_gap_minutes + early_penalty + prof_penalty

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

def plot_schedule(schedule, *, show_location=True, dark_mode=False, outfile=None):
    # does this course appear with an OK professor anywhere?
    has_good_prof = {s['course']: (s['prof'] not in EXCLUDE_PROFS)
                     for s in schedule if s['prof'] not in EXCLUDE_PROFS}
    
    async_courses = [] 

    # ----------------------------------------------------------------
    # colours & style
    # ----------------------------------------------------------------
    if dark_mode:
        plt.style.use("dark_background")
        bg_colour      = "#111111"
        text_colour    = "white"
        normal_colour  = "#3b78ff"
        forced_colour  = "#c94c4c"
        online_colour  = "lightgreen"
        grid_kwargs    = dict(color="#444444", linestyle="--",
                              linewidth=0.6, alpha=0.25)
    else:
        bg_colour      = "white"
        text_colour    = "black"
        normal_colour  = "skyblue"
        forced_colour  = "lightcoral"
        online_colour  = "lightgreen"
        grid_kwargs    = dict(color="black", linestyle="--",
                              linewidth=0.8, alpha=0.4)

    fig, ax = plt.subplots(figsize=(12, 9), facecolor=bg_colour)   # ← was (10, 8)
    ax.set_facecolor(bg_colour)

    # grid & axes -----------------------------------------------------
    ax.set_xlim(0, 5)
    ax.set_ylim(8, 22)
    ax.invert_yaxis()

    ax.set_xticks(range(5))
    ax.set_xticklabels(DAYS, color=text_colour)
    ax.set_yticks(range(8, 23))
    ax.set_yticklabels([f"{h:02d}:00" for h in range(8, 23)], color=text_colour)

    ax.set_axisbelow(True)          # make sure grid stays *under* rectangles
    ax.grid(True, **grid_kwargs)

    # slots -----------------------------------------------------------
    for slot in schedule:
        # A-sync ON-LINE: skip plotting but remember the course
        if slot['is_online'] and not slot['is_online_scheduled']:
            async_courses.append(slot['course'])      # or f"{slot['course']} {slot['section']}"
            continue

        # anything else that still has no time (rare offline “Unknown”) – ignore
        if slot['start'] is None or slot['end'] is None:
            continue

        course       = f"{slot['course']} {slot['section']}"
        start_hour   = slot['start'].hour + slot['start'].minute / 60
        end_hour     = slot['end'].hour   + slot['end'].minute   / 60
        duration     = end_hour - start_hour

        # colour selection ‑‑ order matters
        if slot['prof'] in EXCLUDE_PROFS and not has_good_prof.get(slot['course']):
            fill_colour = forced_colour
        elif slot['is_online_scheduled']:
            fill_colour = online_colour
        else:
            fill_colour = normal_colour

        for day in slot['days']:
            if day not in DAY_TO_INDEX:
                continue
            x = DAY_TO_INDEX[day]
            rect = patches.Rectangle((x, start_hour), 0.95, duration,
                                     color=fill_colour,
                                     edgecolor=text_colour,
                                     linewidth=1.2)
            ax.add_patch(rect)

            if slot['is_online']:
                location = "Online (Zoom)"
            else:
                location = f"{slot['building']}\nRoom: {slot['room']}".strip()

            if show_location and location not in ("", "Unknown"):
                label = f"{course}\n{slot['prof']}\n{location}"
            else:
                label = f"{course}\n{slot['prof']}"

            ax.text(x + 0.02, start_hour + duration / 2,
                    label, va="center", ha="left",
                    fontsize=9, color=text_colour)
            
    # ── AFTER the rectangles are done ─────────────────────────
    ax.set_title("Your Optimal Weekly Schedule", color=text_colour)

    plt.tight_layout(rect=[0, 0.07, 1, 1])

    if async_courses:
        label = "ONLINE ASYNC COURSES: " + ", ".join(sorted(set(async_courses)))
        fig.text(0.01, 0.02,                       # x=1 % from left, y=2 % up
                 label,
                 ha="left", va="bottom",
                 fontsize=11, color=text_colour)
        
    # Get the absolute path to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set up the schedules directory parallel to 'src' (project root / schedules)
    project_root = os.path.dirname(script_dir)
    save_dir = os.path.join(project_root, "schedules")
    os.makedirs(save_dir, exist_ok=True)       # create if it’s missing

    # save only if caller asks
    if outfile is not None:
        # Remove any leading "schedules/" or os.sep from outfile
        outfile_rel = outfile
        if outfile_rel.startswith("schedules" + os.sep):
            outfile_rel = outfile_rel[len("schedules" + os.sep):]
        elif outfile_rel.startswith("schedules/"):
            outfile_rel = outfile_rel[len("schedules/"):]
        outfile_rel = outfile_rel.lstrip(os.sep)

        outfile_path = os.path.join(save_dir, outfile_rel)
        os.makedirs(os.path.dirname(outfile_path), exist_ok=True)
        fig.savefig(outfile_path, dpi=300, bbox_inches="tight")
        print(f"✅  Saved   {outfile_path}")


    plt.show()

# Main function
def optimize_schedule(course_list, *, show_location=True, dark_mode=False):
    slots          = build_slots(course_list)
    course_groups  = group_by_course(slots)
    valid_schedules = generate_valid_schedules(course_groups)

    if not valid_schedules:
        print("No valid schedules found.")
        return

    scored = sorted(
        ((score_schedule(s), s) for s in valid_schedules),
        key=lambda x: x[0]
    )

    display_top_schedules(scored, top_n=3)

    # make a run folder inside ../schedules/ (parallel to src)
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    root_dir_abs = os.path.join(project_root, "schedules")
    ts           = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir_rel  = os.path.join("schedules", ts)
    run_dir_abs  = os.path.join(root_dir_abs, ts)
    print(f"\n📂  Saving plots in {run_dir_abs}\n")

    # plot & save the 3 best schedules
    for idx, (score, sched) in enumerate(scored[:3], start=1):
        fname   = f"schedule{idx}_{int(score)}.png"
        outfile = os.path.join(run_dir_rel, fname)
        plot_schedule(sched,
                      show_location=show_location,
                      dark_mode=dark_mode,
                      outfile=outfile)

EXCLUDE_PROFS = {}

# basically a legacy variable but I don't want the code to break so don't delete
AVOID_PROFS = EXCLUDE_PROFS

if __name__ == "__main__":
    fall   = "fall.txt"
    winter = "winter.txt"
    summer = "summer.txt"

    # ────────────────────────────────────────────────────────────────
    # INPUT/ADJUSTMENTSß
    # ----------------------------------------------------------------

    COURSES = {""}
    TERM_FILE      = fall
    SHOW_LOCATION  = True        # ← set False to hide building + room
    DARK_MODE      = False
    # ────────────────────────────────────────────────────────────────

    courses = parse_input(COURSES, TERM_FILE)
    optimize_schedule(courses,
                      show_location=SHOW_LOCATION,
                      dark_mode=DARK_MODE)

# User Input Fields: Courses, Prof Exclusions, Summer/Fall/Winter term, Show Location (y/n), Dark Mode (y/n)