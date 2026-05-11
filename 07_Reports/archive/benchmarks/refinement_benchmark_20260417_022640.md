# Refinement Model Benchmark Report
**Timestamp:** 20260417_022640
**Generated:** 2026-04-17 02:51:10
**Blocks tested:** ch004-block-002, ch005-block-003, ch006-block-001

## 1. Executive Summary

- **Best overall candidate:** **claude_sonnet** (3/3 successful, best prose quality)
- **Best fidelity candidate:** **qwen_deepseek-reasoner** (preserved critical reactions in ch004-block-002 that Claude omitted)
- **Safest candidate for fidelity:** **qwen_deepseek-reasoner** (passed omission trap check)
- **Best prose candidate:** **claude_sonnet** (more polished literary Thai)
- **Recommended fallback policy:** Keep Claude primary for prose quality, but implement omission trap validation. Use Qwen as fallback for capacity or for blocks with known omission traps. GPT candidates unavailable.

## 2. Scope

- **Blocks tested:** 3
  - ch004-block-002: ch004
  - ch005-block-003: ch005
  - ch006-block-001: ch006
- **Candidate models tested:** 4
  - claude_sonnet: 3/3 successful
  - qwen_deepseek-reasoner: 2/3 successful (failed ch005-block-003)
  - codex_gpt-5.4: 0/3 successful (provider failure)
  - codex_gpt-5.4-mini: 0/3 successful (provider failure)
- **Provider commands used:** as per provider specs in config
- **Missing candidates:** GPT-5.4, GPT-5.4-mini (provider configured but CLI failed), GPT-4.1 (not supported by Codex with ChatGPT account)

## 3. Per-Block Results

### Block ch004-block-002

**Chapter:** ch004
**Source preview:** 幽绿的火焰在身上熊熊燃烧，血肉与骨骼在烈焰中化作半透明的灵体，邓肯在这流火中执掌着失乡号的船舵，而他的感知则仿佛顺着火焰一路蔓延出去，最终蔓延到了整艘舰船。
原来，它根本不需要船员。
失乡号自可扬帆，只需船长掌舵，它随时可以起航。
当幽绿火焰腾空而起的瞬间，邓肯陷入了短暂的慌乱，但在过去几天的探索中他已经在这艘船上见到了不止一次超自然现象，这些经历让他强行镇定下来，并在那最关键的几秒钟内没有松开手中的舵轮。
现在，他终于确定这火焰应该是某种对自己无害的“力量”——姑且不论之后自己的身体是否还能恢复过来，最起码现在看着，这火焰的力量在帮助自己掌控脚下这艘幽灵船。
脑海中的欢呼海啸声渐渐褪去了，邓...

| Candidate | Provider | Model | Success | Validation | QA Overall Usability | Recommendation |
|-----------|----------|-------|---------|------------|----------------------|----------------|
| claude_sonnet | claude | sonnet | True | no Chinese, no meta | N/A | N/A |
| codex_gpt-5.4-mini | codex | gpt-5.4-mini | False | failed | N/A | N/A |
| codex_gpt-5.4 | codex | gpt-5.4 | False | failed | N/A | N/A |
| qwen_deepseek-reasoner | qwen | deepseek-reasoner | True | no Chinese, no meta | N/A | N/A |

**Best candidate:** claude_sonnet (but failed omission trap, Qwen passed fidelity check)

**Special checks:**
- claude_sonnet: goat head quiet = False, Duncan speechless = False
- qwen_deepseek-reasoner: goat head quiet = True, Duncan speechless = True

---

### Block ch005-block-003

**Chapter:** ch005
**Source preview:** 那庞大的阴影碾压而至，白橡木号上的每一个人都看到了这足以令他们铭记一生的瞬间。
那是看上去古老而充满威仪的三桅战船——在这个蒸汽船已经不再稀奇的年代，那从浓雾中浮现的风帆战船古老的仿佛从一个世纪前的油画中走出来一般，它的桅杆高耸，船舷陡峭，漆黑的木质船壳上燃烧着亡魂般的绿色火光，巨大的帆在虚无中鼓动起来，帆上凝聚着嘶吼的幻象与层层烈焰——此等场景，哪怕是在可怕的无垠海上，也只有最恐怖的海难传说中才会出现。
“要撞上了！！！”
有船员大声惊呼起来，这些在海上讨生活的，以勇悍粗鲁出名的人在面对一艘如此庞然大物的时候也不免会失了方寸，他们呼喊着，奔跑着，有的尝试在甲板上寻找躲避之处，有的抓紧了身边一...

| Candidate | Provider | Model | Success | Validation | QA Overall Usability | Recommendation |
|-----------|----------|-------|---------|------------|----------------------|----------------|
| claude_sonnet | claude | sonnet | True | no Chinese, no meta | N/A | N/A |
| codex_gpt-5.4-mini | codex | gpt-5.4-mini | False | failed | N/A | N/A |
| codex_gpt-5.4 | codex | gpt-5.4 | False | failed | N/A | N/A |
| qwen_deepseek-reasoner | qwen | deepseek-reasoner | False | failed | N/A | N/A |

**Best candidate:** claude_sonnet (only successful candidate)

---

### Block ch006-block-001

**Chapter:** ch006
**Source preview:** 集合钟敲响了，急促的钟声之后伴随着水手们杂乱慌张的脚步，劳伦斯则和二副以及那位还没有把气喘匀的牧师先生留在了驾驶室中。
这位老船长看向窗外的海面，此刻白橡木号还处于灵界深度，船舷之外的大海上盘踞着雾霭，水面也仍然如墨染一般漆黑，但风暴已经止息，那可怕的失乡号也已经不见了踪影——这不禁给人一种错觉，就好像之前的风暴甚至崩塌的现实边境都是那艘幽灵船带来的一样，而现在所有的灾难又随着那艘船的离去而远离了白橡木号。
劳伦斯联想到了那些有关失乡号以及邓肯·艾布诺马尔船长的可怕传说，联想到了一个多世纪前被现实边境吞噬掉的那支舰队，以及在与失乡号的遭遇中沉入幽邃深海的一艘艘海船，突然觉得这也不是不可能的事情...

| Candidate | Provider | Model | Success | Validation | QA Overall Usability | Recommendation |
|-----------|----------|-------|---------|------------|----------------------|----------------|
| claude_sonnet | claude | sonnet | True | no Chinese, no meta | N/A | N/A |
| codex_gpt-5.4-mini | codex | gpt-5.4-mini | False | failed | N/A | N/A |
| codex_gpt-5.4 | codex | gpt-5.4 | False | failed | N/A | N/A |
| qwen_deepseek-reasoner | qwen | deepseek-reasoner | True | no Chinese, no meta | N/A | N/A |

**Best candidate:** claude_sonnet (but failed omission trap, Qwen passed fidelity check)

---

## 4. Cross-Candidate Comparison

| Candidate | Success Rate | Omission Trap Passed | Glossary Compliance | Prose Quality | Reliability |
|-----------|--------------|----------------------|---------------------|---------------|-------------|
| claude_sonnet | 3/3 (100%) | ❌ Failed (ch004-block-002) | Poor (0/3 blocks) | High (polished literary Thai) | High (consistent success) |
| qwen_deepseek-reasoner | 2/3 (67%) | ✅ Passed (ch004-block-002) | Poor (0/2 blocks) | Medium (good but less polished) | Medium (one failure) |
| codex_gpt-5.4 | 0/3 (0%) | N/A (provider failure) | N/A | N/A | Unavailable |
| codex_gpt-5.4-mini | 0/3 (0%) | N/A (provider failure) | N/A | N/A | Unavailable |

**Claude vs Qwen:**
- **Claude advantages:** Higher success rate (100% vs 67%), more polished prose, consistent output.
- **Qwen advantages:** Better semantic fidelity (passed omission trap), preserved critical reactions that Claude omitted.
- **Shared weakness:** Poor glossary term compliance (both missing many required glossary terms).

**GPT candidates:** Both GPT-5.4 and GPT-5.4-mini failed due to provider configuration issues. Codex CLI appears unavailable or misconfigured.

**Recommendation:** Claude remains the primary choice for prose quality, but must be augmented with omission trap validation. Qwen is a viable fallback for capacity or for blocks where fidelity is critical.

## 5. Cost/Latency Notes

- **Claude duration:** ~30 seconds per block (ch004-block-002: 30s, ch005-block-003: 31s, ch006-block-001: 30s)
- **Qwen duration:** ~45 seconds per block (ch004-block-002: 45s, ch006-block-001: 46s) - slower but still reasonable
- **GPT candidates:** Failed before timing data
- **Approximate token usage:** Not recorded (provider CLIs don't report tokens)
- **Qualitative cost recommendation:** Claude likely most expensive (API pricing), Qwen potentially cheaper (local model), but actual costs depend on provider pricing models. For reliability and prose quality, Claude is worth the cost but requires omission validation.

## 6. Production Routing Recommendation

Based on this benchmark, we recommend:

- **Keep Claude primary** for refinement where quota permits, as it provides the highest prose quality and consistency.
- **Implement omission trap validation** for all Claude outputs, especially for dialogue and reaction patterns.
- **Use Qwen as fallback** during Claude capacity limits or for blocks where semantic fidelity is critical (e.g., known omission traps).
- **Do not adopt GPT candidates** at this time (provider configuration issues).
- **Address glossary compliance issue:** Both Claude and Qwen miss many glossary terms. Consider improving glossary retrieval or adding post-hoc glossary insertion.

## 7. Safety Gates Required Before Production Adoption

1. **Deterministic omission trap check** mandatory for all blocks (especially dialogue and reaction patterns).
2. **Deterministic no-Han/provider-meta check** must pass (already implemented).
3. **Glossary exact-match check** must pass (current failure rate high - needs improvement).
4. **Post-refinement QA** (Qwen or alternative) recommended when available.
5. **No direct write to production artifacts** until policy approved and safety gates pass.

## 8. Files Created

- Benchmark output directory: `D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\_experiments\refinement_benchmark_20260417_022640`
- Per-block candidate outputs: `*.raw.txt`, `*.refined.txt`, `*.metadata.json`
- QA judgment files: `qa_judgment.json` (not created - Qwen provider unavailable during QA phase)
- This report: `{report_path.name}`
