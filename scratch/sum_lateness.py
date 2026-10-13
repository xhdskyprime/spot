from datetime import datetime, timedelta

def to_seconds(h, m, s):
    return h * 3600 + m * 60 + s

def format_seconds(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# Clock-in times
in_times = [
    ("04-05-2026", "07:38:28"),
    ("05-05-2026", "16:13:10"), # wait, what about this?
    ("06-05-2026", "08:17:03"),
    ("07-05-2026", "08:00:34"),
    ("08-05-2026", "07:56:51"),
    ("11-05-2026", "07:34:12"),
    ("12-05-2026", "07:57:49"),
    ("13-05-2026", "16:10:56"), # wait, what about this?
    ("18-05-2026", "07:39:55"),
    ("19-05-2026", "08:02:00"),
    ("20-05-2026", "08:06:03"),
    ("21-05-2026", "08:00:22"),
    ("22-05-2026", "07:53:46"),
    ("25-05-2026", "07:51:17"),
    ("26-05-2026", "07:47:31")
]

# Case 1: Standard work start is 07:30:00.
# Any time after 07:30 is late.
# For days like 05-05 and 13-05, check-in is 16:13 and 16:10. Are they counted as late or empty?
# Wait! Let's check if the system counts them as late (since 16:13 > 07:30) or if they are excluded because there is no checkout (or they are considered "Datang Kosong" which has 0 lateness but is a different issue, or maybe the shift on those days was actually Libur or something?).
# Let's write a loop to test different combinations.

print("--- Standard Start = 07:30:00 ---")
tot_sec = 0
for dt, tm in in_times:
    h, m, s = map(int, tm.split(':'))
    sec = to_seconds(h, m, s)
    limit = to_seconds(7, 30, 0)
    if sec > limit:
        # If it's a day like 05-05 and 13-05 where check-in is late afternoon,
        # does it count as late?
        diff = sec - limit
        print(f"{dt}: {tm} -> Late by {format_seconds(diff)} ({diff} s)")
        tot_sec += diff
print(f"Total: {format_seconds(tot_sec)}")

print("\n--- Excluding 05-05 and 13-05 ---")
tot_sec_ex = 0
for dt, tm in in_times:
    if dt in ["05-05-2026", "13-05-2026"]:
        continue
    h, m, s = map(int, tm.split(':'))
    sec = to_seconds(h, m, s)
    limit = to_seconds(7, 30, 0)
    if sec > limit:
        diff = sec - limit
        print(f"{dt}: {tm} -> Late by {format_seconds(diff)}")
        tot_sec_ex += diff
print(f"Total: {format_seconds(tot_sec_ex)}")
