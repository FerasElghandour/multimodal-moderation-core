"""Offline example using the public implementation; see README for evidence scope."""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)

from moderation import Assessment,assess,decide,summarize
good=decide(Assessment('text',{'abuse':.1}))
bad=decide(Assessment('image',{'abuse':.8}))
failed=assess(b'synthetic','video',lambda p,m:1/0)
print(summarize([good,bad,decide(failed)]))
