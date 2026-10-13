import datetime

# Tap logs of Khoirunnisa
# Date, Check-in (Masuk), Check-out (Pulang)
logs = [
    ("01-05", "07:13:31", "16:15:37"),
    ("02-05", "07:05:43", "14:11:47"),
    ("03-05", None, None), # Libur
    ("04-05", "07:12:47", "16:16:32"),
    ("05-05", "13:58:39", "21:04:12"),
    ("06-05", "13:48:47", "21:04:18"),
    ("07-05", "20:47:10", "20:47:10"),
    ("08-05", "07:54:12", "16:30:17"),
    ("09-05", "07:14:18", "14:14:55"),
    ("10-05", None, None), # Libur
    ("11-05", "07:16:47", "14:12:47"),
    ("12-05", "13:56:46", "21:05:12"),
    ("13-05", "21:02:47", "21:02:47"),
    ("14-05", "07:14:16", "14:12:48"),
    ("15-05", "13:51:17", "21:04:37"),
    ("16-05", "14:12:41", "21:02:37"),
    ("17-05", None, None), # Libur
    ("18-05", "07:14:38", "14:15:28"),
    ("19-05", "13:54:39", "21:05:27"),
    ("20-05", "20:56:22", "20:56:22"),
    ("21-05", "07:51:17", "16:30:17"),
    ("22-05", "07:13:38", "14:12:47"),
    ("23-05", "13:52:16", "21:05:27"),
    ("24-05", None, None), # Libur
    ("25-05", "20:57:31", "20:57:31"),
    ("26-05", "07:54:12", "16:30:17"),
    ("27-05", "07:13:17", "14:16:47")
]

# We need to find the shift schedule of Khoirunnisa for May 2026.
# Since she is "RSUD shift", her shift for each day could be:
# Pagi (P): 07:00 to 14:00
# Siang (S): 14:00 to 21:00
# Malam (M): 21:00 to 07:00 (next day)
# Libur (L): No work
# Let's find which days have what shift.
# First, let's examine standard times for shifts in seconds:
# Pagi: start = 7*3600 (25200), end = 14*3600 (50400)
# Siang: start = 14*3600 (50400), end = 21*3600 (75600)
# Malam: start = 21*3600 (75600), end = (24 + 7)*3600 (111600)
# Default (Dinas): start = 7.5*3600 (27000) or 8*3600 (28800)

target_wm = 34 * 3600 + 6 * 60 + 45 # 122805 s
target_wp = 13 * 3600 + 31 * 60 + 19 # 48679 s

print(f"Target Lateness (TTWM-TI): {target_wm}s ({34*3600 + 6*60 + 45}s)")
print(f"Target Early (TTWP-TI): {target_wp}s ({13*3600 + 31*60 + 19}s)")

# Let's calculate for each day if we assign shifts:
# Let's see what happens if we assign shifts based on the actual hours:
# P: Day 1, 2, 4, 9, 11, 14, 18, 22, 27
# S: Day 5, 6, 12, 15, 16, 19, 23
# M: Day 7, 13, 20, 25 (Single taps around 21:00)
# Non-Shift (D): Day 8, 21, 26 (Check-ins at 07:54, 07:51, 07:54 and check-outs at 16:30)

# Let's check lateness and early checkouts for this configuration.
# We will calculate for each day:
# lateness = max(0, check_in - start_time)
# early_checkout = max(0, end_time - check_out)

shifts = {}
for date, msk, plg in logs:
    if not msk:
        continue
    # Let's infer shift code from date:
    day = int(date.split('-')[0])
    if day in [1, 2, 4, 9, 11, 14, 18, 22, 27]:
        shifts[date] = 'P'
    elif day in [5, 6, 12, 15, 16, 19, 23]:
        shifts[date] = 'S'
    elif day in [7, 13, 20, 25]:
        shifts[date] = 'M'
    elif day in [8, 21, 26]:
        shifts[date] = 'D' # Dinas / Non-Shift

# Let's calculate:
tot_wm = 0
tot_wp = 0

print("\nDetail per Day with Inferred Shifts:")
for date, msk, plg in logs:
    if not msk:
        continue
    sh = shifts[date]
    h_in, m_in, s_in = map(int, msk.split(':'))
    h_out, m_out, s_out = map(int, plg.split(':'))
    
    sec_in = h_in * 3600 + m_in * 60 + s_in
    sec_out = h_out * 3600 + m_out * 60 + s_out
    
    # Target hours
    if sh == 'P':
        start_time = 7 * 3600
        end_time = 14 * 3600
    elif sh == 'S':
        start_time = 14 * 3600
        end_time = 21 * 3600
    elif sh == 'M':
        start_time = 21 * 3600
        # Malam checkout is next day morning, but on same day tap, it's before end_time
        # Since check-out in logs is same day, let's see how system calculates it.
        # If it treats the same day tap as checkout, then:
        end_time = (24 + 7) * 3600 # 31 * 3600
    elif sh == 'D':
        # Default / Dinas
        start_time = 7.5 * 3600 # 07:30
        end_time = 16 * 3600 # 16:00
        
    lat = max(0, sec_in - start_time)
    
    if sh == 'M':
        # If check-in and check-out are both 20:56:22 (on day 20)
        # sec_in = 20:56:22 (75382). start_time = 21:00:00 (75600). So not late!
        # sec_out = 20:56:22 (75382). end_time = 31*3600 (111600).
        # early = end_time - sec_out = 111600 - 75382 = 36218s (10h 3m 38s!)
        early = max(0, end_time - sec_out)
    else:
        early = max(0, end_time - sec_out)
        
    print(f"Date {date} (Shift {sh}): In {msk} (late {lat}s), Out {plg} (early {early}s)")
    tot_wm += lat
    tot_wp += early

def format_seconds(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

print(f"\nTotal Lateness (TTWM-TI): {format_seconds(tot_wm)} ({tot_wm}s)")
print(f"Total Early (TTWP-TI): {format_seconds(tot_wp)} ({tot_wp}s)")
