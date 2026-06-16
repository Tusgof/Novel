import subprocess
import sys
import time

def test_model(model_id):
    args = ["qwen", "-m", model_id]
    try:
        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = proc.communicate(input="Reply exactly: OK", timeout=10)
        print(f"Model {model_id}: returncode={proc.returncode}, stdout={repr(stdout)}, stderr={repr(stderr)}")
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print(f"Model {model_id}: timeout")
    except Exception as e:
        print(f"Model {model_id}: error {e}")

if __name__ == "__main__":
    test_model("deepseek-reasoner")
    test_model("elephant")
    test_model("deepseek-chat")