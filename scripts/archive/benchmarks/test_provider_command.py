import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path
import yaml
from novel_pipeline.providers.base import build_provider_spec, ProviderRunner
from novel_pipeline.types import ProviderRequest

providers_yaml = Path(__file__).parent.parent / ".system" / "providers.yaml"
with open(providers_yaml, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

qwen_config = config.get("providers", {}).get("qwen", {})
print("qwen_config:", qwen_config)
spec = build_provider_spec("qwen", qwen_config)
print("spec:", spec)
print("spec.executable:", spec.executable)
print("spec.model_flag:", spec.model_flag)
print("spec.model_position:", spec.model_position)
print("spec.prompt_flag:", spec.prompt_flag)
print("spec.prompt_position:", spec.prompt_position)
print("spec.prompt_transport:", getattr(spec, 'prompt_transport', 'argv'))

runner = ProviderRunner(spec)
request = ProviderRequest(prompt="Reply exactly: OK", provider="qwen", model="deepseek-reasoner")
command = runner.build_command(request)
print("command:", command)