import subprocess
import sys
import time

cmd = ["qwen", "-m", "deepseek-reasoner"]
print("Running:", cmd)
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
)
try:
    stdout, stderr = proc.communicate(input="Reply exactly: OK", timeout=10)
    print("Return code:", proc.returncode)
    print("Stdout:", repr(stdout))
    print("Stderr:", repr(stderr))
except subprocess.TimeoutExpired:
    print("Timeout")
    proc.kill()
    stdout, stderr = proc.communicate()
    print("Killed")
except Exception as e:
    print("Error:", e)