def extr_numb( s):
    if is_range(s):
        a, b = map(int, s.split('-'))
        return [a, b]
    return None
def is_range( s):
    parts = s.split('-')
    if len(parts) == 2:
        return parts[0].isdigit() and parts[1].isdigit()
    return False
print(extr_numb('4-7'))