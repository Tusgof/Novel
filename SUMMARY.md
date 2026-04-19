# Project Summary: Deep Sea Embers Translation Pipeline

## Current Status (April 2026)

### Completed Chapters
- **ch001**: Complete (5 blocks) - `run-ch001-clean-v4`
- **ch002**: Complete (6 blocks) - `batch-ch002-ch003-v1`
- **ch003**: Complete (5 blocks) - `batch-ch002-ch003-v1`
- **ch004-ch008**: Complete (28 blocks total) - `batch-ch004-ch008-v2` (production dry-run)

### Current Execution
- **V3.8 controlled rollout in progress**:
  - `batch-ch009-ch018-v1` glossary scan completed
  - Glossary approval gate completed
  - Approved new term: `瓦斯灯` = `โคมไฟแก๊ส`
  - Rejected 29 generic/noisy/context-dependent terms
  - Chapters ch009-ch018 approved for translation
  - Staged execution: ch009-ch013 first, verify, then ch014-ch018

### Key Metrics
- **Total blocks processed**: 44 blocks across 8 chapters
- **Failed blocks**: 0 in completed runs
- **Glossary terms approved**: 25+ key terms
- **Glossary terms deprecated/quarantined**: 50+ false positives/substrings

### Recent Fixes
1. **Glossary retrieval**: Longest-match algorithm prevents substring false positives (e.g., `乡号` vs `失乡号`)
2. **Formatting**: Quote-only lines removed, non-dialogue quote stripping, sound-effect italics preserved
3. **Provider reliability**: Classification handles quota/capacity, timeout, auth failures
4. **Windows compatibility**: Claude/Qwen use stdin to avoid argv length limits

### Pipeline Health
- **Literal translation**: Gemini Pro (capacity errors wait/resume, no Claude fallback)
- **Refinement**: Claude Sonnet primary, Qwen DeepSeek Reasoner fallback
- **QA judge**: Qwen DeepSeek Reasoner primary, Gemini Pro fallback only on provider failure
- **Formatting**: Local Python (Qwen configured but not used)
- **Glossary extraction**: Gemini Pro
- **Glossary suggestion**: Claude Sonnet

### Next Milestones
- **V3.7**: Production batch readiness (complete)
- **V3.8**: Documentation updates (in progress)
- **Future**: Scale to 5-chapter batches without manual intervention

## System Architecture

### Core Components
1. **Pipeline stages**: Fetch → Chunk → Glossary Scan → Human Approval → Literal Translation → Refinement → QA → Formatting → Final Assembly
2. **Artifact storage**: 
   - `03_Raw/`: Source content and manifests
   - `04_Work/`: Block artifacts (literal/refined/QA/formatted)
   - `05_Output/`: Final chapter Markdown
   - `06_Logs/`: Append-only ledger
3. **Glossary management**:
   - `01_Glossary/`: Approved terms
   - `01_Glossary/quarantine/`: Deprecated terms
   - Human-in-the-loop mandatory for term approval

### Quality Gates
- **Mojibake validation**: Prevents wrong-script output
- **QA hybrid rules + AI judge**: Validates translation quality
- **Provider output classification**: Never commits quota/error/meta text as successful translation
- **Cross-chapter consistency**: Glossary terms maintained across all chapters

## Operational Status

### Running Commands
```powershell
# Check status
novel-pipeline --config '.system/config.yaml' status --run-id batch-ch009-ch018-v1

# Resume execution
novel-pipeline --config '.system/config.yaml' resume --run-id batch-ch009-ch018-v1

# Rerun specific block
novel-pipeline --config '.system/config.yaml' rerun-block --run-id batch-ch004-ch008-v2 --block-id ch004-block-003 --from-stage qa
```

### Validation Commands
```powershell
# Compile check
python -m compileall novel_pipeline

# Test translation
python test_translation.py

# Validate fixes
python validate_fixes.py
```

## Known Issues & Resolutions

### Resolved Issues
1. **Gemini 429/No Capacity**: Wait and resume implemented, no silent Claude fallback
2. **Claude Quota**: Provider layer classifies quota as unusable output
3. **Windows Encoding**: `$env:PYTHONIOENCODING='utf-8'` set before commands
4. **Glossary Drift**: Source term presence verified, approved Thai term exists

### Active Monitoring
- Provider quota usage during batch runs
- Cross-chapter glossary consistency
- Formatting quality for dialogue and quotes
- QA failure recovery workflows