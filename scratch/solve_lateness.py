from itertools import combinations
import datetime

# Clock-in times
in_times = [
    ("04-05", "07:38:28"), # h=7, m=38, s=28
    ("05-05", "16:13:10"),
    ("06-05", "08:17:03"),
    ("07-05", "08:00:34"),
    ("08-05", "07:56:51"),
    ("11-05", "07:34:12"),
    ("12-05", "07:57:49"),
    ("13-05", "16:10:56"),
    ("18-05", "07:39:55"),
    ("19-05", "08:02:00"),
    ("20-05", "08:06:03"),
    ("21-05", "08:00:22"),
    ("22-05", "07:53:46"),
    ("25-05", "07:51:17"),
    ("26-05", "07:47:31")
]

target_seconds = 3 * 3600 + 55 * 60 + 5 # 14105 seconds

# Let's parse time strings to seconds from midnight
in_secs = []
for dt, tm in in_times:
    h, m, s = map(int, tm.split(':'))
    in_secs.append((dt, h * 3600 + m * 60 + s))

print(f"Target seconds: {target_seconds} (03:55:05)")

# Let's search for a combination of days and a base start time that gives exactly target_seconds.
# The base start time is usually a standard time, e.g. 07:30 (27000s), 07:45 (27900s), 08:00 (28800s),
# or maybe there are multiple shifts!
# Wait! Let's check what shifts Muhamad Lutfi had.
# If he has shift Pagi (P), does shift Pagi start at 07:30 or 07:00?
# In otomatisasi_api.py line 194, shift pagi target masuk is 07:00:00!
# If target masuk is 07:00:00, then let's see.
# Let's run a search.

# We will try all possible base times from 07:00:00 to 08:30:00 (step 1 second)
# and all possible subsets of in_secs (from length 1 to 15)
# to see if the sum of max(0, clock_in - base_time) equals target_seconds.
# To make it faster, we can group by base time.

found = False
for base_h in range(7, 9):
    for base_m in range(0, 60):
        for base_s in range(0, 60):
            base_sec = base_h * 3600 + base_m * 60 + base_s
            
            # Calculate lateness for each day
            latenesses = []
            for dt, t_sec in in_secs:
                lat = max(0, t_sec - base_sec)
                latenesses.append((dt, lat))
                
            # Now find if any subset of latenesses sums to target_seconds
            # Since n=15, 2^15 = 32768, which is very small and fast to check!
            for r in range(1, len(in_secs) + 1):
                for comb in combinations(latenesses, r):
                    s = sum(c[1] for c in comb)
                    if s == target_seconds:
                        print(f"MATCH FOUND!")
                        print(f"Base Time: {base_h:02d}:{base_m:02d}:{base_s:02d}")
                        print("Days included:")
                        for dt, lat in comb:
                            if lat > 0:
                                # Find original time
                                orig_time = [tm for d, tm in in_times if d == dt][0]
                                print(f"  - {dt}: {orig_time} -> late by {lat}s ({lat//60}m {lat%60}s)")
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if found:
            break
    if found:
        break

if not found:
    print("No simple single-base-time match found. Checking if there are different base times for different days (e.g. Mon-Thu vs Fri, or Shift Pagi vs Shift Normal).")
    # Let's check Mon-Thu vs Fri:
    # Monday to Thursday (Mon: 04, 11, 18, 25; Tue: 05, 12, 19, 26; Wed: 06, 13, 20; Thu: 07, 21)
    # Friday (08, 15, 22)
    # In SPOT, standard Monday-Thursday start is 07:30 (or is it?), Friday is 07:30 (or is it?).
    # What if Monday-Thursday start is 07:30, Friday is 07:30? Let's check if the system calculates it as:
    # Let's test combinations where we have two base times: base_weekday and base_friday.
