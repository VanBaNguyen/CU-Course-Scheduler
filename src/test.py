#!/usr/bin/env python
# ─────────────────────────────────────────────────────────────────────────────
# test_performance.py  –  benchmark parse_input + optimize_schedule
# ─────────────────────────────────────────────────────────────────────────────

import argparse
import statistics as st
import time

import matplotlib.pyplot as plt
plt.show = lambda *a, **k: None          # suppress all plot windows

from parsing          import parse_input
from optimal_schedule import optimize_schedule


COURSE_SET = {"COMP 2804", "COMP 2406", "COMP 3000", "COMP 2404", "GEOM 2005"}
TERM_FILE  = "fall.txt"


def timed_call(fn, *args, **kwargs):
    t0 = time.perf_counter()
    fn(*args, **kwargs)
    return time.perf_counter() - t0


def run_benchmark(reps: int):
    results = []

    for _ in range(reps):
        # Parse once
        t_parse = timed_call(parse_input, COURSE_SET, TERM_FILE)
        courses = parse_input(COURSE_SET, TERM_FILE)   # reuse parsed data

        # Optimize (plot suppressed by plt.show stub)
        t_opt = timed_call(optimize_schedule, courses, show_location=False)

        results.append((t_parse, t_opt, t_parse + t_opt))

    return results


def main():
    parser = argparse.ArgumentParser("Performance test for scheduler")
    parser.add_argument("--reps", type=int, default=100)
    args = parser.parse_args()

    runs = run_benchmark(args.reps)
    p_times, o_times, tot_times = zip(*runs)

    def line(label, data):
        print(f"{label:14s}  "
              f"min {min(data):7.4f}s  "
              f"avg {st.mean(data):7.4f}s  "
              f"max {max(data):7.4f}s")

    print("\n=== Scheduler Performance ===")
    line("parse_input", p_times)
    line("optimize",    o_times)
    line("total",       tot_times)
    print(f"reps: {args.reps}, courses: {len(COURSE_SET)}, term: {TERM_FILE}\n")


if __name__ == "__main__":
    main()
