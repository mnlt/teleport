#!/usr/bin/env python3
"""UX demo helper: restore backups created by _uxdemo-inject.py.

Run:  curl -sL https://raw.githubusercontent.com/mnlt/teleport/main/setup/_uxdemo-cleanup.py | python3
"""
import shutil
from pathlib import Path

H = Path.home()
CC = H / ".claude.json"
SL = H / ".claude" / "settings.local.json"
BAK_CC = H / ".claude.json.uxdemo"
BAK_SL = H / ".claude" / "settings.local.json.uxdemo"

if not BAK_CC.exists():
    print(f"⚠  no backup found at {BAK_CC} — was _uxdemo-inject.py run?")
    raise SystemExit(1)

shutil.move(str(BAK_CC), str(CC))
print(f"✓ restored {CC.name}")

if BAK_SL.exists():
    shutil.move(str(BAK_SL), str(SL))
    print(f"✓ restored {SL.name}")
else:
    print(f"· no settings.local.json backup to restore (wasn't present at inject time)")

print()
print("Demo cleaned up. Your original state is back.")
