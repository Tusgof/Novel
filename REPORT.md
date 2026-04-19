# Project Report: Deep Sea Embers Translation Pipeline

**Report Generated**: วันอาทิตย์ที่ 19 เมษายน 2569 (April 19, 2026)
**Based on**: SUMMARY.md (as of April 2026)
**Scope**: Project status and operational metrics

## Executive Summary

The Deep Sea Embers translation pipeline is operating successfully with 8 chapters completed (44 blocks) and 10 additional chapters (ch009-ch018) in the current batch. The system has demonstrated production readiness through successful dry-run batches and maintains strict quality controls through glossary consistency, provider reliability measures, and automated validation gates.

## Progress Metrics

### Chapter Completion Status
| Chapter | Blocks | Status | Run ID | Output Location |
|---------|--------|--------|--------|-----------------|
| ch001 | 5 | ✅ Complete | run-ch001-clean-v4 | `05_Output/ch001/ch001.md` |
| ch002 | 6 | ✅ Complete | batch-ch002-ch003-v1 | `05_Output/ch002/ch002.md` |
| ch003 | 5 | ✅ Complete | batch-ch002-ch003-v1 | `05_Output/ch003/ch003.md` |
| ch004 | 6 | ✅ Complete | batch-ch004-ch008-v2 | `05_Output/ch004/ch004.md` |
| ch005 | 5 | ✅ Complete | batch-ch004-ch008-v2 | `05_Output/ch005/ch005.md` |
| ch006 | 6 | ✅ Complete | batch-ch004-ch008-v2 | `05_Output/ch006/ch006.md` |
| ch007 | 6 | ✅ Complete | batch-ch004-ch008-v2 | `05_Output/ch007/ch007.md` |
| ch008 | 5 | ✅ Complete | batch-ch004-ch008-v2 | `05_Output/ch008/ch008.md` |
| **Total** | **44** | **8/8 chapters** | **3 batches** | **All outputs exist** |

### Key Metrics (from SUMMARY.md)
- **Total blocks processed**: 44 blocks across 8 chapters
- **Failed blocks**: 0 in completed runs
- **Glossary terms approved**: 25+ key terms
- **Glossary terms deprecated/quarantined**: 50+ false positives/substrings

### Current Batch (V3.8 Controlled Rollout)
- **Batch ID**: `batch-ch009-ch018-v1`
- **Chapters**: ch009 through ch018 (10 chapters)
- **Status**: Glossary scan completed, approval gate completed
- **Approved term**: `瓦斯灯` = `โคมไฟแก๊ส` (gas lamp)
- **Rejected terms**: 29 generic/noisy/context-dependent terms
- **Execution plan**: **Staged execution** - ch009-ch013 first, verify outputs, then ch014-ch018
- **Current phase**: Ready for translation execution (V3.8 controlled rollout in progress)

## Quality Assurance Metrics

### Glossary Management
- **Approved terms**: 25+ key translation terms
- **Deprecated terms**: 50+ false positives/substrings in quarantine
- **Key fixes**: Longest-match algorithm prevents substring collisions (e.g., `乡号` vs `失乡号`)
- **Human gate**: Mandatory approval for all new terms
- **Recent approval**: `瓦斯灯` = `โคมไฟแก๊ส` (gas lamp) approved for current batch

### Provider Performance
| Provider | Role | Status | Fallback Strategy |
|----------|------|--------|-------------------|
| Gemini Pro | Literal translation, Glossary extraction | ✅ Operational | Wait/resume on capacity errors (no Claude fallback) |
| Claude Sonnet | Refinement, Glossary suggestion | ✅ Operational | Qwen DeepSeek Reasoner fallback |
| Qwen DeepSeek Reasoner | QA judge, Refinement fallback | ✅ Operational | Gemini Pro fallback only on provider failure |
| Local Python | Formatting | ✅ Operational | N/A |

**Provider Routing Policy**:
- `term_extraction`: Gemini Pro
- `term_suggestion`: Claude Sonnet  
- `literal_translation`: Gemini Pro
- `refinement`: Claude Sonnet (Qwen DeepSeek Reasoner fallback)
- `qa_judge`: Qwen DeepSeek Reasoner (Gemini Pro fallback only on provider failure)
- `formatting`: Local Python (Qwen configured but not used)

### Validation Results
- **Mojibake validation**: No wrong-script output detected
- **QA failures**: 0 failed blocks in completed runs
- **Formatting**: Quote-only lines removed, dialogue formatting preserved
- **Cross-chapter consistency**: Glossary terms maintained across all outputs

## System Health

### Pipeline Components
1. **✅ Fetch**: Piaotia adapter operational
2. **✅ Chunk**: ~600 Chinese characters per block
3. **✅ Glossary Scan**: Pre-batch term extraction
4. **✅ Human Approval**: Interactive glossary term approval
5. **✅ Literal Translation**: Gemini Pro with glossary
6. **✅ Refinement**: Claude Sonnet improves prose
7. **✅ QA**: Qwen DeepSeek Reasoner validates quality
8. **✅ Formatting**: Local Python for dialogue/quotes
9. **✅ Final Assembly**: Combine blocks into chapter Markdown

### Artifact Integrity
- **Source artifacts**: `03_Raw/` - Complete for all chapters
- **Work artifacts**: `04_Work/` - All block artifacts preserved
- **Output artifacts**: `05_Output/` - All final Markdown files exist
- **Ledger**: `06_Logs/` - Append-only audit trail maintained

## Operational Commands

### Status Checking
```powershell
# Check current batch status
novel-pipeline --config '.system/config.yaml' status --run-id batch-ch009-ch018-v1

# Verify completed chapters
python test_translation.py
python validate_fixes.py
```

### Recovery Operations
```powershell
# Resume interrupted run
novel-pipeline --config '.system/config.yaml' resume --run-id batch-ch009-ch018-v1

# Rerun specific block from stage
novel-pipeline --config '.system/config.yaml' rerun-block --run-id batch-ch004-ch008-v2 --block-id ch004-block-003 --from-stage qa
```

### Validation
```powershell
# Compile check
python -m compileall novel_pipeline

# Provider smoke tests
"Reply OK only" | claude -p --model sonnet
gemini -p "Reply OK only" --model pro
"Reply OK only" | qwen -m deepseek-reasoner
```

## Issues and Resolutions

### ✅ Resolved Issues
1. **Gemini capacity errors**: Wait/resume implemented, no silent Claude fallback
2. **Windows argv length**: Claude/Qwen use stdin to avoid argv length limits
3. **Glossary substring collisions**: Longest-match retrieval algorithm prevents false positives (e.g., `乡号` vs `失乡号`)
4. **Formatting quality**: Quote-only lines removed, non-dialogue quote stripping, sound-effect italics preserved
5. **Cross-chapter consistency**: Glossary terms maintained across all chapters
6. **Provider reliability**: Classification handles quota/capacity, timeout, auth failures
7. **Glossary retrieval**: Longest-match algorithm prevents substring false positives
8. **Windows compatibility**: Claude/Qwen use stdin to avoid argv length limits

### 🔄 Active Monitoring (from SUMMARY.md)
- Provider quota usage during batch runs
- Cross-chapter glossary consistency
- Formatting quality for dialogue and quotes
- QA failure recovery workflows

## Recommendations

### Immediate Actions
1. **Proceed with ch009-ch013 execution** as planned in V3.8 staged rollout
2. **Verify outputs** before proceeding to ch014-ch018
3. **Monitor provider quotas** during batch execution
4. **Continue V3.8 documentation updates** currently in progress

### Milestone Status
- **V3.7**: Production batch readiness (✅ Complete)
- **V3.8**: Documentation updates (🔄 In progress)
- **Future**: Scale to 5-chapter batches without manual intervention (as per SUMMARY.md)

### Future Improvements (aligned with SUMMARY.md)
1. **Batch progress reporting** for operator visibility
2. **Configurable cooldown** for provider capacity errors
3. **Enhanced Piaotia adapter** robustness
4. **Cross-chapter consistency verification** automation
5. **Scale to 5-chapter batches** without manual intervention (as per SUMMARY.md future milestone)

## Conclusion

The Deep Sea Embers translation pipeline is operating at production readiness level. All completed chapters (ch001-ch008) have passed validation checks, and the current batch (ch009-ch018) is proceeding according to the V3.8 controlled rollout plan. The system demonstrates robust glossary management, provider reliability, and quality assurance through multiple validation gates.

**Next checkpoint**: Completion of ch009-ch013 execution and verification before proceeding to ch014-ch018.