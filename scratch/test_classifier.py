def classify_times(times):
    scores = {'P': 0, 'S': 0, 'M': 0, 'Non-Shift': 0}
    
    has_morning_entry = any(5 <= (t/3600.0) <= 9.5 for t in times)
    has_afternoon_entry = any(12.5 <= (t/3600.0) <= 15.5 for t in times)
    has_night_entry = any(19.5 <= (t/3600.0) <= 23.5 for t in times)
    
    has_afternoon_exit = any(13.5 <= (t/3600.0) <= 16.5 for t in times)
    has_evening_exit = any(20.5 <= (t/3600.0) <= 22.5 for t in times)
    
    # Pagi
    if has_morning_entry and has_afternoon_exit:
        scores['P'] += 10
    elif has_morning_entry:
        scores['P'] += 3
    elif has_afternoon_exit:
        scores['P'] += 3
        
    # Siang
    if has_afternoon_entry and has_evening_exit:
        scores['S'] += 10
    elif has_afternoon_entry:
        scores['S'] += 3
    elif has_evening_exit:
        scores['S'] += 3
        
    # Malam
    if has_night_entry:
        scores['M'] += 8
    if has_morning_entry and not has_afternoon_exit and not has_afternoon_entry:
        scores['M'] += 2
        
    # Non-Shift (Standard Office Hour)
    has_std_entry = any(7 <= (t/3600.0) <= 9 for t in times)
    has_std_exit = any(15.5 <= (t/3600.0) <= 18 for t in times)
    if has_std_entry and has_std_exit:
        scores['Non-Shift'] += 12
        
    best_shift = max(scores, key=scores.get)
    if scores[best_shift] == 0:
        return {"status": "review_manual", "reason": "unknown_shift", "message": "Review Manual: Pola tapping tidak cocok dengan shift P/S/M/D."}
    elif best_shift == 'Non-Shift':
        detected_shift = 'D'
    else:
        detected_shift = best_shift
        
    return {"status": "success", "detected_shift": detected_shift, "scores": scores}

# Test cases
def time_to_sec(t_str):
    h, m, s = map(int, t_str.split(':'))
    return h * 3600 + m * 60 + s

tests = [
    ("Standard Office Hours (07:15 - 16:15)", ["07:13:31", "16:15:37"]),
    ("Standard Office Hours (07:54 - 16:30)", ["07:54:12", "16:30:17"]),
    ("Pagi Shift (07:15 - 14:15)", ["07:13:31", "14:11:47"]),
    ("Siang Shift (13:58 - 21:04)", ["13:58:39", "21:04:12"]),
    ("Malam Shift (21:02 check-in)", ["21:02:47"]),
    ("Single tap at weird hour (12:00)", ["12:00:00"]),
]

for name, t_list in tests:
    times = [time_to_sec(t) for t in t_list]
    res = classify_times(times)
    print(f"Test: {name}")
    print(f"  Inputs: {t_list}")
    print(f"  Result: {res}")
    print("-" * 50)
