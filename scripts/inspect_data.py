import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import data

print("Checking get_all_members() return value:")
members = data.get_all_members()
for m in members:
    print(m)
