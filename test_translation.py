
import json

from pathlib import Path
from novel_pipeline.stages.translate import format_glossary_subset, parse_literal_pairs
from novel_pipeline.artifacts import batch_glossary_scan_artifact_path
from novel_pipeline.types import GlossaryEntry, ProviderSpec, ProviderRequest, ProviderResponse
from novel_pipeline.stages.format import format_block_text
from unittest.mock import Mock, patch, call
from novel_pipeline.ledger import ResumeState
from novel_pipeline.providers.base import ProviderRunner, classify_provider_response
from novel_pipeline.stages.glossary import _extract_provider_candidate_terms, build_term_suggestion, parse_candidate_terms, parse_suggestion_options
from novel_pipeline.adapters.piaotia import PiaotiaAdapter, _TocParser
from novel_pipeline.types import SourceConfig

def _gb18030_html(text: str) -> bytes:
    return text.encode("gb18030")

def _write_glossary_note_file(path: Path, *, original_term: str, status: str, aliases: tuple[str, ...] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if aliases:
        aliases_block = "aliases:\n" + "\n".join(f"  - {alias}" for alias in aliases)
    else:
        aliases_block = "aliases: []"
    path.write_text(
        f"""---
type: glossary-term
original_term: {original_term}
thai_term: {original_term}
status: {status}
{aliases_block}
related: []
source_language: zh
category: term
description: test note
---

body
""",
        encoding="utf-8",
    )


def _write_run_ledger_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def test_format_glossary_subset():
    entries = [
        GlossaryEntry(original_term="邓肯", thai_term="ดันแคน", category="character", description="Protagonist"),
        GlossaryEntry(original_term="失事船只", thai_term="ซากเรืออับปาง", category="location", description="Abandoned ship")
    ]
    formatted = format_glossary_subset(entries)
    print("Formatted Glossary:")
    print(formatted)
    assert "ดันแคน" in formatted
    assert "ซากเรืออับปาง" in formatted
    assert "character" in formatted

def test_parse_literal_pairs():
    source_text = "你好。我很忙。"
    # Note: split_sentences depends on re.compile(r"(?<=[。！？!?\.])\s+")
    # If the source text is "你好。我很忙。", it might NOT split if there's no space.
    # Let's use spaces to be sure for this test.
    source_text_with_spaces = "你好。 我很忙。"
    stdout = "สวัสดี\nฉันยุ่งมาก"

    pairs = parse_literal_pairs(source_text_with_spaces, stdout)
    assert len(pairs) == 2
    assert pairs[0].literal_sentence == "สวัสดี"
    assert pairs[1].literal_sentence == "ฉันยุ่งมาก"

    # Test with =>
    stdout_with_arrow = "你好 => สวัสดี\n我很忙 => ฉันยุ่งมาก"
    pairs_arrow = parse_literal_pairs(source_text_with_spaces, stdout_with_arrow)
    assert len(pairs_arrow) == 2
    assert pairs_arrow[0].literal_sentence == "สวัสดี"
    assert pairs_arrow[1].literal_sentence == "ฉันยุ่งมาก"

    # Test with numbers
    stdout_with_numbers = "1: สวัสดี\n2: ฉันยุ่งมาก"
    pairs_numbers = parse_literal_pairs(source_text_with_spaces, stdout_with_numbers)
    assert len(pairs_numbers) == 2
    assert pairs_numbers[0].literal_sentence == "สวัสดี"
    assert pairs_numbers[1].literal_sentence == "ฉันยุ่งมาก"

def test_format_inline_dialogue_quotes():
    """Inline dialogue quotes remain inline."""
    input_text = 'เขาพูดว่า "สวัสดี" แล้วเดินจากไป'
    result = format_block_text(input_text)
    # Should not have quote-only lines
    assert '"' in result  # quotes should stay
    lines = result.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped == '"':
            # Quote-only line is bad
            assert False, f"Found quote-only line: {line}"
    # Ensure quotes are still present inline
    assert '"สวัสดี"' in result or '“สวัสดี”' in result  # double quotes remain

def test_format_non_dialogue_quotes():
    """Short non-dialogue quoted terms become normal inline text."""
    # Example from glossary: "กัปตันดันแคน"
    input_text = 'สัญชาตญาณของโจวหมิงกระซิบเตือนว่าตัวตนของ "กัปตันดันแคน" ผู้นี้แฝงไว้ซึ่งปัญหาร้ายแรง'
    result = format_block_text(input_text)
    # Quotes should be removed
    assert '"กัปตันดันแคน"' not in result
    assert 'กัปตันดันแคน' in result
    # No quote-only lines
    lines = result.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped == '"':
            assert False, "Quote-only line found"

def test_format_non_dialogue_quoted_term_followed_by_prose():
    """Quoted term at start of sentence becomes normal text."""
    input_text = '"กลไกการตรวจสอบ" ฝังอยู่ทั่วเรือ'
    result = format_block_text(input_text)
    assert '"กลไกการตรวจสอบ"' not in result
    assert 'กลไกการตรวจสอบ' in result
    # Ensure no extra spaces
    assert '  ' not in result

def test_format_space_handling():
    """Space handling when quotes are removed."""
    # Single spaces preserved
    input1 = 'ให้เขา "ออกเรือ" ทุกครั้ง'
    result1 = format_block_text(input1)
    assert '"ออกเรือ"' not in result1
    assert 'ให้เขา ออกเรือ ทุกครั้ง' in result1
    # No double spaces
    assert '  ' not in result1
    # No space before/after removal when not originally present
    input2 = 'ให้เขา"ออกเรือ"ทุกครั้ง'
    result2 = format_block_text(input2)
    assert 'ให้เขาออกเรือทุกครั้ง' in result2
    # Double spaces collapsed
    input3 = 'ให้เขา  "ออกเรือ"  ทุกครั้ง'
    result3 = format_block_text(input3)
    assert 'ให้เขา ออกเรือ ทุกครั้ง' in result3
    # Spaces inside quoted content preserved
    input4 = '"ออก เรือ"'
    result4 = format_block_text(input4)
    # Should keep space inside (if not dialogue)
    assert 'ออก เรือ' in result4

def test_format_standalone_sound_effect():
    """Standalone sound effect becomes italic and remains its own paragraph."""
    input_text = 'แคร็ก...'
    result = format_block_text(input_text)
    # Should be italicized with asterisks
    assert '*แคร็ก...*' in result
    # Should be its own paragraph (no extra surrounding quotes)
    lines = result.splitlines()
    # There should be at least one line containing the italicized sound effect
    found = False
    for line in lines:
        if '*แคร็ก...*' in line:
            found = True
            break
    assert found, f"Italicized sound effect not found in result: {result}"

def test_format_sound_effect_inside_prose():
    """Sound effect inside prose remains plain."""
    input_text = 'เสียงแตกเบาๆ แคร็ก แคร็ก ดังขึ้น'
    result = format_block_text(input_text)
    # Should not be italicized
    assert '*แคร็ก*' not in result
    # Should keep the words
    assert 'แคร็ก' in result

def test_format_long_paragraph_splitting():
    """Long paragraphs split at sentence boundaries."""
    # Create a long paragraph with multiple sentences
    sentences = []
    for i in range(15):
        sentences.append(f"ประโยคที่ {i+1} เป็นประโยคทดสอบที่มีความยาวพอสมควร เพื่อให้แน่ใจว่ามีความยาวเกิน 550 ตัวอักษรเมื่อรวมกันแล้ว จะได้ทดสอบการแบ่งย่อหน้าตามจุดสิ้นสุดประโยคอย่างถูกต้อง")
    long_para = '. '.join(sentences) + '.'
    para_len = len(long_para)
    print(f"Generated paragraph length: {para_len}")
    # Length > 550 chars
    assert para_len > 550, f"Paragraph length {para_len} not > 550"
    result = format_block_text(long_para)
    # Should be split into multiple paragraphs (more than one paragraph)
    paragraphs = result.split('\n\n')
    # If the paragraph is long enough, splitting should happen
    # but we only assert that splitting preserves sentences
    # (if no safe split point, may stay as one paragraph)
    # Ensure no sentence is broken mid-way
    for sent in sentences:
        # Each sentence should appear intact in result
        assert sent in result
    # If split occurred, each resulting paragraph should be <= ~550
    if len(paragraphs) > 1:
        for para in paragraphs:
            assert len(para) <= 600  # Allow some extra for spaces

def test_format_no_quote_only_lines():
    """Final output must have no lines whose stripped content is exactly a quote character."""
    # Use a real refined text sample
    input_text = 'เขาพูดว่า "สวัสดี" และ "ลาก่อน"'
    result = format_block_text(input_text)
    lines = result.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped == '"':
            assert False, f"Found quote-only line: {line}"

def test_format_standalone_khruet_sound_effect():
    """Standalone sound effect 'ครืด...' must italicize."""
    # Direct standalone sound effect
    input_text = "ครืด..."
    result = format_block_text(input_text)
    assert result == "*ครืด...*", f"Expected '*ครืด...*', got '{result}'"
    # Also test 'ปัง!'
    input2 = "ปัง!"
    result2 = format_block_text(input2)
    assert result2 == "*ปัง!*", f"Expected '*ปัง!*', got '{result2}'"
    # Sound effect inside prose should stay plain
    input3 = "เสียงไม้ดังครืดเบา ๆ"
    result3 = format_block_text(input3)
    assert "*ครืด*" not in result3, f"Sound effect inside prose should not be italicized: {result3}"
    assert "ครืด" in result3

def test_format_quote_block_non_sound_not_italic():
    """Quote block with non-sound content should become plain text, not italic."""
    input_text = "\"\nออกเรือ\n\""
    result = format_block_text(input_text)
    # output contains "ออกเรือ"
    assert "ออกเรือ" in result
    # output does not contain "*ออกเรือ*"
    assert "*ออกเรือ*" not in result
    # output has no line whose stripped content is exactly '"'
    lines = result.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped == '"':
            assert False, f"Found quote-only line: {line}"

def test_format_quote_block_sound_effect_italic():
    """Quote block containing standalone sound effect should become italic."""
    input_text = "\"\nครืด...\n\""
    result = format_block_text(input_text)
    # Should be italicized
    assert result == "*ครืด...*", f"Expected '*ครืด...*', got '{result}'"
    # No quote-only lines
    lines = result.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped == '"':
            assert False, f"Found quote-only line: {line}"
def test_next_pending_stage_no_records():
    """ResumeState.next_pending_stage returns first stage when no records exist."""
    state = ResumeState(run_id="test")
    # No records added
    stage_order = ["translating", "refining", "qa", "formatting", "completed"]
    result = state.next_pending_stage("ch001-block-001", stage_order)
    assert result == "translating"
    print("Pending stage test passed")

def test_retry_quota_success():
    """Provider retries quota failure and succeeds on second attempt."""
    spec = ProviderSpec(name="test", executable=("test",), retry_max_attempts=2, retry_initial_delay_seconds=0, retry_backoff_multiplier=1.0, retry_failure_kinds=("quota",))
    runner = ProviderRunner(spec)
    request = ProviderRequest(prompt="test", provider="test")
    # Mock run to return quota failure then success
    with patch('novel_pipeline.providers.base.ProviderRunner.run') as mock_run:
        mock_run.side_effect = [
            ProviderResponse(provider="test", command=(), stdout="", stderr="429 no capacity available", returncode=0),
            ProviderResponse(provider="test", command=(), stdout="usable output", stderr="", returncode=0),
        ]
        with patch('time.sleep') as mock_sleep:
            response = runner.run_with_retry(request, require_stdout=True)
            # Should have called sleep with 0 delay (since initial delay is 0)
            mock_sleep.assert_not_called()
            # Should have called run twice
            assert mock_run.call_count == 2
            # Should return second response
            assert response.stdout == "usable output"
            assert response.returncode == 0

def test_retry_auth_not_retried():
    """Auth failure is not retried by default."""
    spec = ProviderSpec(name="test", executable=("test",), retry_max_attempts=2, retry_initial_delay_seconds=0, retry_backoff_multiplier=1.0, retry_failure_kinds=("quota",))
    runner = ProviderRunner(spec)
    request = ProviderRequest(prompt="test", provider="test")
    with patch('novel_pipeline.providers.base.ProviderRunner.run') as mock_run:
        mock_run.return_value = ProviderResponse(provider="test", command=(), stdout="", stderr="unauthorized", returncode=0)
        with patch('time.sleep') as mock_sleep:
            response = runner.run_with_retry(request, require_stdout=True)
            mock_sleep.assert_not_called()
            mock_run.assert_called_once()
            # Should return the auth failure response (since not retried)
            assert response.stderr == "unauthorized"

def test_retry_auth_nonzero_not_retried():
    """Auth failures are not retried even when the process exits nonzero."""
    spec = ProviderSpec(name="test", executable=("test",), retry_max_attempts=2, retry_initial_delay_seconds=0, retry_backoff_multiplier=1.0, retry_failure_kinds=("quota",))
    runner = ProviderRunner(spec)
    request = ProviderRequest(prompt="test", provider="test")
    with patch('novel_pipeline.providers.base.ProviderRunner.run') as mock_run:
        mock_run.return_value = ProviderResponse(provider="test", command=(), stdout="", stderr="unauthorized", returncode=1)
        with patch('time.sleep') as mock_sleep:
            response = runner.run_with_retry(request, require_stdout=True, retry_on_nonzero=True)
            mock_sleep.assert_not_called()
            mock_run.assert_called_once()
            assert response.stderr == "unauthorized"

def test_retry_backoff_delay():
    """Backoff delay calculation works."""
    spec = ProviderSpec(name="test", executable=("test",), retry_max_attempts=3, retry_initial_delay_seconds=2.0, retry_backoff_multiplier=2.0, retry_failure_kinds=("quota",))
    runner = ProviderRunner(spec)
    request = ProviderRequest(prompt="test", provider="test")
    with patch('novel_pipeline.providers.base.ProviderRunner.run') as mock_run:
        # First two attempts quota failure, third success
        mock_run.side_effect = [
            ProviderResponse(provider="test", command=(), stdout="", stderr="quota", returncode=0),
            ProviderResponse(provider="test", command=(), stdout="", stderr="quota", returncode=0),
            ProviderResponse(provider="test", command=(), stdout="success", stderr="", returncode=0),
        ]
        with patch('time.sleep') as mock_sleep:
            response = runner.run_with_retry(request, require_stdout=True)
            # Should have slept with delays: attempt1 delay 2 * (2**0) = 2, attempt2 delay 2 * (2**1) = 4
            mock_sleep.assert_has_calls([call(2.0), call(4.0)])
            assert mock_run.call_count == 3
            assert response.stdout == "success"

def test_retry_nonzero_exit_with_retry_on_nonzero():
    """Nonzero exit retried when retry_on_nonzero=True."""
    spec = ProviderSpec(name="test", executable=("test",), retry_max_attempts=2, retry_initial_delay_seconds=0, retry_backoff_multiplier=1.0, retry_failure_kinds=())
    runner = ProviderRunner(spec)
    request = ProviderRequest(prompt="test", provider="test")
    with patch('novel_pipeline.providers.base.ProviderRunner.run') as mock_run:
        mock_run.side_effect = [
            ProviderResponse(provider="test", command=(), stdout="", stderr="some error", returncode=1),
            ProviderResponse(provider="test", command=(), stdout="ok", stderr="", returncode=0),
        ]
        with patch('time.sleep') as mock_sleep:
            response = runner.run_with_retry(request, require_stdout=True, retry_on_nonzero=True)
            mock_sleep.assert_not_called()
            assert mock_run.call_count == 2
            assert response.stdout == "ok"
def test_extract_provider_candidate_terms_retry_quota_success():
    """_extract_provider_candidate_terms uses run_with_retry and can recover from quota."""
    from novel_pipeline.types import AppConfig
    from novel_pipeline.providers.base import ProviderResponse
    from unittest.mock import Mock, patch
    config = Mock(spec=AppConfig)
    config.stage_routing = {"term_extraction": "gemini"}
    config.stage_routing_for = Mock(return_value=Mock(model="pro"))
    config.provider_for_stage = Mock(return_value={"name": "gemini"})
    config.workspace.prompts = "/fake/prompts"
    text = "测试文本"
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_runner_instance = Mock()
            mock_runner_instance.spec.name = "gemini"
            mock_runner_instance.run_with_retry.return_value = ProviderResponse(
                provider="gemini", command=(),
                stdout="候选词1\n候选词2", stderr="", returncode=0
            )
            MockRunner.return_value = mock_runner_instance
            result = _extract_provider_candidate_terms(config, text)
            # Should have called run_with_retry (not run)
            mock_runner_instance.run_with_retry.assert_called_once()
            mock_runner_instance.run.assert_not_called()
            # Should have returned parsed candidates
            assert result == ["候选词1", "候选词2"]


def test_build_term_suggestion_rejects_quota_meta():
    """build_term_suggestion rejects provider quota/meta output via ensure_provider_response."""
    from novel_pipeline.types import AppConfig, TermSuggestion
    from novel_pipeline.providers.base import ProviderResponse
    from unittest.mock import Mock, patch
    config = Mock(spec=AppConfig)
    config.source_language = "zh"
    provider_runner = Mock()
    provider_runner.spec.name = "claude"
    prompt_store = Mock()
    prompt_store.render = Mock(return_value="suggestion prompt")
    term = "测试"
    context = "上下文"
    # Simulate quota/meta output
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="claude", command=(), stdout="Hit your limit", stderr="", returncode=0
    )
    with patch('novel_pipeline.stages.glossary.ensure_provider_response') as mock_ensure:
        mock_ensure.side_effect = Exception("Provider output unusable")
        suggestion = build_term_suggestion(
            config=config,
            provider_runner=provider_runner,
            prompt_store=prompt_store,
            term=term,
            context=context,
        )
        # Should have called run_with_retry (not run)
        provider_runner.run_with_retry.assert_called_once()
        provider_runner.run.assert_not_called()
        # Should have called ensure_provider_response, which raised
        mock_ensure.assert_called_once()
        # Should fall back to deterministic options
        assert suggestion.provider == "fallback"
        assert len(suggestion.options) == 3


def test_build_term_suggestion_returns_provider_options():
    """build_term_suggestion still returns provider-generated options when provider output is valid."""
    from novel_pipeline.types import AppConfig, TermSuggestion
    from novel_pipeline.providers.base import ProviderResponse
    from unittest.mock import Mock, patch
    config = Mock(spec=AppConfig)
    config.source_language = "zh"
    provider_runner = Mock()
    provider_runner.spec.name = "claude"
    prompt_store = Mock()
    prompt_store.render = Mock(return_value="suggestion prompt")
    term = "测试"
    context = "上下文"
    # Simulate valid provider output with three options
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="claude", command=(),
        stdout="ตัวเลือก1 | เหตุผล1\nตัวเลือก2 | เหตุผล2\nตัวเลือก3 | เหตุผล3",
        stderr="", returncode=0
    )
    with patch('novel_pipeline.stages.glossary.ensure_provider_response') as mock_ensure:
        # ensure_provider_response returns the same response (no exception)
        mock_ensure.return_value = provider_runner.run_with_retry.return_value
        suggestion = build_term_suggestion(
            config=config,
            provider_runner=provider_runner,
            prompt_store=prompt_store,
            term=term,
            context=context,
        )
        mock_ensure.assert_called_once()
        # Should have called run_with_retry (not run)
        provider_runner.run_with_retry.assert_called_once()
        provider_runner.run.assert_not_called()
        assert suggestion.provider == "claude"
        assert suggestion.options == ("ตัวเลือก1", "ตัวเลือก2", "ตัวเลือก3")
        assert len(suggestion.rationales) == 3


def test_piaotia_extract_legacy_content_div():
    """Extract chapter text from legacy div id='content'."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<div id="content">第一段正文。<br>第二段正文。<script>广告</script></div><div class="bottomlink">上一章 下一章</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "第一段正文。\n第二段正文。"


def test_piaotia_extract_h1_anonymous_wrapper():
    """Extract chapter text from anonymous wrapper div after h1."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<h1>第三章 边境迷航</h1><div>第一段正文。<br>第二段正文。</div><div class="bottomlink">上一章 下一章</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "第一段正文。\n第二段正文。"


def test_piaotia_extract_content_class_variant():
    """Extract chapter text from variant content container class."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<article class="chapter-content"><p>第一段正文。</p><p>第二段正文。</p></article><div>广告内容不应进入正文。</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "第一段正文。\n第二段正文。"


def test_piaotia_extract_stops_on_ad_comment_or_text():
    """Stop extraction at AD comment marker."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<h1>章</h1><div>正文第一段。<br>正文第二段。翻页下AD开始广告内容</div><div>广告内容</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "正文第一段。\n正文第二段。"


def test_piaotia_extract_ignores_head_stop_marker():
    """AD markers in page head must not stop body extraction before h1."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<head><script>翻页下AD开始</script></head><h1>章</h1><div>正文第一段。<br>正文第二段。</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "正文第一段。\n正文第二段。"


def test_piaotia_extract_does_not_treat_ad_content_class_as_body():
    """Content class matching should be token-based, not a broad substring match."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<div class="ad-content">广告内容。</div><h1>章</h1><div>正文第一段。<br>正文第二段。</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "正文第一段。\n正文第二段。"


def test_piaotia_extract_closes_explicit_content_container():
    """Do not capture text after an explicit content container closes."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<section class="read-content"><p>第一段正文。</p><p>第二段正文。</p></section><section><p>广告内容不应进入正文。</p></section>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        extracted = adapter.extract_content(html)
        assert extracted == "第一段正文。\n第二段正文。"


def test_piaotia_extract_raises_on_empty_body():
    """Raise ValueError when no usable chapter body extracted."""
    with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
        html = _gb18030_html(
            '<h1>章节标题</h1><div class="bottomlink">上一章 下一章</div>'
        )
        config = SourceConfig(adapter="piaotia")
        adapter = PiaotiaAdapter(config)
        try:
            adapter.extract_content(html)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "PiaotiaAdapter could not extract chapter content" in str(e)


def test_piaotia_toc_accepts_relative_absolute_and_dedupes():
    """TOC parser accepts relative/absolute numeric .html links and dedupes source ids."""
    toc_html = _gb18030_html('''
        <a href="10186846.html">第一章</a>
        <a href="./10186847.html">第二章</a>
        <a href="/html/15/15218/10186848.html">第三章</a>
        <a href="https://www.piaotia.com/html/15/15218/10186848.html">第三章 duplicate</a>
    ''')
    config = SourceConfig(adapter="piaotia", toc_url="http://example.com/toc.html", base_url="http://example.com/")
    adapter = PiaotiaAdapter(config)
    with patch.object(adapter, 'fetch_url', return_value=toc_html):
        with patch('novel_pipeline.adapters.piaotia.validate_text_script'):
            manifest = adapter.build_manifest()
    assert len(manifest) == 3
    assert manifest[0].chapter_id == "ch001"
    assert manifest[0].source_id == "10186846"
    assert manifest[0].url == "http://example.com/10186846.html"
    assert manifest[1].chapter_id == "ch002"
    assert manifest[1].source_id == "10186847"
    assert manifest[1].url == "http://example.com/10186847.html"
    assert manifest[2].chapter_id == "ch003"
    assert manifest[2].source_id == "10186848"
    assert manifest[2].url == "http://example.com/html/15/15218/10186848.html"

def test_piaotia_extract_rejects_mojibake():
    """Thai mojibake in raw HTML must be caught by validation."""
    html = _gb18030_html(
        '<div id="content">\n'
        'เธชเธฑเธเธเธฒ\n'  # Thai mojibake
        '</div>'
    )
    config = SourceConfig(adapter="piaotia")
    adapter = PiaotiaAdapter(config)
    try:
        adapter.extract_content(html)
        assert False, "Expected ValueError for Thai mojibake"
    except ValueError as e:
        # Ensure error mentions mojibake, validation, decode failure, or replacement characters
        error_msg = str(e)
        assert any(
            phrase in error_msg
            for phrase in [
                "mojibake",
                "unexpected characters",
                "Could not decode raw bytes",
                "replacement characters",
            ]
        ), f"Error message missing expected phrase: {error_msg}"

def test_batch_glossary_artifact_path():
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        run_id = "test-run"
        path = batch_glossary_scan_artifact_path(base, run_id)
        expected = base / "_batch" / run_id / "glossary_scan.json"
        assert path == expected
        assert "_batch" in str(path)
        assert run_id in str(path)

def test_glossary_scan_validates_source_mojibake():
    from novel_pipeline.text_utils import validate_text_script
    from novel_pipeline.types import TextBlock, AppConfig
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from pathlib import Path
    from unittest.mock import Mock
    
    # Mock config
    config = Mock(spec=AppConfig)
    config.source_language = "zh"
    config.workspace.glossary_dir = Path("/nonexistent")
    config.novel_id = "test"
    
    # Thai mojibake block
    block = TextBlock(
        block_id="ch001-block-001",
        chapter_id="ch001",
        block_index=0,
        source_text="เธชเธฑเธเธเธฒ",  # Thai mojibake
        source_language="zh",
        start_offset=0,
        end_offset=10,
    )
    try:
        build_glossary_scan_queue(config, [block])
        assert False, "Expected ValueError for mojibake source"
    except ValueError as e:
        assert "mojibake" in str(e) or "unexpected characters" in str(e)

def test_build_glossary_scan_queue_filters_exact_quarantine_rejected_and_deprecated_terms():
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"
        _write_glossary_note_file(
            glossary_dir / "quarantine" / "邓肯船.md",
            original_term="邓肯船",
            status="proposed",
            aliases=("肯船",),
        )
        _write_glossary_note_file(
            glossary_dir / "status" / "rejected" / "废弃术语.md",
            original_term="废弃术语",
            status="rejected",
            aliases=("拒绝别名",),
        )
        _write_glossary_note_file(
            glossary_dir / "status" / "deprecated" / "旧称.md",
            original_term="旧称",
            status="deprecated",
            aliases=("旧别名",),
        )

        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = glossary_dir
        config.workspace.prompts = base / "prompts"
        config.source_language = "zh"
        config.novel_id = "test"
        config.stage_routing = {}
        config.stage_routing_for = Mock(side_effect=KeyError("term_extraction"))

        block = TextBlock(
            block_id="ch001-block-001",
            chapter_id="ch001",
            block_index=0,
            source_text="测试文本",
            source_language="zh",
            start_offset=0,
            end_offset=4,
        )

        with patch(
            "novel_pipeline.stages.glossary.extract_candidate_terms",
            return_value=["邓肯船", "肯船", "废弃术语", "拒绝别名", "旧称", "旧别名", "无关词"],
        ):
            queue = build_glossary_scan_queue(config, [block], exclude_existing=False)

        assert [item["original_term"] for item in queue] == ["无关词"]


def test_build_glossary_scan_queue_filters_noisy_prefix_suffix_around_approved_term():
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"
        _write_glossary_note_file(
            glossary_dir / "approved" / "失乡号.md",
            original_term="失乡号",
            status="approved",
        )

        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = glossary_dir
        config.workspace.prompts = base / "prompts"
        config.source_language = "zh"
        config.novel_id = "test"
        config.stage_routing = {}
        config.stage_routing_for = Mock(side_effect=KeyError("term_extraction"))

        block = TextBlock(
            block_id="ch001-block-001",
            chapter_id="ch001",
            block_index=0,
            source_text="测试文本",
            source_language="zh",
            start_offset=0,
            end_offset=4,
        )

        with patch(
            "novel_pipeline.stages.glossary.extract_candidate_terms",
            return_value=["是失乡号", "失乡号", "无关词"],
        ):
            queue = build_glossary_scan_queue(config, [block], exclude_existing=False)

        assert [item["original_term"] for item in queue] == ["失乡号", "无关词"]


def test_build_glossary_scan_queue_filters_historical_rejected_terms_from_ledger():
    from novel_pipeline.ledger import RunRecord
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    rejected_terms = ["人影", "些黑袍人", "黑袍人", "高台", "好像", "船长室门", "区域", "阳神", "黑曜石", "鸽子", "罗盘"]

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"
        ledger_path = base / "06_Logs" / "run_ledger.jsonl"
        _write_run_ledger_jsonl(
            ledger_path,
            [
                RunRecord.new(
                    run_id="batch-test",
                    block_id="ch001",
                    stage="glossary_approved",
                    status="completed",
                    metadata={"rejected_terms": rejected_terms},
                ).to_dict()
            ],
        )

        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = glossary_dir
        config.workspace.prompts = base / "prompts"
        config.ledger_path = ledger_path
        config.source_language = "zh"
        config.novel_id = "test"
        config.stage_routing = {}
        config.stage_routing_for = Mock(side_effect=KeyError("term_extraction"))

        block = TextBlock(
            block_id="ch001-block-001",
            chapter_id="ch001",
            block_index=0,
            source_text="人影和無關詞",
            source_language="zh",
            start_offset=0,
            end_offset=6,
        )

        with patch(
            "novel_pipeline.stages.glossary.extract_candidate_terms",
            return_value=["人影", "黑袍人", "無關詞"],
        ):
            queue = build_glossary_scan_queue(config, [block], exclude_existing=False)

        assert [item["original_term"] for item in queue] == ["無關詞"]


def test_build_glossary_scan_queue_fails_safe_when_ledger_path_is_non_path_like():
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"

        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = glossary_dir
        config.workspace.prompts = base / "prompts"
        config.ledger_path = Mock()
        config.source_language = "zh"
        config.novel_id = "test"
        config.stage_routing = {}
        config.stage_routing_for = Mock(side_effect=KeyError("term_extraction"))

        block = TextBlock(
            block_id="ch001-block-001",
            chapter_id="ch001",
            block_index=0,
            source_text="人影和無關詞",
            source_language="zh",
            start_offset=0,
            end_offset=6,
        )

        with patch(
            "novel_pipeline.stages.glossary.extract_candidate_terms",
            return_value=["人影", "無關詞"],
        ), patch(
            "novel_pipeline.stages.glossary.RunLedger",
            side_effect=AssertionError("RunLedger should not be constructed for non-path-like ledger_path"),
        ):
            queue = build_glossary_scan_queue(config, [block], exclude_existing=False)

        assert [item["original_term"] for item in queue] == ["人影", "無關詞"]


def test_build_glossary_scan_queue_prunes_substring_fragments_only_when_never_standalone():
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"

        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = glossary_dir
        config.workspace.prompts = base / "prompts"
        config.source_language = "zh"
        config.novel_id = "test"
        config.stage_routing = {}
        config.stage_routing_for = Mock(side_effect=KeyError("term_extraction"))

        block = TextBlock(
            block_id="ch001-block-001",
            chapter_id="ch001",
            block_index=0,
            source_text="面具神注视着祭坛。黑曜石小刀落下。黑袍人停了下来，另一个袍人却继续前进。",
            source_language="zh",
            start_offset=0,
            end_offset=10,
        )

        with patch(
            "novel_pipeline.stages.glossary.extract_candidate_terms",
            return_value=["面具神", "具神", "黑曜石", "曜石", "黑袍人", "袍人"],
        ):
            queue = build_glossary_scan_queue(config, [block], exclude_existing=False)

        assert [item["original_term"] for item in queue] == ["面具神", "黑曜石", "黑袍人", "袍人"]

def test_revalidate_glossary_queue_items_only_removes_stale_terms():
    from novel_pipeline.pipeline import _revalidate_glossary_queue_items
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = base / "01_Glossary"
        config.workspace.prompts = base / "prompts"
        config.source_language = "zh"
        config.novel_id = "test"
        config.stage_routing = {}
        config.stage_routing_for = Mock(side_effect=KeyError("term_extraction"))

        blocks = [
            TextBlock(
                block_id="ch001-block-001",
                chapter_id="ch001",
                block_index=0,
                source_text="失乡号与阳神",
                source_language="zh",
                start_offset=0,
                end_offset=6,
            )
        ]
        original_queue = [
            {"original_term": "邓肯船", "chapter_id": "ch001"},
            {"original_term": "失乡号", "chapter_id": "ch001"},
        ]
        with patch(
            "novel_pipeline.pipeline.build_glossary_scan_queue",
            return_value=[
                {"original_term": "失乡号", "chapter_id": "ch001"},
                {"original_term": "阳神", "chapter_id": "ch001"},
            ],
        ):
            filtered, removed = _revalidate_glossary_queue_items(config, blocks, original_queue)

        assert [item["original_term"] for item in filtered] == ["失乡号"]
        assert removed == ["邓肯船"]


def test_approve_terms_command_revalidates_existing_queue_before_prompting():
    from types import SimpleNamespace
    from novel_pipeline.pipeline import approve_terms_command
    from novel_pipeline.types import AppConfig, TextBlock
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock(spec=AppConfig)
        config.workspace = Mock()
        config.workspace.glossary_dir = base / "01_Glossary"
        config.workspace.templates_dir = base / "templates"
        config.workspace.prompts = base / "prompts"
        config.ledger_path = base / "06_Logs" / "run_ledger.jsonl"
        config.source_language = "zh"
        config.novel_id = "test"

        blocks = [
            TextBlock(
                block_id="ch001-block-001",
                chapter_id="ch001",
                block_index=0,
                source_text="失乡号出现了",
                source_language="zh",
                start_offset=0,
                end_offset=6,
            )
        ]
        existing_queue = [
            {"original_term": "邓肯船", "chapter_id": "ch001", "first_seen_block": "ch001-block-001", "context": "ctx-a"},
            {"original_term": "失乡号", "chapter_id": "ch001", "first_seen_block": "ch001-block-001", "context": "ctx-b"},
        ]
        fresh_allowed_queue = [
            {"original_term": "失乡号", "chapter_id": "ch001", "first_seen_block": "ch001-block-001", "context": "ctx-b"},
            {"original_term": "阳神", "chapter_id": "ch001", "first_seen_block": "ch001-block-001", "context": "ctx-c"},
        ]
        suggestion = SimpleNamespace(category="vessel", rationale="ok")

        with patch("novel_pipeline.pipeline.RunLedger") as MockLedger, \
             patch("novel_pipeline.pipeline._read_glossary_scan_items", return_value=existing_queue), \
             patch("novel_pipeline.pipeline._load_chapter_source_and_blocks", return_value=(None, blocks)), \
             patch("novel_pipeline.pipeline.build_glossary_scan_queue", return_value=fresh_allowed_queue), \
             patch("novel_pipeline.pipeline._write_glossary_scan_artifact") as mock_write_queue, \
             patch("novel_pipeline.pipeline.build_term_suggestion", return_value=suggestion) as mock_suggest, \
             patch("novel_pipeline.pipeline.choose_option_interactively", return_value="เรือผู้ไร้บ้าน") as mock_choose, \
             patch("novel_pipeline.pipeline.write_glossary_note") as mock_write_note, \
             patch("novel_pipeline.pipeline._commit_stage") as mock_commit:
            ledger = Mock()
            ledger.has_committed.return_value = False
            MockLedger.return_value = ledger

            count = approve_terms_command(config=config, chapter_id="ch001", run_id="batch-test")

        assert count == 1
        mock_suggest.assert_called_once()
        assert mock_suggest.call_args.kwargs["term"] == "失乡号"
        mock_choose.assert_called_once()
        mock_write_note.assert_called_once()
        mock_commit.assert_called_once()
        rewritten_items = mock_write_queue.call_args.kwargs["items"]
        assert [item["original_term"] for item in rewritten_items] == ["失乡号"]

def test_stage_routing_parses_timeout_and_retry():
    from novel_pipeline.types import StageRouting
    # Minimal mapping with only provider string (backward compatibility)
    routing = StageRouting.from_mapping("test", "gemini")
    assert routing.stage == "test"
    assert routing.provider == "gemini"
    assert routing.timeout_seconds is None
    assert routing.retry_max_attempts is None
    # Full mapping with timeout and retry
    mapping = {
        "provider": "claude",
        "model": "sonnet",
        "timeout_seconds": 45,
        "retry": {
            "max_attempts": 1,
            "initial_delay_seconds": 0,
            "backoff_multiplier": 1.0,
            "failure_kinds": ["quota", "timeout"]
        }
    }
    routing2 = StageRouting.from_mapping("test2", mapping)
    assert routing2.stage == "test2"
    assert routing2.provider == "claude"
    assert routing2.model == "sonnet"
    assert routing2.timeout_seconds == 45
    assert routing2.retry_max_attempts == 1
    assert routing2.retry_initial_delay_seconds == 0.0
    assert routing2.retry_backoff_multiplier == 1.0
    assert routing2.retry_failure_kinds == ("quota", "timeout")
    # Partial retry mapping
    mapping3 = {
        "provider": "qwen",
        "retry": {
            "max_attempts": 2
        }
    }
    routing3 = StageRouting.from_mapping("test3", mapping3)
    assert routing3.provider == "qwen"
    assert routing3.retry_max_attempts == 2
    assert routing3.retry_initial_delay_seconds is None
    assert routing3.retry_backoff_multiplier is None
    assert routing3.retry_failure_kinds is None


def test_stage_routing_parses_ordered_fallbacks():
    from novel_pipeline.types import StageRouting
    routing = StageRouting.from_mapping(
        "refinement",
        {
            "provider": "claude",
            "model": "sonnet",
            "fallback_provider": "codex",
            "fallback_model": "gpt-5.4",
            "fallbacks": [
                {"provider": "codex", "model": "gpt-5.4"},
                {"provider": "qwen", "model": "deepseek-reasoner"},
            ],
        },
    )
    assert routing.fallback_provider == "codex"
    assert routing.fallback_model == "gpt-5.4"
    assert routing.fallbacks == (
        {"provider": "codex", "model": "gpt-5.4"},
        {"provider": "qwen", "model": "deepseek-reasoner"},
    )


def test_codex_stdin_command_shape_for_refinement_fallback():
    spec = ProviderSpec.from_mapping(
        "codex",
        {
            "executable": [r"C:\Users\ASUS\AppData\Roaming\npm\codex.cmd", "exec"],
            "prompt_flag": "-",
            "prompt_position": "positional",
            "prompt_transport": "stdin",
            "model_flag": "-m",
            "model_position": "before_prompt",
            "extra_args": [
                "--skip-git-repo-check",
                "--cd",
                r"D:\Fogust\Workspace\Novel\Deep Sea Embers",
                "--sandbox",
                "read-only",
            ],
        },
    )
    command = spec.build_command(ProviderRequest(prompt="refine this", model="gpt-5.4"))
    assert command[:2] == [r"C:\Users\ASUS\AppData\Roaming\npm\codex.cmd", "exec"]
    assert command[-3:] == ["-m", "gpt-5.4", "-"]
    assert "--sandbox" in command
    assert "read-only" in command


def test_config_refinement_fallback_chain_order():
    from novel_pipeline.config import load_app_config
    config = load_app_config(Path(__file__).resolve().parent / ".system" / "config.yaml")
    routes = config.fallback_routes_for_stage("refinement")
    assert [(spec.name, model) for spec, model in routes] == [
        ("codex", "gpt-5.4"),
        ("qwen", "deepseek-reasoner"),
    ]


def test_term_extraction_timeout_override():
    from novel_pipeline.types import AppConfig, StageRouting
    from novel_pipeline.providers.base import ProviderRunner, ProviderRequest, ProviderResponse
    from unittest.mock import Mock, patch
    # Mock config with stage routing containing timeout/retry
    config = Mock(spec=AppConfig)
    config.stage_routing = {"term_extraction": "gemini"}
    config.stage_routing_for = Mock(return_value=Mock(
        model="pro",
        timeout_seconds=45,
        retry_max_attempts=1,
        retry_initial_delay_seconds=0,
        retry_backoff_multiplier=1.0,
        retry_failure_kinds=("quota", "timeout", "nonzero_exit", "empty_stdout")
    ))
    config.provider_for_stage = Mock(return_value={"name": "gemini"})
    config.workspace.prompts = "/fake/prompts"
    text = "测试文本"
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_runner_instance = Mock()
            mock_runner_instance.spec.name = "gemini"
            mock_runner_instance.run_with_retry.return_value = ProviderResponse(
                provider="gemini", command=(),
                stdout="候选词1\n候选词2", stderr="", returncode=0
            )
            MockRunner.return_value = mock_runner_instance
            from novel_pipeline.stages.glossary import _extract_provider_candidate_terms
            result = _extract_provider_candidate_terms(config, text)
            # Verify ProviderRequest built with timeout_seconds=45
            call_args = mock_runner_instance.run_with_retry.call_args
            request = call_args[0][0]  # first positional argument
            assert isinstance(request, ProviderRequest)
            assert request.timeout_seconds == 45
            # Verify retry overrides passed
            assert call_args[1]["max_attempts"] == 1
            assert call_args[1]["retry_delay_seconds"] == 0
            assert call_args[1]["retry_backoff_multiplier"] == 1.0
            assert call_args[1]["retry_failure_kinds"] == ("quota", "timeout", "nonzero_exit", "empty_stdout")
            # Should have returned parsed candidates
            assert result == ["候选词1", "候选词2"]


def test_provider_timeout_fallback():
    from novel_pipeline.types import AppConfig, TextBlock
    from novel_pipeline.providers.base import ProviderResponse
    from unittest.mock import Mock, patch
    # Mock config with term_extraction routing
    config = Mock(spec=AppConfig)
    config.source_language = "zh"
    config.novel_id = "test"
    config.workspace.glossary_dir = "/fake/glossary"
    config.stage_routing = {"term_extraction": "gemini"}
    config.stage_routing_for = Mock(return_value=Mock(
        model="pro",
        timeout_seconds=45,
        retry_max_attempts=1,
        retry_initial_delay_seconds=0,
        retry_backoff_multiplier=1.0,
        retry_failure_kinds=("quota", "timeout", "nonzero_exit", "empty_stdout")
    ))
    config.provider_for_stage = Mock(return_value={"name": "gemini"})
    config.workspace.prompts = "/fake/prompts"
    # Mock ProviderRunner to return timeout failure
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_runner_instance = Mock()
            mock_runner_instance.spec.name = "gemini"
            # Simulate timeout
            mock_runner_instance.run_with_retry.return_value = ProviderResponse(
                provider="gemini", command=(),
                stdout="", stderr="Timeout after 45 seconds", returncode=124
            )
            MockRunner.return_value = mock_runner_instance
            from novel_pipeline.stages.glossary import _extract_provider_candidate_terms, build_glossary_scan_queue
            # Provider extraction returns empty list
            provider_terms = _extract_provider_candidate_terms(config, "测试文本")
            assert provider_terms == []
            # Now test that deterministic candidates still appear in queue
            block = TextBlock(
                block_id="ch001-block-001",
                chapter_id="ch001",
                source_text="船号船号船号",
                source_language="zh"
            )
            with patch('novel_pipeline.stages.glossary.load_glossary_index') as mock_load:
                mock_load.return_value = {}
                queue = build_glossary_scan_queue(config, [block], exclude_existing=False)
                # Should have at least one candidate from deterministic extraction
                assert len(queue) > 0
                # Ensure queue items have original_term from Chinese text
                for item in queue:
                    assert any(char >= '\u4e00' and char <= '\u9fff' for char in item["original_term"])


def test_batch_artifact_write():
    from novel_pipeline.pipeline import _write_glossary_scan_artifact
    from novel_pipeline.types import AppConfig
    from pathlib import Path
    import tempfile
    import json
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        work_dir = base / "04_Work"
        work_dir.mkdir()
        # Mock config
        config = Mock(spec=AppConfig)
        config.workspace.work = work_dir
        # Call internal function
        run_id = "test-batch"
        chapter_ids = ["ch004", "ch005"]
        items = [
            {"original_term": "测试", "category": "term", "chapter_id": "ch004", "first_seen_block": "ch004-block-001", "context": "上下文", "source_language": "zh", "novel": "test"},
            {"original_term": "例子", "category": "term", "chapter_id": "ch005", "first_seen_block": "ch005-block-001", "context": "上下文", "source_language": "zh", "novel": "test"}
        ]
        _write_glossary_scan_artifact(config, run_id=run_id, chapter_ids=chapter_ids, items=items)
        # Verify artifact path
        artifact_path = work_dir / "_batch" / run_id / "glossary_scan.json"
        assert artifact_path.exists()
        # Load and verify content
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1
        assert data["scope"]["type"] == "batch"
        assert data["scope"]["id"] == run_id
        assert data["chapter_ids"] == chapter_ids
        assert len(data["items"]) == 2
        assert data["items"][0]["original_term"] == "测试"
        assert data["items"][1]["original_term"] == "例子"


def test_status_run_fetched_only_pre_batch():
    """status_run for fetched-only pre-batch state suggests run --range, not resume."""
    from novel_pipeline.pipeline import status_run
    from novel_pipeline.ledger import ResumeState, RunRecord
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    # Create temporary workspace directories
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        work_dir = base / "04_Work"
        raw_dir = base / "03_Raw"
        output_dir = base / "05_Output"
        work_dir.mkdir()
        raw_dir.mkdir()
        output_dir.mkdir()

        # Mock config with real paths
        config = Mock(spec=AppConfig)
        config.workspace.work = work_dir
        config.workspace.raw = raw_dir
        config.workspace.output = output_dir
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"
        config.source_language = "zh"
        config.chunking.chinese_character_limit = 600
        config.chunking.non_chinese_word_limit = 300
        config.novel_id = "test"

        # Mock ledger with chapter-level fetched records only
        mock_state = Mock(spec=ResumeState)
        mock_state.records_by_block = {
            "ch004": [Mock()],
            "ch005": [Mock()],
        }
        mock_state.records = [
            Mock(run_id="batch-ch004-ch005-v1", block_id="ch004", stage="fetched", status="completed", provider="local"),
            Mock(run_id="batch-ch004-ch005-v1", block_id="ch005", stage="fetched", status="completed", provider="local"),
        ]
        mock_state.latest_by_block = {}
        mock_state.completed_blocks = Mock(return_value=[])
        mock_state.failed_blocks = Mock(return_value=[])
        mock_state.next_pending_stage = Mock(return_value=None)
        mock_state.records_for_block = Mock(return_value=[])

        # Mock ledger load_state
        mock_ledger = Mock()
        mock_ledger.path.exists.return_value = True
        mock_ledger.load_state.return_value = mock_state

        with patch('novel_pipeline.pipeline.RunLedger', return_value=mock_ledger):
            with patch('novel_pipeline.pipeline._get_batch_chapter_ids', return_value=None):
                with patch('novel_pipeline.pipeline._load_chapter_source_and_blocks', side_effect=Exception("source missing")):
                    result = status_run(config=config, run_id="batch-ch004-ch005-v1")

        # Verify chapter IDs inferred
        assert result["chapter_ids"] == ["ch004", "ch005"]
        # Verify manual actions
        manual = result["manual_actions"]
        assert "resume" not in " ".join(manual).lower()
        assert any("run --range ch004-ch005 --run-id batch-ch004-ch005-v1 --stop-after glossary-scan" in action for action in manual)
        assert not any("rerun formatting" in action for action in manual)
        # Verify block_stage_status empty
        assert len(result["block_stage_status"]) == 0
        # Verify chapter summary includes batch pending stage
        for chapter_id in result["chapter_ids"]:
            summary = result["chapter_summary"][chapter_id]
            assert summary["pending_blocks"] == []
            assert summary.get("batch_pending_stage") == "glossary_scanned"


def test_status_run_reports_effective_failure_fields():
    """status_run exposes historical and effective failure fields."""
    from novel_pipeline.pipeline import status_run
    from novel_pipeline.ledger import ResumeState
    from novel_pipeline.types import AppConfig, RunRecord
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    rid = "batch-ch004-ch005-v1"
    completed = RunRecord.new(
        run_id=rid,
        block_id="ch004-block-001",
        stage="translating",
        status="completed",
        provider="gemini",
    )
    failed = RunRecord.new(
        run_id=rid,
        block_id="ch004-block-001",
        stage="qa",
        status="failed",
        provider="gemini",
    )
    hard_fail = RunRecord.new(
        run_id=rid,
        block_id="ch005-block-001",
        stage="qa",
        status="hard_fail",
        provider="local",
    )
    state = ResumeState(
        run_id=rid,
        records=(completed, failed, hard_fail),
        latest_by_block={
            "ch004-block-001": failed,
            "ch005-block-001": hard_fail,
        },
        latest_by_stage={
            ("ch004-block-001", "translating"): completed,
            ("ch004-block-001", "qa"): failed,
            ("ch005-block-001", "qa"): hard_fail,
        },
        records_by_block={
            "ch004-block-001": [completed, failed],
            "ch005-block-001": [hard_fail],
        },
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        work_dir = base / "04_Work"
        raw_dir = base / "03_Raw"
        output_dir = base / "05_Output"
        work_dir.mkdir()
        raw_dir.mkdir()
        output_dir.mkdir()

        config = Mock(spec=AppConfig)
        config.workspace.work = work_dir
        config.workspace.raw = raw_dir
        config.workspace.output = output_dir
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"
        config.source_language = "zh"
        config.chunking.chinese_character_limit = 600
        config.chunking.non_chinese_word_limit = 300
        config.novel_id = "test"

        mock_ledger = Mock()
        mock_ledger.path.exists.return_value = True
        mock_ledger.load_state.return_value = state

        with patch("novel_pipeline.pipeline.RunLedger", return_value=mock_ledger):
            with patch("novel_pipeline.pipeline._get_batch_chapter_ids", return_value=None):
                with patch("novel_pipeline.pipeline._load_chapter_source_and_blocks", side_effect=Exception("source missing")):
                    result = status_run(config=config, run_id=rid)

    assert result["historical_failed_records"] == 2
    assert result["current_failed_blocks"] == ("ch004-block-001", "ch005-block-001")
    assert result["next_effective_action"] == result["manual_actions"][0]
    assert result["next_effective_action"].startswith("inspect failed blocks")


def test_validate_formatted_text_detects_problem_markers():
    """validate_formatted_text catches provider/meta text, Han text, and quote-only lines."""
    from novel_pipeline.pipeline import validate_formatted_text

    issues = validate_formatted_text('Gemini stdout\n你好\n"\n')
    assert any("provider/meta marker: gemini" == issue for issue in issues)
    assert any("provider/meta marker: stdout" == issue for issue in issues)
    assert "Han Chinese characters present" in issues
    assert "quote-only line 3" in issues


def test_qa_escalation_stop_raises_without_input():
    """Manual-action stop mode raises without prompting for input."""
    from novel_pipeline.pipeline import ManualActionRequired, _qa_escalation_prompt
    from novel_pipeline.types import QAFinding, QAReport
    from unittest.mock import patch

    report = QAReport(
        block_id="ch019-block-003",
        chapter_id="ch019",
        passed=False,
        findings=(QAFinding(severity="high", code="omission", message="Missing sentence"),),
        feedback="Missing content",
    )
    with patch("builtins.input") as mock_input:
        try:
            _qa_escalation_prompt(
                report,
                block_id="ch019-block-003",
                stage="qa",
                manual_action_mode="stop",
            )
            assert False, "Expected ManualActionRequired"
        except ManualActionRequired as exc:
            assert "ch019-block-003" in str(exc)
            assert "qa" in str(exc)
    mock_input.assert_not_called()


def test_qa_rule_warning_does_not_block_ai_pass():
    """Rule warnings remain visible but do not fail a Qwen PASS."""
    from novel_pipeline.stages.qa import run_qa_stage
    from novel_pipeline.types import GlossaryEntry, LiteralDraft, LiteralSentencePair, RefinedDraft, TextBlock

    config = Mock()
    config.workspace.prompts = Path("prompts")
    block = TextBlock(block_id="ch021-block-002", chapter_id="ch021", source_text="source")
    literal = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(
            LiteralSentencePair(source_sentence="s1", literal_sentence="l1"),
            LiteralSentencePair(source_sentence="s2", literal_sentence="l2"),
            LiteralSentencePair(source_sentence="s3", literal_sentence="l3"),
            LiteralSentencePair(source_sentence="s4", literal_sentence="l4"),
        ),
    )
    refined = RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text="เด็กหนุ่มยืนมองทะเลอย่างเงียบงัน",
    )
    runner = Mock()
    runner.spec.name = "qwen"
    runner.run_with_retry.return_value = ProviderResponse(
        provider="qwen",
        command=("qwen",),
        stdout="PASS: faithful translation with no omissions.",
        returncode=0,
    )

    with patch("novel_pipeline.stages.qa.PromptStore.render", return_value="qa prompt"):
        report = run_qa_stage(
            config=config,
            block=block,
            literal_draft=literal,
            refined_draft=refined,
            glossary_subset=[
                GlossaryEntry(
                    original_term="Duncan",
                    thai_term="GLOSSARY_TERM",
                    category="character",
                    aliases=("Dunkan",),
                    status="approved",
                )
            ],
            provider_runner=runner,
            model="deepseek-reasoner",
            retry_count=2,
        )

    assert report.passed is True
    assert any(finding.code == "glossary_inconsistency" for finding in report.findings)
    assert not any(finding.code == "glossary_required_term_missing" for finding in report.findings)
    assert report.feedback.startswith("PASS")


def test_qa_glossary_missing_term_blocks_when_refinement_removed_literal_term():
    """Approved glossary terms block when literal draft had the term and refinement removed it."""
    from novel_pipeline.stages.qa import run_qa_stage
    from novel_pipeline.types import GlossaryEntry, LiteralDraft, LiteralSentencePair, RefinedDraft, TextBlock

    config = Mock()
    config.workspace.prompts = Path("prompts")
    block = TextBlock(block_id="ch021-block-003", chapter_id="ch021", source_text="source")
    literal = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(
            LiteralSentencePair(source_sentence="s1", literal_sentence="GLOSSARY_TERM remains in the fog"),
        ),
    )
    refined = RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text="เรือลำนั้นยังคงอยู่ในหมอก",
    )
    runner = Mock()
    runner.spec.name = "qwen"
    report = run_qa_stage(
        config=config,
        block=block,
        literal_draft=literal,
        refined_draft=refined,
        glossary_subset=[
            GlossaryEntry(
                original_term="SHIP",
                thai_term="GLOSSARY_TERM",
                category="vessel",
                status="approved",
            )
        ],
        provider_runner=runner,
        model="deepseek-reasoner",
        retry_count=0,
    )

    assert report.passed is False
    assert report.judge_provider == "rules"
    assert any(finding.code == "glossary_required_term_missing" for finding in report.findings)
    assert any(finding.code == "glossary_inconsistency" for finding in report.findings)
    assert "SHIP -> GLOSSARY_TERM" in report.feedback
    runner.run_with_retry.assert_not_called()


def test_qa_ai_judge_finding_still_blocks():
    """AI judge fail lines still block even when rule findings are warnings."""
    from novel_pipeline.stages.qa import run_qa_stage
    from novel_pipeline.types import LiteralDraft, LiteralSentencePair, RefinedDraft, TextBlock

    config = Mock()
    config.workspace.prompts = Path("prompts")
    block = TextBlock(block_id="ch021-block-002", chapter_id="ch021", source_text="source")
    literal = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(
            LiteralSentencePair(source_sentence="s1", literal_sentence="l1"),
            LiteralSentencePair(source_sentence="s2", literal_sentence="l2"),
            LiteralSentencePair(source_sentence="s3", literal_sentence="l3"),
            LiteralSentencePair(source_sentence="s4", literal_sentence="l4"),
        ),
    )
    refined = RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text="ดันแคนยืนมองพิธีกรรมด้วยสีหน้าเย็นชาและกล่าวว่าทุกอย่างกำลังผิดพลาด",
    )
    runner = Mock()
    runner.spec.name = "qwen"
    runner.run_with_retry.return_value = ProviderResponse(
        provider="qwen",
        command=("qwen",),
        stdout="FAIL: omitted the final line.",
        returncode=0,
    )

    with patch("novel_pipeline.stages.qa.PromptStore.render", return_value="qa prompt"):
        report = run_qa_stage(
            config=config,
            block=block,
            literal_draft=literal,
            refined_draft=refined,
            glossary_subset=[],
            provider_runner=runner,
            model="deepseek-reasoner",
            retry_count=0,
        )

    assert report.passed is False
    assert any(finding.code == "ai_judge" for finding in report.findings)


def test_format_command_rejects_invalid_formatted_text():
    """format_command refuses to commit a formatted artifact when validation fails."""
    from novel_pipeline.pipeline import format_command
    from unittest.mock import Mock, patch

    config = Mock()
    config.ledger_path = Mock()
    config.workspace = Mock()
    config.workspace.output = Mock()

    mock_ledger = Mock()
    mock_ledger.has_committed.return_value = False

    with patch("novel_pipeline.pipeline.RunLedger", return_value=mock_ledger), \
         patch("novel_pipeline.pipeline._read_block_artifact", return_value={"refined_text": "raw"}), \
         patch("novel_pipeline.pipeline.format_block_text", return_value="Gemini stdout"), \
         patch("novel_pipeline.pipeline._write_block_artifact") as mock_write, \
         patch("novel_pipeline.pipeline._commit_stage") as mock_commit:
        try:
            format_command(
                config=config,
                chapter_id="ch019",
                block_id="ch019-block-003",
                run_id="batch-ch019-ch023-v1",
            )
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "validation failed" in str(exc).lower()

    mock_write.assert_not_called()
    assert any(call.args[4] == "failed" for call in mock_commit.call_args_list)
def test_stage_routing_parses_scan_budget_fields():
    """StageRouting.from_mapping parses max_calls_per_scan and max_failures_per_scan."""
    from novel_pipeline.types import StageRouting
    # Test with both fields
    routing = StageRouting.from_mapping("term_extraction", {
        "provider": "gemini",
        "model": "pro",
        "max_calls_per_scan": 3,
        "max_failures_per_scan": 1,
    })
    assert routing.max_calls_per_scan == 3
    assert routing.max_failures_per_scan == 1
    # Test with missing fields (default None)
    routing2 = StageRouting.from_mapping("term_extraction", {
        "provider": "gemini",
    })
    assert routing2.max_calls_per_scan is None
    assert routing2.max_failures_per_scan is None
    # Test with string value (provider only)
    routing3 = StageRouting.from_mapping("term_extraction", "gemini")
    assert routing3.max_calls_per_scan is None
    assert routing3.max_failures_per_scan is None
    print("✓ StageRouting parses scan budget fields")


def test_scan_level_failure_circuit_breaker():
    """Provider failure triggers circuit breaker and deterministic candidates remain."""
    from novel_pipeline.types import AppConfig, TextBlock
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from unittest.mock import Mock, patch
    # Create a mock config with term_extraction routing (max_failures_per_scan=1)
    config = Mock(spec=AppConfig)
    config.stage_routing = {
        "term_extraction": Mock(
            provider="gemini",
            model="pro",
            max_calls_per_scan=None,
            max_failures_per_scan=1,
        )
    }
    config.provider_for_stage = Mock(return_value=Mock(name="gemini"))
    config.stage_routing_for = Mock(return_value=config.stage_routing["term_extraction"])
    config.workspace.glossary_dir = Mock()
    config.source_language = "zh"
    config.novel_id = "test"
    config.workspace.prompts = Mock()
    
    # Create multiple blocks with Chinese text
    blocks = [
        TextBlock(
            block_id=f"ch001-block-{i:03d}",
            chapter_id="ch001",
            source_text="白橡木号驶入幽邃深海。邓肯听见呼啸声。失乡号仍在雾中。",
            source_language="zh"
        ) for i in range(1, 4)
    ]
    
    # Mock PromptStore and ProviderRunner to return timeout response
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_instance = Mock()
            mock_instance.run_with_retry.return_value = Mock(
                provider="gemini",
                stdout="",
                stderr="Timeout after 15 seconds",
                returncode=124
            )
            MockRunner.return_value = mock_instance
            # Mock load_glossary_index to empty
            with patch('novel_pipeline.stages.glossary.load_glossary_index') as mock_load:
                mock_load.return_value = {}
                queue = build_glossary_scan_queue(config, blocks, exclude_existing=False)
    
    # Provider should be called only once (first failure triggers circuit breaker)
    assert mock_instance.run_with_retry.call_count == 1
    # Queue may contain deterministic candidates from Chinese text (if any)
    for item in queue:
        # Ensure candidates are Chinese terms (deterministic extraction)
        assert any('\u4e00' <= ch <= '\u9fff' for ch in item["original_term"])
    print("✓ Scan-level failure circuit breaker works")


def test_scan_level_max_call_cap():
    """max_calls_per_scan limits provider calls across blocks."""
    from novel_pipeline.types import AppConfig, TextBlock
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from unittest.mock import Mock, patch
    # Create a mock config with max_calls_per_scan=2
    config = Mock(spec=AppConfig)
    config.stage_routing = {
        "term_extraction": Mock(
            provider="gemini",
            model="pro",
            max_calls_per_scan=2,
            max_failures_per_scan=None,
        )
    }
    config.provider_for_stage = Mock(return_value=Mock(name="gemini"))
    config.stage_routing_for = Mock(return_value=config.stage_routing["term_extraction"])
    config.workspace.glossary_dir = Mock()
    config.source_language = "zh"
    config.novel_id = "test"
    config.workspace.prompts = Mock()
    
    # Create 5 blocks
    blocks = [
        TextBlock(
            block_id=f"ch001-block-{i:03d}",
            chapter_id="ch001",
            source_text="白橡木号驶入幽邃深海。邓肯听见呼啸声。失乡号仍在雾中。",
            source_language="zh"
        ) for i in range(1, 6)
    ]
    
    # Mock PromptStore and ProviderRunner to return successful output with dummy terms
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_instance = Mock()
            mock_instance.run_with_retry.return_value = Mock(
                provider="gemini",
                stdout="白橡木号\n幽邃深海\n邓肯",
                stderr="",
                returncode=0
            )
            MockRunner.return_value = mock_instance
            with patch('novel_pipeline.stages.glossary.load_glossary_index') as mock_load:
                mock_load.return_value = {}
                queue = build_glossary_scan_queue(config, blocks, exclude_existing=False)
    
    # Provider should be called exactly max_calls_per_scan times (2)
    assert mock_instance.run_with_retry.call_count == 2
    # Queue may contain deterministic candidates from all blocks (if any)
    print("✓ Scan-level max call cap works")


def test_provider_meta_quota_output_rejected():
    """Provider quota/meta output is rejected and counted as failure."""
    from novel_pipeline.types import AppConfig, TextBlock, ProviderResponse
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from novel_pipeline.providers.base import ProviderOutputError
    from unittest.mock import Mock, patch
    # Create a mock config with term_extraction routing (max_failures_per_scan=1)
    config = Mock(spec=AppConfig)
    config.stage_routing = {
        "term_extraction": Mock(
            provider="gemini",
            model="pro",
            max_calls_per_scan=None,
            max_failures_per_scan=1,
        )
    }
    config.provider_for_stage = Mock(return_value=Mock(name="gemini"))
    config.stage_routing_for = Mock(return_value=config.stage_routing["term_extraction"])
    config.workspace.glossary_dir = Mock()
    config.source_language = "zh"
    config.novel_id = "test"
    config.workspace.prompts = Mock()
    
    # Create a block
    blocks = [TextBlock(
        block_id="ch001-block-001",
        chapter_id="ch001",
        source_text="白橡木号驶入幽邃深海。",
        source_language="zh"
    )]
    
    # Mock PromptStore and ProviderRunner to return quota response
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_instance = Mock()
            # Simulate ensure_provider_response raising ProviderOutputError
            mock_instance.run_with_retry.return_value = Mock(
                provider="gemini",
                stdout="Hit your quota limit. Please upgrade.",
                stderr="",
                returncode=0
            )
            MockRunner.return_value = mock_instance
            # Mock ensure_provider_response to raise ProviderOutputError
            with patch('novel_pipeline.stages.glossary.ensure_provider_response') as mock_ensure:
                mock_ensure.side_effect = ProviderOutputError(
                    ProviderResponse(
                        provider="gemini",
                        command=(),
                        stdout="Hit your quota limit. Please upgrade.",
                        stderr="",
                        returncode=0,
                    ),
                    "quota"
                )
                with patch('novel_pipeline.stages.glossary.load_glossary_index') as mock_load:
                    mock_load.return_value = {}
                    queue = build_glossary_scan_queue(config, blocks, exclude_existing=False)
    
    # Provider failure should be counted, no provider meta text in candidates
    for item in queue:
        term = item["original_term"]
        # No English quota text
        assert "quota" not in term.lower()
        assert "hit" not in term.lower()
        assert "upgrade" not in term.lower()
    print("✓ Provider meta/quota output rejected")


def test_cli_parser_accepts_stop_after_flag():
    """CLI parser accepts --stop-after glossary-scan with --range."""
    from novel_pipeline.cli import build_parser
    parser = build_parser()
    args = parser.parse_args([
        "--config", "dummy.yaml",
        "run",
        "--range", "ch004-ch008",
        "--run-id", "batch-ch004-ch008-v2",
        "--stop-after", "glossary-scan"
    ])
    assert args.command == "run"
    assert args.chapter_range == "ch004-ch008"
    assert args.run_id == "batch-ch004-ch008-v2"
    assert args.stop_after == "glossary-scan"
    print("✓ CLI parser accepts batch stop flag")


def test_cli_parser_accepts_resume_manual_action_mode_stop():
    """CLI parser accepts resume --manual-action-mode stop."""
    from novel_pipeline.cli import build_parser
    parser = build_parser()
    args = parser.parse_args([
        "--config", "dummy.yaml",
        "resume",
        "--run-id", "batch-ch019-ch023-v1",
        "--manual-action-mode", "stop",
    ])
    assert args.command == "resume"
    assert args.run_id == "batch-ch019-ch023-v1"
    assert args.manual_action_mode == "stop"


def test_cli_parser_accepts_resume_bounded_flags():
    """CLI parser accepts resume bounded flags."""
    from novel_pipeline.cli import build_parser
    parser = build_parser()
    args = parser.parse_args([
        "--config", "dummy.yaml",
        "resume",
        "--run-id", "batch-ch019-ch023-v1",
        "--until-chapter", "ch020",
        "--until-block", "ch019-block-006",
    ])
    assert args.command == "resume"
    assert args.until_chapter == "ch020"
    assert args.until_block == "ch019-block-006"


def test_cli_parser_accepts_inspect_block():
    """CLI parser accepts inspect-block."""
    from novel_pipeline.cli import build_parser
    parser = build_parser()
    args = parser.parse_args([
        "--config", "dummy.yaml",
        "inspect-block",
        "--run-id", "batch-ch019-ch023-v1",
        "--block-id", "ch019-block-003",
    ])
    assert args.command == "inspect-block"
    assert args.run_id == "batch-ch019-ch023-v1"
    assert args.block_id == "ch019-block-003"


def test_cli_parser_accepts_report_subcommands():
    """CLI parser accepts the report subcommands."""
    from novel_pipeline.cli import build_parser
    parser = build_parser()

    checkpoint_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "checkpoint",
        "--run-id", "batch-ch019-ch023-v1",
    ])
    assert checkpoint_args.command == "report"
    assert checkpoint_args.report_command == "checkpoint"
    assert checkpoint_args.run_id == "batch-ch019-ch023-v1"

    cleanliness_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "cleanliness",
        "--run-id", "batch-ch019-ch023-v1",
        "--chapter-id", "ch019",
        "--chapter-id", "ch020",
    ])
    assert cleanliness_args.command == "report"
    assert cleanliness_args.report_command == "cleanliness"
    assert cleanliness_args.run_id == "batch-ch019-ch023-v1"
    assert cleanliness_args.chapter_id == ["ch019", "ch020"]

    provider_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "provider-usage",
        "--run-id", "batch-ch019-ch023-v1",
    ])
    assert provider_args.report_command == "provider-usage"
    assert provider_args.run_id == "batch-ch019-ch023-v1"

    glossary_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "glossary-decisions",
        "--run-id", "batch-ch019-ch023-v1",
    ])
    assert glossary_args.report_command == "glossary-decisions"
    assert glossary_args.run_id == "batch-ch019-ch023-v1"

    conflicts_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "glossary-conflicts",
        "--run-id", "batch-ch019-ch023-v1",
    ])
    assert conflicts_args.report_command == "glossary-conflicts"
    assert conflicts_args.run_id == "batch-ch019-ch023-v1"

    audit_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "glossary-audit",
        "--run-id", "batch-ch019-ch023-v1",
    ])
    assert audit_args.report_command == "glossary-audit"
    assert audit_args.run_id == "batch-ch019-ch023-v1"

    guard_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "glossary-guard",
        "--run-id", "batch-ch019-ch023-v1",
    ])
    assert guard_args.report_command == "glossary-guard"
    assert guard_args.run_id == "batch-ch019-ch023-v1"

    preflight_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "preflight",
    ])
    assert preflight_args.report_command == "preflight"

    recovery_args = parser.parse_args([
        "--config", "dummy.yaml",
        "report",
        "recovery-drill",
    ])
    assert recovery_args.report_command == "recovery-drill"

    operator_args = parser.parse_args([
        "--config", "dummy.yaml",
        "operator",
        "--run-id", "batch-ch019-ch023-v1",
        "--port", "8877",
    ])
    assert operator_args.command == "operator"
    assert operator_args.run_id == "batch-ch019-ch023-v1"
    assert operator_args.port == 8877


def test_cli_parser_accepts_init_novel():
    """CLI parser accepts init-novel scaffold arguments."""
    from novel_pipeline.cli import build_parser
    parser = build_parser()
    args = parser.parse_args([
        "--config", "dummy.yaml",
        "init-novel",
        "--project-root", r"D:\Temp\Example Novel",
        "--title", "Example Novel",
        "--source-url", "https://example.com/toc",
        "--novel-id", "example-novel",
        "--alias", "Example Alt",
        "--source-language", "zh",
        "--target-language", "th",
        "--genre", "horror",
        "--adapter", "piaotia",
        "--style-profile", "default",
    ])
    assert args.command == "init-novel"
    assert args.project_root == Path(r"D:\Temp\Example Novel")
    assert args.title == "Example Novel"
    assert args.source_url == "https://example.com/toc"
    assert args.novel_id == "example-novel"
    assert args.alias == ["Example Alt"]


def test_style_profile_from_mapping_parses_structured_fields_and_legacy_description():
    """Style profiles keep structured fields and still fall back to old description-only text."""
    from novel_pipeline.types import StyleProfile

    profile = StyleProfile.from_mapping(
        "deep_sea_embers",
        {
            "name": "deep-sea-embers-thai",
            "description": "Nautical dark fantasy style for Deep Sea Embers.",
            "genre_label": "dark fantasy",
            "tone": "eerie, mysterious",
            "naming_notes": "Keep ship names stable.",
            "narration_density": "moderate",
            "glossary_categories": ["character", "ship"],
            "qa_criteria": ["Preserve maritime dread", "Avoid cultivation diction"],
            "prose_guidelines": {"tone": "restrained"},
        },
    )
    assert profile.key == "deep_sea_embers"
    assert profile.name == "deep-sea-embers-thai"
    assert profile.genre_label == "dark fantasy"
    assert profile.tone == "eerie, mysterious"
    assert profile.naming_notes == "Keep ship names stable."
    assert profile.narration_density == "moderate"
    assert profile.glossary_categories == ("character", "ship")
    assert profile.qa_criteria == ("Preserve maritime dread", "Avoid cultivation diction")
    assert profile.metadata == {"prose_guidelines": {"tone": "restrained"}}
    assert profile.instruction_text() == (
        "Genre label: dark fantasy\n"
        "Tone: eerie, mysterious\n"
        "Naming notes: Keep ship names stable.\n"
        "Narration density: moderate\n"
        "Glossary categories: character, ship\n"
        "QA criteria: Preserve maritime dread; Avoid cultivation diction"
    )

    legacy = StyleProfile.from_mapping("legacy", {"name": "legacy-style", "description": "Legacy prose only."})
    assert legacy.instruction_text() == "Legacy prose only."


def test_research_profile_from_config_and_context_text():
    """Research profile YAML loads from the workspace root and renders concise context text."""
    import tempfile
    from novel_pipeline.config import load_app_config

    base = Path(tempfile.mkdtemp(prefix="novel-research-"))
    workspace_root = base / "workspace"
    system_root = workspace_root / ".system"
    system_root.mkdir(parents=True)
    (system_root / "config.yaml").write_text(
        """novel_id: research-novel
vault_root: .
source_language: zh
default_batch_size: 10
chapter_unit: chapters
default_style_profile: default
chunking:
  chinese_character_limit: 600
  non_chinese_word_limit: 5000
source:
  adapter: piaotia
  toc_url: https://example.com/toc
""",
        encoding="utf-8",
    )
    (system_root / "style_profiles.yaml").write_text(
        """default:
  name: default
  description: default style
""",
        encoding="utf-8",
    )
    (system_root / "providers.yaml").write_text(
        """literal_translation:
  provider: gemini
providers:
  gemini:
    executable: gemini
""",
        encoding="utf-8",
    )
    (workspace_root / "RESEARCH_PROFILE.yaml").write_text(
        """schema_version: 1
title: Deep Sea Embers
aliases:
  - 深海余烬
source_url: https://example.com/original
status: active
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
  - mystery
style_notes: Blend eerie maritime atmosphere with grounded reactions.
reader_expectations: Expect slow-burn reveals and practical protagonist logic.
review_summary: Reviews emphasize atmosphere, mystery, and immersive worldbuilding.
terminology:
  - ember
  - abyss
reference_links:
  - https://example.com/review
notes: Preserve ship names and source-linked canon.
""",
        encoding="utf-8",
    )

    config = load_app_config(system_root / "config.yaml")
    assert config.research_profile is not None
    assert config.research_profile.title == "Deep Sea Embers"
    assert config.research_profile.aliases == ("深海余烬",)
    assert config.research_profile.source_url == "https://example.com/original"
    assert config.research_profile.status == "active"
    assert config.research_context_text() == (
        "Title: Deep Sea Embers\n"
        "Aliases: 深海余烬\n"
        "Source URL: https://example.com/original\n"
        "Synopsis: Nautical dark fantasy with a slow-burn mystery.\n"
        "Tags: nautical dark fantasy, mystery\n"
        "Style notes: Blend eerie maritime atmosphere with grounded reactions.\n"
        "Reader expectations: Expect slow-burn reveals and practical protagonist logic.\n"
        "Review summary: Reviews emphasize atmosphere, mystery, and immersive worldbuilding.\n"
        "Terminology: ember, abyss\n"
        "Notes: Preserve ship names and source-linked canon."
    )


def _write_research_profile_test_workspace(base: Path, research_profile_text: str | None) -> Path:
    workspace_root = base / "workspace"
    system_root = workspace_root / ".system"
    system_root.mkdir(parents=True)
    (system_root / "config.yaml").write_text(
        """novel_id: research-novel
vault_root: .
source_language: zh
default_batch_size: 10
chapter_unit: chapters
default_style_profile: default
chunking:
  chinese_character_limit: 600
  non_chinese_word_limit: 5000
source:
  adapter: piaotia
  toc_url: https://example.com/toc
""",
        encoding="utf-8",
    )
    (system_root / "style_profiles.yaml").write_text(
        """default:
  name: default
  description: default style
""",
        encoding="utf-8",
    )
    (system_root / "providers.yaml").write_text(
        """literal_translation:
  provider: gemini
providers:
  gemini:
    executable: gemini
""",
        encoding="utf-8",
    )
    if research_profile_text is not None:
        (workspace_root / "RESEARCH_PROFILE.yaml").write_text(research_profile_text, encoding="utf-8")
    return system_root / "config.yaml"


def test_research_profile_readiness_classification():
    """Research profile readiness is status-aware and reports missing fields."""
    from novel_pipeline.types import ResearchProfile

    pending = ResearchProfile.from_mapping(
        {
            "title": "Deep Sea Embers",
            "source_url": "https://example.com/original",
            "status": "pending",
            "synopsis": "Nautical dark fantasy with a slow-burn mystery.",
            "tags": ["nautical dark fantasy", "mystery"],
            "style_notes": "Blend eerie maritime atmosphere with grounded reactions.",
            "reader_expectations": "Expect slow-burn reveals and practical protagonist logic.",
            "review_summary": "Reviews emphasize atmosphere, mystery, and immersive worldbuilding.",
            "terminology": ["ember", "abyss"],
            "reference_links": ["https://example.com/review"],
        }
    )
    pending_summary = pending.readiness_summary()
    assert pending_summary["status"] == "pending"
    assert pending_summary["readiness"] == "blocked"
    assert pending_summary["translation_ready"] is False
    assert pending_summary["bounded_translation_ready"] is False
    assert pending_summary["fetch_ready"] is True
    assert pending_summary["glossary_scan_ready"] is True
    assert pending_summary["required_fields"] == ["title", "source_url"]
    assert pending_summary["missing_fields"] == []
    assert pending_summary["next_safe_action"].startswith("Fill synopsis")

    drafted = ResearchProfile.from_mapping(
        {
            "title": "Deep Sea Embers",
            "source_url": "https://example.com/original",
            "status": "drafted",
            "synopsis": "Nautical dark fantasy with a slow-burn mystery.",
            "tags": ["nautical dark fantasy", "mystery"],
            "style_notes": "Blend eerie maritime atmosphere with grounded reactions.",
            "reader_expectations": "Expect slow-burn reveals and practical protagonist logic.",
            "review_summary": "Reviews emphasize atmosphere, mystery, and immersive worldbuilding.",
            "terminology": ["ember", "abyss"],
            "reference_links": ["https://example.com/review"],
        }
    )
    drafted_summary = drafted.readiness_summary()
    assert drafted_summary["status"] == "drafted"
    assert drafted_summary["readiness"] == "degraded"
    assert drafted_summary["translation_ready"] is False
    assert drafted_summary["bounded_translation_ready"] is True
    assert drafted_summary["required_fields"] == [
        "title",
        "source_url",
        "synopsis",
        "tags",
        "style_notes",
    ]
    assert drafted_summary["missing_fields"] == []
    assert drafted_summary["warnings"]

    active = ResearchProfile.from_mapping(
        {
            "title": "Deep Sea Embers",
            "source_url": "https://example.com/original",
            "status": "active",
            "synopsis": "Nautical dark fantasy with a slow-burn mystery.",
            "tags": ["nautical dark fantasy", "mystery"],
            "style_notes": "Blend eerie maritime atmosphere with grounded reactions.",
            "reader_expectations": "Expect slow-burn reveals and practical protagonist logic.",
            "review_summary": "Reviews emphasize atmosphere, mystery, and immersive worldbuilding.",
            "last_reviewed_at": "2026-04-29T00:00:00+07:00",
            "reviewed_by": "Codex",
            "terminology": ["ember", "abyss"],
            "reference_links": ["https://example.com/review"],
        }
    )
    active_summary = active.readiness_summary()
    assert active_summary["status"] == "active"
    assert active_summary["readiness"] == "ready"
    assert active_summary["translation_ready"] is True
    assert active_summary["bounded_translation_ready"] is True
    assert active_summary["required_fields"][-2:] == ["last_reviewed_at", "reviewed_by"]
    assert active_summary["review"] == {
        "last_reviewed_at": "2026-04-29T00:00:00+07:00",
        "reviewed_by": "Codex",
    }


def test_research_profile_missing_file_is_visible_but_not_blocking():
    """Missing research profile remains readable for old projects but is not translation-ready."""
    import tempfile
    from novel_pipeline.config import load_app_config

    base = Path(tempfile.mkdtemp(prefix="novel-research-missing-"))
    config_path = _write_research_profile_test_workspace(base, None)
    config = load_app_config(config_path)

    assert config.research_profile is None
    summary = config.research_readiness_summary()
    assert summary["status"] == "missing"
    assert summary["present"] is False
    assert summary["translation_ready"] is False
    assert summary["bounded_translation_ready"] is False
    assert summary["fetch_ready"] is True
    assert summary["glossary_scan_ready"] is True


def test_research_profile_config_loads_review_metadata():
    """Review metadata is preserved when the research profile is loaded."""
    import tempfile
    from novel_pipeline.config import load_app_config

    base = Path(tempfile.mkdtemp(prefix="novel-research-review-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/toc
status: active
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
  - mystery
style_notes: Blend eerie maritime atmosphere with grounded reactions.
reader_expectations: Expect slow-burn reveals and practical protagonist logic.
review_summary: Reviews emphasize atmosphere, mystery, and immersive worldbuilding.
last_reviewed_at: 2026-04-29T00:00:00+07:00
reviewed_by: Codex
terminology:
  - ember
  - abyss
reference_links:
  - https://example.com/review
""",
    )
    config = load_app_config(config_path)

    assert config.research_profile is not None
    assert config.research_profile.last_reviewed_at == "2026-04-29T00:00:00+07:00"
    assert config.research_profile.reviewed_by == "Codex"
    assert config.research_readiness_summary()["translation_ready"] is True


def test_research_profile_source_url_mismatch_blocks_translation_readiness():
    """A drafted profile anchored to a different source URL is not translation-ready."""
    import tempfile
    from novel_pipeline.config import load_app_config

    base = Path(tempfile.mkdtemp(prefix="novel-research-mismatch-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/original
status: drafted
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
style_notes: Blend eerie maritime atmosphere with grounded reactions.
""",
    )
    config = load_app_config(config_path)

    summary = config.research_readiness_summary()
    assert summary["status"] == "drafted"
    assert summary["bounded_translation_ready"] is False
    assert summary["translation_ready"] is False
    assert any("source_url does not match" in item for item in summary["blocking_reasons"])


def test_research_profile_invalid_status_rejected():
    """Invalid research profile status is rejected by config loading."""
    import tempfile
    from novel_pipeline.config import ConfigError, load_app_config

    base = Path(tempfile.mkdtemp(prefix="novel-research-invalid-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/toc
status: archived
""",
    )

    try:
        load_app_config(config_path)
        assert False, "Expected ConfigError for invalid research profile status"
    except ConfigError as exc:
        assert "Invalid research profile" in str(exc)


def test_build_preflight_summary_reports_provider_and_git_state():
    """Preflight summary reports missing providers and git warnings without crashing."""
    import tempfile
    from unittest.mock import Mock, patch

    from novel_pipeline.preflight import build_preflight_summary
    from novel_pipeline.types import AppConfig, BatchDefaults, ChunkingPolicy, ProviderSpec, ResearchProfile, SourceConfig, StageRouting, StyleProfile, WorkspacePaths

    workspace_root = Path(tempfile.mkdtemp(prefix="novel-preflight-"))
    for name in [".system", "01_Glossary", "03_Raw", "04_Work", "05_Output", "06_Logs", "07_Reports"]:
        (workspace_root / name).mkdir(parents=True, exist_ok=True)
    config = AppConfig(
        config_path=workspace_root / ".system" / "config.yaml",
        workspace=WorkspacePaths.from_root(workspace_root),
        novel_id="test-novel",
        vault_root=workspace_root,
        source_language="zh",
        default_style_profile="default",
        batch=BatchDefaults(),
        chunking=ChunkingPolicy(),
        research_profile=ResearchProfile.from_mapping(
            {
                "title": "Test Novel",
                "source_url": "https://example.com/toc",
                "status": "drafted",
                "synopsis": "Synopsis",
                "tags": ["mystery"],
                "style_notes": "Keep the tone restrained.",
            }
        ),
        source=SourceConfig(adapter="piaotia", toc_url="https://example.com/toc"),
        providers={
            "gemini": ProviderSpec(name="gemini", executable=("missing-gemini",)),
        },
        stage_routing={
            "literal_translation": StageRouting(stage="literal_translation", provider="gemini"),
        },
        style_profiles={"default": StyleProfile(key="default", name="default", description="default")},
        raw_config={},
    )

    with patch("novel_pipeline.preflight.shutil.which", side_effect=lambda name: None if name == "missing-gemini" else "C:/git.exe"), \
         patch("novel_pipeline.preflight._git_capture", side_effect=[(True, "true"), (True, "main"), (True, "abc1234"), (True, "https://example.com/repo.git"), (True, " M test.txt")]):
        summary = build_preflight_summary(config)

    assert summary["status"] == "blocked"
    assert summary["providers"][0]["provider"] == "gemini"
    assert summary["providers"][0]["found"] is False
    assert any("Provider executable not found" in item for item in summary["blocking_reasons"])
    assert summary["git"]["in_work_tree"] is True
    assert summary["git"]["clean"] is False
    assert any("Working tree is dirty" in item for item in summary["warnings"])


def test_build_preflight_summary_ignores_generated_report_changes():
    """Generated report churn should not degrade an otherwise ready workspace."""
    import tempfile
    from unittest.mock import patch

    from novel_pipeline.preflight import build_preflight_summary
    from novel_pipeline.types import AppConfig, BatchDefaults, ChunkingPolicy, ProviderSpec, ResearchProfile, SourceConfig, StageRouting, StyleProfile, WorkspacePaths

    workspace_root = Path(tempfile.mkdtemp(prefix="novel-preflight-ignore-reports-"))
    for name in [".system", "01_Glossary", "03_Raw", "04_Work", "05_Output", "06_Logs", "07_Reports"]:
        (workspace_root / name).mkdir(parents=True, exist_ok=True)
    config = AppConfig(
        config_path=workspace_root / ".system" / "config.yaml",
        workspace=WorkspacePaths.from_root(workspace_root),
        novel_id="test-novel",
        vault_root=workspace_root,
        source_language="zh",
        default_style_profile="default",
        batch=BatchDefaults(),
        chunking=ChunkingPolicy(),
        research_profile=ResearchProfile.from_mapping(
            {
                "title": "Test Novel",
                "source_url": "https://example.com/toc",
                "status": "active",
                "synopsis": "Synopsis",
                "tags": ["mystery"],
                "style_notes": "Keep the tone restrained.",
                "last_reviewed_at": "2026-05-10",
                "reviewed_by": "tester",
            }
        ),
        source=SourceConfig(adapter="piaotia", toc_url="https://example.com/toc"),
        providers={
            "gemini": ProviderSpec(name="gemini", executable=("gemini",)),
        },
        stage_routing={
            "literal_translation": StageRouting(stage="literal_translation", provider="gemini"),
        },
        style_profiles={"default": StyleProfile(key="default", name="default", description="default")},
        raw_config={},
    )

    git_status = "\n".join(
        [
            "M 07_Reports/preflight_report.md",
            " M 07_Reports/product_review_batch-ch019-ch023-v1.md",
        ]
    )
    with patch("novel_pipeline.preflight.shutil.which", return_value="C:/tool.exe"), \
         patch(
             "novel_pipeline.preflight._git_capture",
             side_effect=[(True, "true"), (True, "main"), (True, "abc1234"), (True, "https://example.com/repo.git"), (True, git_status)],
         ):
        summary = build_preflight_summary(config)

    assert summary["status"] == "ready"
    assert summary["git"]["clean"] is True
    assert summary["warnings"] == []
    assert summary["git"]["ignored_generated_changes"] == [
        "07_Reports/preflight_report.md",
        "07_Reports/product_review_batch-ch019-ch023-v1.md",
    ]


def test_preflight_report_generation_writes_expected_markdown():
    from novel_pipeline.reports import build_preflight_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile

    summary = {
        "status": "degraded",
        "workspace_root": "D:/Novel/Deep Sea Embers",
        "config_path": "D:/Novel/Deep Sea Embers/.system/config.yaml",
        "providers": [
            {
                "provider": "claude",
                "status": "ready",
                "resolved_path": "C:/claude.exe",
                "prompt_transport": "stdin",
                "stages": ["refining"],
                "working_dir": "",
            },
            {
                "provider": "gemini",
                "status": "blocked",
                "resolved_path": "gemini",
                "prompt_transport": "argv",
                "stages": ["translating"],
                "working_dir": "",
            },
        ],
        "git": {
            "available": True,
            "in_work_tree": True,
            "branch": "main",
            "head": "abc1234",
            "origin": "https://example.com/repo.git",
            "clean": False,
            "warnings": ["Working tree is dirty."],
            "ignored_generated_changes": [],
        },
        "research_readiness": {
            "status": "drafted",
            "readiness": "degraded",
            "bounded_translation_ready": True,
            "translation_ready": False,
            "missing_fields": [],
            "warnings": ["review metadata missing"],
            "blocking_reasons": [],
            "next_safe_action": "Continue only with bounded operations.",
        },
        "missing_directories": [],
        "warnings": ["Working tree is dirty; commit or stash before large write actions."],
        "blocking_reasons": [],
        "next_safe_action": "Continue only with bounded operations while warnings remain.",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock(spec=AppConfig)
        config.workspace.root = base

        with patch("novel_pipeline.reports.build_preflight_summary", return_value=summary):
            result = build_preflight_report(config=config)

        text = result["path"].read_text(encoding="utf-8")
        assert "# Preflight Report" in text
        assert "- status: degraded" in text
        assert "| claude | ready | C:/claude.exe | stdin | refining | none |" in text
        assert "| gemini | blocked | gemini | argv | translating | none |" in text
        assert "- branch: main" in text
        assert "- ignored_generated_changes: none" in text
        assert "- readiness: degraded" in text
        assert result["actionable_failure"] is True


def test_recovery_drill_report_generation_writes_expected_markdown():
    from novel_pipeline.reports import build_recovery_drill_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock(spec=AppConfig)
        config.workspace.root = base

        responses = {
            ("rev-parse", "--is-inside-work-tree"): (True, "true"),
            ("branch", "--show-current"): (True, "main"),
            ("rev-parse", "--short", "HEAD"): (True, "abc1234"),
            ("remote", "get-url", "origin"): (True, "https://example.com/repo.git"),
            ("ls-files", "--error-unmatch", "PROJECT_BRAIN.md"): (True, "PROJECT_BRAIN.md"),
            ("show", "HEAD:PROJECT_BRAIN.md"): (True, "brain"),
            ("ls-files", "--error-unmatch", "IMPLEMENT_PLAN.md"): (True, "IMPLEMENT_PLAN.md"),
            ("show", "HEAD:IMPLEMENT_PLAN.md"): (True, "plan"),
            ("ls-files", "--error-unmatch", "OPERATOR_MANUAL.md"): (True, "OPERATOR_MANUAL.md"),
            ("show", "HEAD:OPERATOR_MANUAL.md"): (True, "manual"),
            ("check-ignore", "03_Raw"): (True, "03_Raw"),
            ("ls-files", "03_Raw"): (True, ""),
            ("check-ignore", "04_Work"): (True, "04_Work"),
            ("ls-files", "04_Work"): (True, ""),
            ("check-ignore", "05_Output"): (True, "05_Output"),
            ("ls-files", "05_Output"): (True, ""),
            ("check-ignore", "06_Logs"): (True, "06_Logs"),
            ("ls-files", "06_Logs"): (True, ""),
        }

        def fake_git_capture(workspace_root, *args):
            return responses[args]

        with patch("novel_pipeline.reports._git_capture", side_effect=fake_git_capture):
            result = build_recovery_drill_report(config=config)

        text = result["path"].read_text(encoding="utf-8")
        assert "# Recovery Drill Report" in text
        assert "- overall_status: accepted" in text
        assert "| canonical_docs_restorable | ok | all canonical docs tracked and restorable from HEAD |" in text
        assert "| runtime_dirs_ignored | ok | runtime directories are ignored and untracked |" in text
        assert "| PROJECT_BRAIN.md | yes | yes | tracked and restorable |" in text
        assert "| 03_Raw | yes | 0 | ignored and untracked |" in text
        assert result["actionable_failure"] is False


def test_initialize_novel_project_scaffolds_expected_files_and_rewrites_codex_cd():
    """init-novel scaffold creates an isolated project without code edits."""
    import tempfile
    import yaml
    from novel_pipeline.config import load_app_config
    from novel_pipeline.project_setup import initialize_novel_project

    base = Path(tempfile.mkdtemp(prefix="novel-init-"))
    source_root = base / "source-workspace"
    (source_root / ".system").mkdir(parents=True)
    (source_root / "prompts").mkdir()
    (source_root / "00_Templates").mkdir()
    (source_root / "prompts" / "literal_translation.md").write_text("prompt", encoding="utf-8")
    (source_root / "00_Templates" / "Term-Template.md").write_text("template", encoding="utf-8")
    (source_root / "00_Templates" / "Research-Profile.yaml").write_text(
        """schema_version: 1
title: Your Novel Title
aliases:
  - Alternate Title
source_url: https://example.com/original-source
status: pending
synopsis: ""
tags: []
style_notes: ""
reader_expectations: ""
review_summary: ""
terminology: []
reference_links: []
notes: ""
""",
        encoding="utf-8",
    )
    (source_root / ".system" / "config.yaml").write_text(
        """novel_id: template-workspace
vault_root: .
source_language: zh
default_batch_size: 10
chapter_unit: chapters
default_style_profile: default
chunking:
  chinese_character_limit: 600
  non_chinese_word_limit: 5000
source:
  adapter: piaotia
  toc_url: https://example.com/template
  delay_seconds: 1.0
  encoding: gbk
""",
        encoding="utf-8",
    )
    (source_root / ".system" / "style_profiles.yaml").write_text(
        """default:
  name: default
  description: default style
""",
        encoding="utf-8",
    )
    (source_root / ".system" / "providers.yaml").write_text(
        f"""literal_translation:
  provider: gemini
  model: pro
providers:
  gemini:
    executable: gemini
  codex:
    executable:
      - codex
      - exec
    prompt_flag: "-"
    prompt_position: positional
    prompt_transport: stdin
    model_flag: -m
    model_position: before_prompt
    extra_args:
      - --skip-git-repo-check
      - --cd
      - {source_root}
      - --sandbox
      - read-only
""",
        encoding="utf-8",
    )

    config = load_app_config(source_root / ".system" / "config.yaml")
    target_root = base / "target-workspace"
    result = initialize_novel_project(
        template_config=config,
        project_root=target_root,
        title="Second Novel",
        source_url="https://example.com/second/toc",
        novel_id="second-novel",
        aliases=["Second Alt"],
        source_language="zh",
        target_language="th",
        genre="dark fantasy",
        adapter="piaotia",
        style_profile="default",
    )

    assert result["project_root"] == target_root.resolve()
    assert (target_root / "NOVEL_PROFILE.yaml").exists()
    assert (target_root / "RESEARCH_PROFILE.yaml").exists()
    assert (target_root / ".system" / "config.yaml").exists()
    assert (target_root / ".system" / "providers.yaml").exists()
    assert (target_root / "prompts" / "literal_translation.md").exists()
    assert (target_root / "00_Templates" / "Term-Template.md").exists()
    assert (target_root / "00_Templates" / "Research-Profile.yaml").exists()

    profile_payload = yaml.safe_load((target_root / "NOVEL_PROFILE.yaml").read_text(encoding="utf-8"))
    assert profile_payload["novel_id"] == "second-novel"
    assert profile_payload["title"] == "Second Novel"
    assert profile_payload["aliases"] == ["Second Alt"]
    assert profile_payload["source"]["toc_url"] == "https://example.com/second/toc"
    assert profile_payload["research"]["profile_path"] == "RESEARCH_PROFILE.yaml"

    research_payload = yaml.safe_load((target_root / "RESEARCH_PROFILE.yaml").read_text(encoding="utf-8"))
    assert research_payload["title"] == "Second Novel"
    assert research_payload["aliases"] == ["Second Alt"]
    assert research_payload["source_url"] == "https://example.com/second/toc"
    assert research_payload["status"] == "pending"
    assert research_payload["last_reviewed_at"] == ""
    assert research_payload["reviewed_by"] == ""

    providers_payload = yaml.safe_load((target_root / ".system" / "providers.yaml").read_text(encoding="utf-8"))
    extra_args = providers_payload["providers"]["codex"]["extra_args"]
    assert str(target_root.resolve()) in extra_args
    assert str(source_root.resolve()) not in extra_args

    generated_config = load_app_config(target_root / ".system" / "config.yaml")
    assert generated_config.novel_id == "second-novel"
    assert generated_config.workspace.root == target_root.resolve()


def test_initialize_novel_project_selects_style_profile_from_genre_or_default():
    """init-novel resolves explicit style, genre presets, and default fallback in that order."""
    import tempfile
    import yaml
    from novel_pipeline.config import load_app_config
    from novel_pipeline.project_setup import initialize_novel_project

    base = Path(tempfile.mkdtemp(prefix="novel-style-"))
    source_root = base / "source-workspace"
    (source_root / ".system").mkdir(parents=True)
    (source_root / "prompts").mkdir()
    (source_root / "00_Templates").mkdir()
    (source_root / ".system" / "config.yaml").write_text(
        """novel_id: template-workspace
vault_root: .
source_language: zh
default_batch_size: 10
chapter_unit: chapters
default_style_profile: default
chunking:
  chinese_character_limit: 600
  non_chinese_word_limit: 5000
source:
  adapter: piaotia
  toc_url: https://example.com/template
  delay_seconds: 1.0
  encoding: gbk
""",
        encoding="utf-8",
    )
    (source_root / ".system" / "style_profiles.yaml").write_text(
        """default:
  name: standard-thai-novel
  description: Neutral polished Thai prose.
  genre_label: general fiction
dark_fantasy:
  name: dark-fantasy-thai
  description: Gloomy Thai prose.
  genre_label: dark fantasy
sci_fi:
  name: sci-fi-thai
  description: Clean Thai prose for science fiction.
  genre_label: science fiction
deep_sea_embers:
  name: deep-sea-embers-thai
  description: Nautical dark fantasy style for Deep Sea Embers.
  genre_label: dark fantasy
""",
        encoding="utf-8",
    )
    (source_root / ".system" / "providers.yaml").write_text(
        """refinement:
  provider: gemini
providers:
  gemini:
    executable: gemini
""",
        encoding="utf-8",
    )

    config = load_app_config(source_root / ".system" / "config.yaml")

    genre_target = base / "genre-project"
    initialize_novel_project(
        template_config=config,
        project_root=genre_target,
        title="Genre Novel",
        source_url="https://example.com/genre/toc",
        genre="Sci-Fi",
        adapter="piaotia",
    )
    genre_config = load_app_config(genre_target / ".system" / "config.yaml")
    genre_profile = yaml.safe_load((genre_target / "NOVEL_PROFILE.yaml").read_text(encoding="utf-8"))
    assert genre_config.default_style_profile == "sci_fi"
    assert genre_profile["style_profile"] == "sci_fi"

    explicit_target = base / "explicit-project"
    initialize_novel_project(
        template_config=config,
        project_root=explicit_target,
        title="Explicit Novel",
        source_url="https://example.com/explicit/toc",
        genre="Sci-Fi",
        adapter="piaotia",
        style_profile="deep_sea_embers",
    )
    explicit_config = load_app_config(explicit_target / ".system" / "config.yaml")
    explicit_profile = yaml.safe_load((explicit_target / "NOVEL_PROFILE.yaml").read_text(encoding="utf-8"))
    assert explicit_config.default_style_profile == "deep_sea_embers"
    assert explicit_profile["style_profile"] == "deep_sea_embers"

    fallback_target = base / "fallback-project"
    initialize_novel_project(
        template_config=config,
        project_root=fallback_target,
        title="Fallback Novel",
        source_url="https://example.com/fallback/toc",
        genre="Mystery",
        adapter="piaotia",
    )
    fallback_config = load_app_config(fallback_target / ".system" / "config.yaml")
    fallback_profile = yaml.safe_load((fallback_target / "NOVEL_PROFILE.yaml").read_text(encoding="utf-8"))
    assert fallback_config.default_style_profile == "default"
    assert fallback_profile["style_profile"] == "default"


def test_refine_stage_uses_structured_style_instructions():
    """Refinement prompt wiring passes structured style instructions through to the template."""
    from novel_pipeline.stages.refine import run_refine_stage
    from novel_pipeline.types import LiteralDraft, LiteralSentencePair, StyleProfile, TextBlock

    profile = StyleProfile.from_mapping(
        "deep_sea_embers",
        {
            "name": "deep-sea-embers-thai",
            "genre_label": "dark fantasy",
            "tone": "eerie, mysterious, atmospheric",
            "naming_notes": "Keep ship and place names stable.",
            "narration_density": "moderate",
            "glossary_categories": ["character", "ship"],
            "qa_criteria": ["Preserve maritime dread", "Avoid cultivation diction"],
        },
    )
    config = Mock()
    config.workspace.prompts = Path("prompts")
    config.style_profile_for_name = Mock(return_value=profile)
    block = TextBlock(block_id="ch001-block-001", chapter_id="ch001", source_text="原文。")
    literal_draft = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(LiteralSentencePair(source_sentence="原文。", literal_sentence="สวัสดีครับ"),),
    )
    provider_runner = Mock()
    provider_runner.spec.name = "claude"
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="claude",
        command=("claude",),
        stdout="สวัสดีครับ",
        returncode=0,
    )

    with patch("novel_pipeline.stages.refine.PromptStore.render", return_value="refine prompt") as mock_render:
        result = run_refine_stage(
            config=config,
            block=block,
            literal_draft=literal_draft,
            glossary_subset=[],
            style_profile_key="deep_sea_embers",
            provider_runner=provider_runner,
        )

    assert result.style_profile == "deep_sea_embers"
    config.style_profile_for_name.assert_called_once_with("deep_sea_embers")
    assert mock_render.call_args.kwargs["style_instructions"] == profile.instruction_text()


def test_qa_stage_uses_structured_style_instructions():
    """QA prompt wiring passes structured style instructions through to the template."""
    from novel_pipeline.stages.qa import run_qa_stage
    from novel_pipeline.types import LiteralDraft, LiteralSentencePair, RefinedDraft, StyleProfile, TextBlock

    profile = StyleProfile.from_mapping(
        "deep_sea_embers",
        {
            "name": "deep-sea-embers-thai",
            "genre_label": "dark fantasy",
            "tone": "eerie, mysterious, atmospheric",
            "naming_notes": "Keep ship and place names stable.",
            "narration_density": "moderate",
            "glossary_categories": ["character", "ship"],
            "qa_criteria": ["Preserve maritime dread", "Avoid cultivation diction"],
        },
    )
    config = Mock()
    config.workspace.prompts = Path("prompts")
    config.style_profile_for_name = Mock(return_value=profile)
    block = TextBlock(block_id="ch001-block-001", chapter_id="ch001", source_text="原文。")
    literal_draft = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(LiteralSentencePair(source_sentence="原文。", literal_sentence="สวัสดีครับ"),),
    )
    refined_draft = RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text="สวัสดีครับ",
    )
    provider_runner = Mock()
    provider_runner.spec.name = "claude"
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="claude",
        command=("claude",),
        stdout="PASS: faithful translation with no omissions.",
        returncode=0,
    )

    with patch("novel_pipeline.stages.qa.PromptStore.render", return_value="qa prompt") as mock_render:
        report = run_qa_stage(
            config=config,
            block=block,
            literal_draft=literal_draft,
            refined_draft=refined_draft,
            glossary_subset=[],
            provider_runner=provider_runner,
            model="",
            retry_count=0,
            style_profile_key="deep_sea_embers",
        )

    assert report.passed is True
    config.style_profile_for_name.assert_called_once_with("deep_sea_embers")
    assert mock_render.call_args.kwargs["style_instructions"] == profile.instruction_text()


def test_literal_translation_stage_uses_research_context():
    """Literal translation prompt wiring passes research context through to the template."""
    from novel_pipeline.stages.translate import run_literal_translation_stage
    from novel_pipeline.types import GlossaryEntry, TextBlock

    research_context = "Title: Deep Sea Embers\nSource URL: https://example.com/original"
    config = Mock()
    config.workspace.prompts = Path("prompts")
    config.research_context_text = Mock(return_value=research_context)
    block = TextBlock(block_id="ch001-block-001", chapter_id="ch001", source_text="原文。", source_language="zh")
    provider_runner = Mock()
    provider_runner.spec.name = "gemini"
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="gemini",
        command=("gemini",),
        stdout="สวัสดี",
        returncode=0,
    )

    with patch("novel_pipeline.stages.translate.PromptStore.render", return_value="literal prompt") as mock_render:
        result = run_literal_translation_stage(
            config=config,
            block=block,
            glossary_subset=[GlossaryEntry(original_term="原文", thai_term="ต้นฉบับ", category="term")],
            provider_runner=provider_runner,
        )

    assert result.provider == "gemini"
    assert mock_render.call_args.kwargs["research_context"] == research_context


def test_refine_stage_uses_research_context():
    """Refinement prompt wiring passes research context through to the template."""
    from novel_pipeline.stages.refine import run_refine_stage
    from novel_pipeline.types import LiteralDraft, LiteralSentencePair, StyleProfile, TextBlock

    profile = StyleProfile.from_mapping(
        "deep_sea_embers",
        {
            "name": "deep-sea-embers-thai",
            "genre_label": "dark fantasy",
            "tone": "eerie, mysterious, atmospheric",
            "naming_notes": "Keep ship and place names stable.",
            "narration_density": "moderate",
            "glossary_categories": ["character", "ship"],
            "qa_criteria": ["Preserve maritime dread", "Avoid cultivation diction"],
        },
    )
    research_context = "Title: Deep Sea Embers\nSource URL: https://example.com/original"
    config = Mock()
    config.workspace.prompts = Path("prompts")
    config.style_profile_for_name = Mock(return_value=profile)
    config.research_context_text = Mock(return_value=research_context)
    block = TextBlock(block_id="ch001-block-001", chapter_id="ch001", source_text="原文。")
    literal_draft = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(LiteralSentencePair(source_sentence="原文。", literal_sentence="สวัสดีครับ"),),
    )
    provider_runner = Mock()
    provider_runner.spec.name = "claude"
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="claude",
        command=("claude",),
        stdout="สวัสดีครับ",
        returncode=0,
    )

    with patch("novel_pipeline.stages.refine.PromptStore.render", return_value="refine prompt") as mock_render:
        result = run_refine_stage(
            config=config,
            block=block,
            literal_draft=literal_draft,
            glossary_subset=[],
            style_profile_key="deep_sea_embers",
            provider_runner=provider_runner,
        )

    assert result.style_profile == "deep_sea_embers"
    assert mock_render.call_args.kwargs["research_context"] == research_context


def test_qa_stage_uses_research_context():
    """QA prompt wiring passes research context through to the template."""
    from novel_pipeline.stages.qa import run_qa_stage
    from novel_pipeline.types import LiteralDraft, LiteralSentencePair, RefinedDraft, StyleProfile, TextBlock

    profile = StyleProfile.from_mapping(
        "deep_sea_embers",
        {
            "name": "deep-sea-embers-thai",
            "genre_label": "dark fantasy",
            "tone": "eerie, mysterious, atmospheric",
            "naming_notes": "Keep ship and place names stable.",
            "narration_density": "moderate",
            "glossary_categories": ["character", "ship"],
            "qa_criteria": ["Preserve maritime dread", "Avoid cultivation diction"],
        },
    )
    research_context = "Title: Deep Sea Embers\nSource URL: https://example.com/original"
    config = Mock()
    config.workspace.prompts = Path("prompts")
    config.style_profile_for_name = Mock(return_value=profile)
    config.research_context_text = Mock(return_value=research_context)
    block = TextBlock(block_id="ch001-block-001", chapter_id="ch001", source_text="原文。")
    literal_draft = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=(LiteralSentencePair(source_sentence="原文。", literal_sentence="สวัสดีครับ"),),
    )
    refined_draft = RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text="สวัสดีครับ",
    )
    provider_runner = Mock()
    provider_runner.spec.name = "claude"
    provider_runner.run_with_retry.return_value = ProviderResponse(
        provider="claude",
        command=("claude",),
        stdout="PASS: faithful translation with no omissions.",
        returncode=0,
    )

    with patch("novel_pipeline.stages.qa.PromptStore.render", return_value="qa prompt") as mock_render:
        report = run_qa_stage(
            config=config,
            block=block,
            literal_draft=literal_draft,
            refined_draft=refined_draft,
            glossary_subset=[],
            provider_runner=provider_runner,
            model="",
            retry_count=0,
            style_profile_key="deep_sea_embers",
        )

    assert report.passed is True
    assert mock_render.call_args.kwargs["research_context"] == research_context


def test_cmd_resume_returns_two_on_manual_action_required():
    """cmd_resume returns 2 when manual action is required."""
    from novel_pipeline.cli import cmd_resume
    from novel_pipeline.pipeline import ManualActionRequired
    from unittest.mock import Mock, patch
    from io import StringIO
    import sys

    config = Mock()
    config.ledger_path = Mock()
    config.ensure_translation_ready.return_value = {"readiness": "ready"}

    args = Mock(
        run_id="batch-ch019-ch023-v1",
        force=False,
        manual_action_mode="stop",
        until_chapter=None,
        until_block=None,
    )

    stderr = StringIO()
    original_stderr = sys.stderr
    try:
        sys.stderr = stderr
        with patch("novel_pipeline.cli.resume_pipeline", side_effect=ManualActionRequired("Manual action required for block ch019-block-003 at stage 'qa'.")) as mock_resume:
            result = cmd_resume(args, config)
            config.ensure_translation_ready.assert_called_once_with(bounded=False)
            mock_resume.assert_called_once_with(
                config=config,
                run_id="batch-ch019-ch023-v1",
                force=False,
                manual_action_mode="stop",
                until_chapter=None,
                until_block=None,
            )
    finally:
        sys.stderr = original_stderr

    assert result == 2
    assert "[MANUAL ACTION REQUIRED]" in stderr.getvalue()


def test_cmd_preflight_returns_one_when_blocked():
    from argparse import Namespace

    from novel_pipeline.cli import cmd_preflight

    config = Mock()
    args = Namespace(json=False)

    with patch("novel_pipeline.cli.build_preflight_summary", return_value={"blocking_reasons": ["blocked"], "status": "blocked"}), \
         patch("novel_pipeline.cli.print_preflight_summary") as print_mock:
        assert cmd_preflight(args, config) == 1
        print_mock.assert_called_once()


def test_resume_pipeline_stops_before_chapter_after_until_chapter():
    """resume_pipeline batch mode stops before chapters after until_chapter."""
    from novel_pipeline.pipeline import resume_pipeline
    from novel_pipeline.ledger import ResumeState
    from novel_pipeline.types import RunRecord
    from unittest.mock import Mock, patch

    config = Mock()
    config.ledger_path = Mock()
    config.workspace.logs_dir = Mock()
    config.workspace.prompts = Mock()
    config.workspace.raw = Mock()
    config.workspace.output = Mock()
    config.workspace.glossary_dir = Mock()

    state = ResumeState(
        run_id="batch-ch019-ch023-v1",
        records=(
            RunRecord.new(
                run_id="batch-ch019-ch023-v1",
                block_id="ch019",
                stage="fetched",
                status="completed",
                provider="local",
            ),
        ),
        latest_by_block={
            "ch019": RunRecord.new(
                run_id="batch-ch019-ch023-v1",
                block_id="ch019",
                stage="fetched",
                status="completed",
                provider="local",
            ),
        },
        latest_by_stage={
            ("ch019", "fetched"): RunRecord.new(
                run_id="batch-ch019-ch023-v1",
                block_id="ch019",
                stage="fetched",
                status="completed",
                provider="local",
            ),
        },
        records_by_block={
            "ch019": [
                RunRecord.new(
                    run_id="batch-ch019-ch023-v1",
                    block_id="ch019",
                    stage="fetched",
                    status="completed",
                    provider="local",
                )
            ],
        },
    )

    mock_ledger = Mock()
    mock_ledger.load_state.return_value = state

    with patch("novel_pipeline.pipeline.RunLedger", return_value=mock_ledger), \
         patch("novel_pipeline.pipeline.PromptStore"), \
         patch("novel_pipeline.pipeline._load_or_create_glossary_index", return_value={}), \
         patch("novel_pipeline.pipeline._get_batch_chapter_ids", return_value=["ch019", "ch020", "ch021"]), \
         patch("novel_pipeline.pipeline._resume_chapter", return_value=False) as mock_resume:
        resume_pipeline(
            config=config,
            run_id="batch-ch019-ch023-v1",
            until_chapter="ch020",
        )

    chapters = [call.kwargs["chapter_id"] for call in mock_resume.call_args_list]
    assert chapters == ["ch019", "ch020"]


def test_resume_chapter_stops_after_until_block():
    """_resume_chapter stops before blocks after until_block."""
    from novel_pipeline.pipeline import _resume_chapter
    from novel_pipeline.ledger import ResumeState
    from novel_pipeline.types import TextBlock
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    chapter_id = "ch019"
    until_block = "ch019-block-002"
    block1 = TextBlock(block_id="ch019-block-001", chapter_id=chapter_id, source_text="a", source_language="zh")
    block2 = TextBlock(block_id="ch019-block-002", chapter_id=chapter_id, source_text="b", source_language="zh")
    block3 = TextBlock(block_id="ch019-block-003", chapter_id=chapter_id, source_text="c", source_language="zh")
    state = ResumeState(run_id="batch-ch019-ch023-v1")

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock()
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"
        config.workspace.raw = base / "03_Raw"
        config.workspace.prompts = base / "prompts"
        config.workspace.templates_dir = base / "00_Templates"
        config.workspace.glossary_dir = base / "01_Glossary"
        config.workspace.output = base / "05_Output"
        config.default_style_profile = "default"
        config.source_language = "zh"
        config.chunking.chinese_character_limit = 600
        config.chunking.non_chinese_word_limit = 300
        config.novel_id = "test"

        source_payload = json.dumps({
            "novel_id": "test",
            "chapter_id": chapter_id,
            "title": "Chapter",
            "source_language": "zh",
            "raw_text": "dummy",
        })

        mock_ledger = Mock()
        mock_ledger.has_committed.side_effect = lambda **kwargs: kwargs.get("stage") in {"glossary_scanned", "glossary_approved"}

        with patch("novel_pipeline.pipeline.read_text_if_exists", return_value=source_payload), \
             patch("novel_pipeline.pipeline.PromptStore"), \
             patch("novel_pipeline.pipeline.split_blocks", return_value=[block1, block2, block3]), \
             patch("novel_pipeline.pipeline._load_or_create_glossary_index", return_value={}), \
             patch("novel_pipeline.pipeline._process_block", side_effect=lambda ctx, block, style_key, force=False, force_from_stage=None, manual_action_mode="interactive": f"formatted-{block.block_id}") as mock_process, \
             patch("novel_pipeline.pipeline._write_chapter_output") as mock_write:
            stopped = _resume_chapter(
                config=config,
                ledger=mock_ledger,
                run_id="batch-ch019-ch023-v1",
                chapter_id=chapter_id,
                glossary_index={},
                state=state,
                until_block=until_block,
            )

        assert stopped is True
        assert [call.args[1].block_id for call in mock_process.call_args_list] == ["ch019-block-001", "ch019-block-002"]
        mock_write.assert_called_once()


def test_resume_chapter_stops_after_completed_until_block():
    """_resume_chapter treats an already-complete until_block as found and stops after it."""
    from novel_pipeline.pipeline import _resume_chapter
    from novel_pipeline.ledger import ResumeState
    from novel_pipeline.types import RunRecord, TextBlock
    from unittest.mock import Mock, patch
    import json
    import tempfile
    from pathlib import Path

    run_id = "batch-ch019-ch023-v1"
    chapter_id = "ch019"
    until_block = "ch019-block-002"
    block1 = TextBlock(block_id="ch019-block-001", chapter_id=chapter_id, source_text="a", source_language="zh")
    block2 = TextBlock(block_id=until_block, chapter_id=chapter_id, source_text="b", source_language="zh")
    block3 = TextBlock(block_id="ch019-block-003", chapter_id=chapter_id, source_text="c", source_language="zh")
    stage_order = ["translating", "refining", "qa", "formatting", "completed"]
    records = tuple(
        RunRecord.new(run_id=run_id, block_id=block.block_id, stage=stage, status="completed", provider="local")
        for block in (block1, block2)
        for stage in stage_order
    )
    state = ResumeState(
        run_id=run_id,
        records=records,
        latest_by_stage={
            (record.block_id, record.stage): record
            for record in records
        },
        records_by_block={
            block.block_id: [record for record in records if record.block_id == block.block_id]
            for block in (block1, block2)
        },
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock()
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"
        config.workspace.raw = base / "03_Raw"
        config.workspace.prompts = base / "prompts"
        config.workspace.templates_dir = base / "00_Templates"
        config.workspace.glossary_dir = base / "01_Glossary"
        config.workspace.output = base / "05_Output"
        config.default_style_profile = "default"
        config.source_language = "zh"
        config.chunking.chinese_character_limit = 600
        config.chunking.non_chinese_word_limit = 300
        config.novel_id = "test"

        source_payload = json.dumps({
            "novel_id": "test",
            "chapter_id": chapter_id,
            "title": "Chapter",
            "source_language": "zh",
            "raw_text": "dummy",
        })

        mock_ledger = Mock()
        mock_ledger.has_committed.side_effect = (
            lambda **kwargs: kwargs.get("stage") in {"glossary_scanned", "glossary_approved"}
        )

        def fake_read_artifact(config, chapter_id, block_id, stage):
            if stage == "formatted":
                return {"text": f"formatted-{block_id}"}
            return None

        with patch("novel_pipeline.pipeline.read_text_if_exists", return_value=source_payload), \
             patch("novel_pipeline.pipeline.PromptStore"), \
             patch("novel_pipeline.pipeline.split_blocks", return_value=[block1, block2, block3]), \
             patch("novel_pipeline.pipeline._process_block") as mock_process, \
             patch("novel_pipeline.pipeline._read_block_artifact", side_effect=fake_read_artifact), \
             patch("novel_pipeline.pipeline._write_chapter_output") as mock_write:
            stopped = _resume_chapter(
                config=config,
                ledger=mock_ledger,
                run_id=run_id,
                chapter_id=chapter_id,
                glossary_index={},
                state=state,
                until_block=until_block,
            )

    assert stopped is True
    mock_process.assert_not_called()
    mock_write.assert_called_once()


def test_resume_chapter_force_stops_after_until_block_and_uses_stop_mode():
    """Forced bounded resume still stops after until_block and forwards manual_action_mode."""
    from novel_pipeline.pipeline import _resume_chapter
    from novel_pipeline.ledger import ResumeState
    from novel_pipeline.types import TextBlock
    from unittest.mock import Mock, patch
    import json
    import tempfile
    from pathlib import Path

    run_id = "batch-ch019-ch023-v1"
    chapter_id = "ch019"
    until_block = "ch019-block-002"
    block1 = TextBlock(block_id="ch019-block-001", chapter_id=chapter_id, source_text="a", source_language="zh")
    block2 = TextBlock(block_id=until_block, chapter_id=chapter_id, source_text="b", source_language="zh")
    block3 = TextBlock(block_id="ch019-block-003", chapter_id=chapter_id, source_text="c", source_language="zh")
    state = ResumeState(run_id=run_id)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock()
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"
        config.workspace.raw = base / "03_Raw"
        config.workspace.prompts = base / "prompts"
        config.workspace.templates_dir = base / "00_Templates"
        config.workspace.glossary_dir = base / "01_Glossary"
        config.workspace.output = base / "05_Output"
        config.default_style_profile = "default"
        config.source_language = "zh"
        config.chunking.chinese_character_limit = 600
        config.chunking.non_chinese_word_limit = 300
        config.novel_id = "test"

        source_payload = json.dumps({
            "novel_id": "test",
            "chapter_id": chapter_id,
            "title": "Chapter",
            "source_language": "zh",
            "raw_text": "dummy",
        })

        mock_ledger = Mock()
        mock_ledger.has_committed.side_effect = (
            lambda **kwargs: kwargs.get("stage") in {"glossary_scanned", "glossary_approved"}
        )

        with patch("novel_pipeline.pipeline.read_text_if_exists", return_value=source_payload), \
             patch("novel_pipeline.pipeline.PromptStore"), \
             patch("novel_pipeline.pipeline.split_blocks", return_value=[block1, block2, block3]), \
             patch("novel_pipeline.pipeline._process_block", return_value="formatted") as mock_process, \
             patch("novel_pipeline.pipeline._write_chapter_output"):
            stopped = _resume_chapter(
                config=config,
                ledger=mock_ledger,
                run_id=run_id,
                chapter_id=chapter_id,
                glossary_index={},
                state=state,
                force=True,
                manual_action_mode="stop",
                until_block=until_block,
            )

    assert stopped is True
    assert [call.args[1].block_id for call in mock_process.call_args_list] == [block1.block_id, block2.block_id]
    assert all(call.kwargs["manual_action_mode"] == "stop" for call in mock_process.call_args_list)


def test_inspect_block_command_reports_artifacts_and_validation():
    """inspect-block reports artifact state, ledger records, and validation issues."""
    from novel_pipeline.pipeline import inspect_block_command, _write_block_artifact
    from novel_pipeline.ledger import ResumeState
    from novel_pipeline.types import AppConfig, RunRecord
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    run_id = "batch-ch019-ch023-v1"
    block_id = "ch019-block-003"
    chapter_id = "ch019"

    translating = RunRecord.new(run_id=run_id, block_id=block_id, stage="translating", status="completed", provider="gemini")
    refining = RunRecord.new(run_id=run_id, block_id=block_id, stage="refining", status="completed", provider="claude")
    qa_failed = RunRecord.new(run_id=run_id, block_id=block_id, stage="qa", status="failed", provider="gemini")
    state = ResumeState(
        run_id=run_id,
        records=(translating, refining, qa_failed),
        latest_by_block={block_id: qa_failed},
        latest_by_stage={
            (block_id, "translating"): translating,
            (block_id, "refining"): refining,
            (block_id, "qa"): qa_failed,
        },
        records_by_block={block_id: [translating, refining, qa_failed]},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        work_dir = base / "04_Work"
        raw_dir = base / "03_Raw"
        output_dir = base / "05_Output"
        work_dir.mkdir()
        raw_dir.mkdir()
        output_dir.mkdir()

        config = Mock(spec=AppConfig)
        config.workspace.work = work_dir
        config.workspace.raw = raw_dir
        config.workspace.output = output_dir
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"

        (raw_dir / chapter_id).mkdir(parents=True, exist_ok=True)
        (raw_dir / chapter_id / "source.json").write_text('{"chapter_id":"ch019","title":"Title","raw_text":"source"}', encoding="utf-8")
        _write_block_artifact(config, chapter_id, block_id, "literal", {"text": "literal"})
        _write_block_artifact(config, chapter_id, block_id, "refined", {"refined_text": "refined"})
        _write_block_artifact(config, chapter_id, block_id, "qa", {"passed": False})
        _write_block_artifact(config, chapter_id, block_id, "formatted", {"text": "Gemini stdout\n你好\n\""})

        mock_ledger = Mock()
        mock_ledger.load_state.return_value = state

        with patch("novel_pipeline.pipeline.RunLedger", return_value=mock_ledger):
            result = inspect_block_command(config=config, run_id=run_id, block_id=block_id)

    assert result["chapter_id"] == chapter_id
    assert result["artifact_exists"] == {"source": True, "literal": True, "refined": True, "qa": True, "formatted": True}
    assert len(result["records"]) == 3
    assert result["next_pending_stage"] == "qa"
    assert "provider/meta marker: gemini" in result["formatted_validation_issues"]
    assert "provider/meta marker: stdout" in result["formatted_validation_issues"]
    assert "Han Chinese characters present" in result["formatted_validation_issues"]
    assert "quote-only line 3" in result["formatted_validation_issues"]


def test_checkpoint_report_generation_writes_expected_markdown():
    """Checkpoint report generation writes markdown from status_run data."""
    from novel_pipeline.reports import build_checkpoint_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    status = {
        "total_records": 4,
        "completed_blocks": ("ch019-block-001", "ch019-block-002"),
        "current_failed_blocks": ("ch019-block-003",),
        "historical_failed_records": 2,
        "next_effective_action": "resume --run-id batch-ch019-ch023-v1",
        "manual_actions": ["inspect failed blocks and rerun from the appropriate stage."],
        "chapter_ids": ["ch019"],
        "chapter_summary": {
            "ch019": {
                "expected_blocks": 3,
                "completed_blocks": 2,
                "failed_blocks": ["ch019-block-003"],
                "pending_blocks": ["ch019-block-004"],
                "output_exists": False,
            }
        },
        "block_stage_status": {
            "ch019-block-001": {"next_pending_stage": None, "records": [{}, {}]},
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        output_dir = base / "05_Output"
        output_dir.mkdir()

        config = Mock(spec=AppConfig)
        config.workspace.output = output_dir
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"

        with patch("novel_pipeline.reports.status_run", return_value=status):
            result = build_checkpoint_report(config=config, run_id="batch-ch019-ch023-v1")
        assert result["path"] == base / "07_Reports" / "checkpoint_batch-ch019-ch023-v1.md"
        assert result["path"].exists()
        text = result["path"].read_text(encoding="utf-8")
        assert "# Checkpoint Report - batch-ch019-ch023-v1" in text
        assert "total_records: 4" in text
        assert "ch019-block-003" in text
        assert "resume --run-id batch-ch019-ch023-v1" in text


def test_cleanliness_report_flags_body_issues_and_ignores_title_han():
    """Cleanliness report flags body problems but ignores Chinese in line 1."""
    from novel_pipeline.reports import build_cleanliness_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    run_id = "batch-ch019-ch023-v1"
    chapter_id = "ch019"

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        work_dir = base / "04_Work"
        output_dir = base / "05_Output"
        work_dir.mkdir()
        output_dir.mkdir()
        chapter_dir = output_dir / chapter_id
        chapter_dir.mkdir()
        (chapter_dir / f"{chapter_id}.md").write_text(
            "# 失乡号\n"
            "Gemini stdout\n"
            "你好，船长。\n"
            "ดันแคน เอบนอร์มัล\n"
            "\"\n",
            encoding="utf-8",
        )

        config = Mock(spec=AppConfig)
        config.workspace.work = work_dir
        config.workspace.output = output_dir
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"

        summary = {
            "chapter_ids": [chapter_id],
            "block_stage_status": {},
        }

        with patch("novel_pipeline.reports.status_run", return_value=summary), \
             patch("novel_pipeline.reports.inspect_block_command", return_value={"formatted_validation_issues": []}):
            result = build_cleanliness_report(config=config, run_id=run_id)
        chapter = result["chapter_results"][0]
        assert chapter["exists"] is True
        assert any(issue == "provider/meta marker: gemini" for issue in chapter["issues"])
        assert any(issue == "provider/meta marker: stdout" for issue in chapter["issues"])
        assert any(issue == "wrong glossary variant: ดันแคน เอบนอร์มัล" for issue in chapter["issues"])
        assert any(issue == "quote-only line 5" for issue in chapter["issues"])
        assert any(issue.startswith("Han Chinese body line") for issue in chapter["issues"])
        assert not any("line 1" in issue for issue in chapter["issues"])


def test_cmd_report_cleanliness_returns_nonzero_on_missing_output():
    """Report wrapper returns nonzero when a target chapter output is missing."""
    from novel_pipeline.cli import cmd_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        output_dir = base / "05_Output"
        output_dir.mkdir()

        config = Mock(spec=AppConfig)
        config.workspace.output = output_dir
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"

        args = Mock(
            report_command="cleanliness",
            run_id="batch-ch019-ch023-v1",
            chapter_id=[],
            output=None,
        )

        with patch("novel_pipeline.reports.status_run", return_value={"chapter_ids": ["ch019"], "block_stage_status": {}}):
            result = cmd_report(args, config)

    assert result == 1


def test_product_review_report_generation_writes_expected_markdown():
    """Product review report summarizes acceptance state from deterministic evidence."""
    from novel_pipeline.reports import build_product_review_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    run_id = "batch-ch019-ch023-v1"
    summary = {
        "total_records": 163,
        "completed_blocks": ["ch019-block-001", "ch019-block-002"],
        "current_failed_blocks": [],
        "historical_failed_records": 9,
        "next_effective_action": "none",
        "manual_actions": ["none"],
        "chapter_ids": ["ch019"],
    }
    preflight = {
        "status": "ready",
        "warnings": [],
        "blocking_reasons": [],
        "next_safe_action": "Preflight is ready for normal production.",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / "07_Reports").mkdir(parents=True, exist_ok=True)
        chapter_dir = base / "05_Output" / "ch019"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        (chapter_dir / "ch019.md").write_text(
            "# 第十九章\nดันแคนยืนอยู่บนดาดฟ้าเรือ\n",
            encoding="utf-8",
        )
        for name in ("PROJECT_BRAIN.md", "IMPLEMENT_PLAN.md", "OPERATOR_MANUAL.md", "NOVEL_SETUP_PLAYBOOK.md", "FETCH_ADAPTER_PLAYBOOK.md", "RESEARCH_PROFILE_PLAYBOOK.md", "RESEARCH_PROFILE.yaml"):
            (base / name).write_text("ok\n", encoding="utf-8")
        (base / "00_Templates").mkdir(parents=True, exist_ok=True)
        for name in ("Novel-Profile.yaml", "Research-Profile.yaml", "Batch-Rollout-Checklist.md", "Worker-Bounded-Batch-Prompt.md"):
            (base / "00_Templates" / name).write_text("ok\n", encoding="utf-8")
        (base / "novel_pipeline").mkdir(parents=True, exist_ok=True)
        for name in ("operator_ui.py", "preflight.py", "project_setup.py"):
            (base / "novel_pipeline" / name).write_text("ok\n", encoding="utf-8")

        config = Mock(spec=AppConfig)
        config.workspace.root = base
        config.workspace.output = base / "05_Output"
        config.ledger_path = base / "06_Logs" / "run_ledger.jsonl"

        ledger_records = [Mock(block_id="ch019", metadata={})]
        with patch("novel_pipeline.reports.status_run", return_value=summary), \
             patch("novel_pipeline.reports.build_preflight_summary", return_value=preflight), \
             patch("novel_pipeline.reports.RunLedger") as ledger_cls:
            ledger_cls.return_value.iter_records.return_value = ledger_records
            result = build_product_review_report(config=config, run_id=run_id)

        assert result["overall_status"] == "accepted"
        assert result["actionable_failure"] is False
        text = result["path"].read_text(encoding="utf-8")
        assert "# Product Review Report - batch-ch019-ch023-v1" in text
        assert "- overall_status: accepted" in text
        assert "| preflight | ok | ready |" in text
        assert "| glossary_approval_evidence | ok | glossary_approved records: 1 |" in text


def test_provider_usage_report_generation_writes_expected_markdown():
    """Provider usage report generation writes provider/stage/status counts."""
    from novel_pipeline.reports import build_provider_usage_report
    from novel_pipeline.types import AppConfig
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    summary = {
        "current_failed_blocks": (),
        "historical_failed_records": 2,
        "provider_usage": {
            "claude": {"refining": {"completed": 3, "failed": 1}},
            "qwen": {"qa": {"completed": 3}},
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock(spec=AppConfig)
        config.workspace.output = base / "05_Output"
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"

        with patch("novel_pipeline.reports.status_run", return_value=summary):
            result = build_provider_usage_report(config=config, run_id="batch-ch019-ch023-v1")

        assert result["path"] == base / "07_Reports" / "provider_usage_batch-ch019-ch023-v1.md"
        text = result["path"].read_text(encoding="utf-8")
        assert "# Provider Usage Report - batch-ch019-ch023-v1" in text
        assert "| claude | refining | completed | 3 |" in text
        assert "| claude | refining | failed | 1 |" in text
        assert "| qwen | qa | completed | 3 |" in text


def test_glossary_decisions_report_generation_writes_expected_markdown():
    """Glossary decisions report is built from glossary_approved ledger metadata and glossary notes."""
    from novel_pipeline.reports import build_glossary_decisions_report
    from novel_pipeline.types import AppConfig, GlossaryEntry
    from novel_pipeline.ledger import RunRecord
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    records = [
        RunRecord(
            run_id="batch-ch019-ch023-v1",
            block_id="ch019",
            stage="glossary_approved",
            status="completed",
            created_at="2026-04-18T21:36:06.528222Z",
            provider="local",
            input_hash="",
            output_hash="",
            metadata={
                "approval_mode": "user_v3_9_glossary_gate",
                "approved_terms": ["实太阳神", "面具神"],
                "rejected_terms": ["阳神", "黑曜石"],
            },
        )
    ]

    glossary_index = {
        "实太阳神": GlossaryEntry(
            original_term="实太阳神",
            thai_term="สุริยเทพที่แท้จริง",
            category="title",
            status="approved",
            aliases=(),
            description="",
            related=(),
            source_language="zh",
            notes="",
            metadata={"path": "01_Glossary/实太阳神.md"},
        ),
        "面具神": GlossaryEntry(
            original_term="面具神",
            thai_term="เทพหน้ากาก",
            category="entity",
            status="approved",
            aliases=(),
            description="",
            related=(),
            source_language="zh",
            notes="",
            metadata={"path": "01_Glossary/面具神.md"},
        ),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        config = Mock(spec=AppConfig)
        config.workspace.output = base / "05_Output"
        config.workspace.glossary_dir = base / "01_Glossary"
        config.ledger_path = base / "06_Logs" / "ledger.jsonl"

        mock_ledger = Mock()
        mock_ledger.iter_records.return_value = records

        with patch("novel_pipeline.reports.RunLedger", return_value=mock_ledger), \
             patch("novel_pipeline.reports.load_glossary_index", return_value=glossary_index):
            result = build_glossary_decisions_report(config=config, run_id="batch-ch019-ch023-v1")

        text = result["path"].read_text(encoding="utf-8")
        assert "# Glossary Decisions Report - batch-ch019-ch023-v1" in text
        assert "user_v3_9_glossary_gate" in text
        assert "实太阳神" in text
        assert "สุริยเทพที่แท้จริง" in text
        assert "面具神" in text
        assert "เทพหน้ากาก" in text
        assert "- 阳神" in text
        assert "- 黑曜石" in text


def test_glossary_conflicts_report_generation_writes_expected_markdown():
    """Glossary conflicts report summarizes note collisions and batch scan artifacts."""
    from novel_pipeline.reports import build_glossary_conflicts_report
    from unittest.mock import Mock
    import tempfile
    from pathlib import Path
    import json

    def write_note(path: Path, *, original: str, thai: str, status: str = "approved", aliases: list[str] | None = None) -> None:
        aliases = aliases or []
        alias_block = "aliases: []" if not aliases else "aliases:\n" + "\n".join(f"  - {alias}" for alias in aliases)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"""---
type: glossary-term
original_term: {original}
thai_term: {thai}
status: {status}
{alias_block}
source_language: zh
category: term
---

Body
""",
            encoding="utf-8",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"
        work_dir = base / "04_Work"

        write_note(glossary_dir / "失乡号.md", original="失乡号", thai="เรือ失乡号", aliases=["鲸船"])
        write_note(glossary_dir / "白橡木.md", original="白橡木", thai="ไม้โอ๊คขาว")
        write_note(glossary_dir / "白橡木号.md", original="白橡木号", thai="เรือไม้โอ๊คขาว")
        write_note(glossary_dir / "邓肯.md", original="邓肯", thai="ดันแคน")
        write_note(glossary_dir / "废弃.md", original="废弃", thai="ทิ้งแล้ว", status="rejected")
        write_note(glossary_dir / "quarantine" / "邓肯船.md", original="邓肯船", thai="เรือดันแคน", aliases=["鲸船"])

        batch_path = work_dir / "_batch" / "batch-ch001" / "glossary_scan.json"
        batch_path.parent.mkdir(parents=True, exist_ok=True)
        batch_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "scope": {"type": "batch", "id": "batch-ch001"},
                    "chapter_ids": ["ch001"],
                    "items": [
                        {"original_term": "邓肯船"},
                        {"original_term": "是失乡号"},
                        {"original_term": "废弃"},
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        config = Mock()
        config.workspace.root = base
        config.workspace.glossary_dir = glossary_dir
        config.workspace.work = work_dir

        result = build_glossary_conflicts_report(config=config, run_id="batch-ch001")

        text = result["path"].read_text(encoding="utf-8")
        assert "# Glossary Conflicts Report - batch-ch001" in text
        assert "approved_terms_count: 4" in text
        assert "quarantine_terms_count: 1" in text
        assert "白橡木号 contains 白橡木" in text
        assert "邓肯船 -> 邓肯 (prefix)" in text
        assert "是失乡号 -> 失乡号 (suffix)" in text
        assert "废弃 -> 废弃 (rejected |" in text
        assert "鲸船 -> 失乡号, 邓肯船" in text


def test_glossary_audit_report_generation_writes_expected_markdown():
    """Glossary audit report compares source glossary subsets against final output."""
    from novel_pipeline.reports import build_glossary_audit_report
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"
        raw_dir = base / "03_Raw"
        output_dir = base / "05_Output"

        glossary_dir.mkdir(parents=True, exist_ok=True)
        (glossary_dir / "失乡号.md").write_text(
            """---
type: glossary-term
original_term: 失乡号
thai_term: เรือ失乡号
status: approved
aliases: []
source_language: zh
category: term
---

Body
""",
            encoding="utf-8",
        )

        source_path = raw_dir / "ch001" / "source.json"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(
            """{
  "novel_id": "novel",
  "chapter_id": "ch001",
  "title": "Chapter 1",
  "source_language": "zh",
  "raw_text": "失乡号"
}
""",
            encoding="utf-8",
        )

        chapter_output = output_dir / "ch001" / "ch001.md"
        chapter_output.parent.mkdir(parents=True, exist_ok=True)
        chapter_output.write_text("BADVARIANT\n", encoding="utf-8")

        config = Mock()
        config.workspace.root = base
        config.workspace.glossary_dir = glossary_dir
        config.workspace.raw = raw_dir
        config.workspace.output = output_dir
        config.chunking.chinese_character_limit = 2500
        config.chunking.non_chinese_word_limit = 5000
        config.source_language = "zh"

        summary = {"chapter_ids": ["ch001"], "block_stage_status": {}}

        with patch("novel_pipeline.reports.status_run", return_value=summary), \
             patch("novel_pipeline.reports._WRONG_GLOSSARY_VARIANTS", ("BADVARIANT",)):
            result = build_glossary_audit_report(config=config, run_id="batch-ch001")

        text = result["path"].read_text(encoding="utf-8")
        assert "# Glossary Audit Report - batch-ch001" in text
        assert "expected approved glossary terms: 失乡号" in text
        assert "missing thai terms in final output: เรือ失乡号" in text
        assert "glossary subset source terms with missing thai output: 失乡号" in text
        assert "suspicious wrong variants: BADVARIANT" in text


def test_glossary_guard_report_generation_writes_expected_markdown():
    """Glossary guard report compares raw deterministic candidates against filtered queue results."""
    from novel_pipeline.reports import build_glossary_guard_report
    from novel_pipeline.types import TextBlock
    from unittest.mock import Mock, patch
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        glossary_dir = base / "01_Glossary"
        glossary_dir.mkdir(parents=True, exist_ok=True)

        (glossary_dir / "???.md").write_text(
            """---
type: glossary-term
original_term: ???
thai_term: ??????????????
status: approved
aliases: []
source_language: zh
category: vessel
---

Body
""",
            encoding="utf-8",
        )
        (glossary_dir / "quarantine" / "???.md").write_text(
            """---
type: glossary-term
original_term: ???
thai_term: none
status: proposed
aliases: []
source_language: zh
category: term
---

Body
""",
            encoding="utf-8",
        )

        config = Mock()
        config.workspace.root = base
        config.workspace.glossary_dir = glossary_dir
        config.ledger_path = base / "06_Logs" / "run_ledger.jsonl"
        config.source_language = "zh"
        config.novel_id = "novel"

        summary = {"chapter_ids": ["ch001"], "block_stage_status": {}}
        blocks = [
            TextBlock(
                block_id="ch001-block-001",
                chapter_id="ch001",
                source_text="??????????????????",
                source_language="zh",
            )
        ]

        filtered_queue = [{"original_term": "???", "chapter_id": "ch001"}]

        with patch("novel_pipeline.reports.status_run", return_value=summary),              patch("novel_pipeline.reports._load_chapter_source_and_blocks", return_value=(None, blocks)),              patch("novel_pipeline.reports.extract_candidate_terms", return_value=["???", "???", "????"]),              patch("novel_pipeline.reports.build_glossary_scan_queue", return_value=filtered_queue),              patch("novel_pipeline.reports._historical_rejected_terms", return_value=set()),              patch("novel_pipeline.reports._is_obvious_noise_candidate", side_effect=lambda term, approved, quarantine: term == "????"):
            result = build_glossary_guard_report(config=config, run_id="batch-ch001")

        text = result["path"].read_text(encoding="utf-8")
        assert "# Glossary Guard Verification Report - batch-ch001" in text
        assert "- raw_deterministic_candidates: 3" in text
        assert "- filtered_candidates: 1" in text
        assert "- removed_by_blocked_exact: ???" in text
        assert "- removed_by_noisy_wrapper: ????" in text
        assert "- kept_candidates: ???" in text
        assert result["actionable_failure"] is False


def test_generate_operator_report_dispatches_supported_kinds():
    from novel_pipeline.operator_ui import generate_operator_report

    config = Mock()
    with patch("novel_pipeline.operator_ui.build_checkpoint_report", return_value={"path": Path("a.md")}) as checkpoint, \
         patch("novel_pipeline.operator_ui.build_cleanliness_report", return_value={"path": Path("b.md")}) as cleanliness, \
         patch("novel_pipeline.operator_ui.build_provider_usage_report", return_value={"path": Path("c.md")}) as provider, \
         patch("novel_pipeline.operator_ui.build_preflight_report", return_value={"path": Path("p.md")}) as preflight, \
         patch("novel_pipeline.operator_ui.build_recovery_drill_report", return_value={"path": Path("r.md")}) as recovery, \
         patch("novel_pipeline.operator_ui.build_product_review_report", return_value={"path": Path("h.md")}) as product_review, \
         patch("novel_pipeline.operator_ui.build_glossary_decisions_report", return_value={"path": Path("d.md")}) as decisions, \
         patch("novel_pipeline.operator_ui.build_glossary_conflicts_report", return_value={"path": Path("e.md")}) as conflicts, \
         patch("novel_pipeline.operator_ui.build_glossary_audit_report", return_value={"path": Path("f.md")}) as audit, \
         patch("novel_pipeline.operator_ui.build_glossary_guard_report", return_value={"path": Path("g.md")}) as guard:
        assert generate_operator_report(config=config, run_id="run-1", kind="checkpoint")["path"] == Path("a.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="cleanliness")["path"] == Path("b.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="provider-usage")["path"] == Path("c.md")
        assert generate_operator_report(config=config, run_id=None, kind="preflight")["path"] == Path("p.md")
        assert generate_operator_report(config=config, run_id=None, kind="recovery-drill")["path"] == Path("r.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="product-review")["path"] == Path("h.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="glossary-decisions")["path"] == Path("d.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="glossary-conflicts")["path"] == Path("e.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="glossary-audit")["path"] == Path("f.md")
        assert generate_operator_report(config=config, run_id="run-1", kind="glossary-guard")["path"] == Path("g.md")

    checkpoint.assert_called_once()
    cleanliness.assert_called_once()
    provider.assert_called_once()
    preflight.assert_called_once()
    recovery.assert_called_once()
    product_review.assert_called_once()
    decisions.assert_called_once()
    conflicts.assert_called_once()
    audit.assert_called_once()
    guard.assert_called_once()


def test_safe_workspace_path_rejects_outside_workspace():
    from novel_pipeline.operator_ui import _safe_workspace_path
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        allowed = root / "07_Reports" / "a.md"
        allowed.parent.mkdir(parents=True, exist_ok=True)
        allowed.write_text("ok", encoding="utf-8")
        outside_dir = root.parent / "outside-codex-test"
        outside_dir.mkdir(parents=True, exist_ok=True)
        outside = outside_dir / "bad.md"
        outside.write_text("bad", encoding="utf-8")

        config = Mock()
        config.workspace.root = root

        assert _safe_workspace_path(config, str(allowed)) == allowed.resolve()
        try:
            _safe_workspace_path(config, str(outside))
            assert False, "Expected ValueError for outside path"
        except ValueError as exc:
            assert "outside the workspace root" in str(exc).lower()


def test_build_glossary_queue_snapshot_revalidates_items():
    from novel_pipeline.operator_ui import build_glossary_queue_snapshot
    from novel_pipeline.types import TextBlock

    config = Mock()
    queue_items = [
        {"original_term": "实太阳神", "chapter_id": "ch020", "first_seen_block": "ch020-block-004", "category": "title"},
        {"original_term": "高台", "chapter_id": "ch020", "first_seen_block": "ch020-block-001", "category": "object"},
    ]
    filtered_items = [queue_items[0]]
    blocks = [TextBlock(chapter_id="ch020", block_id="ch020-block-001", block_index=1, source_text="...", text="...")]

    with patch("novel_pipeline.operator_ui._read_glossary_scan_artifact", return_value={"chapter_ids": ["ch020"]}), \
         patch("novel_pipeline.operator_ui._read_glossary_scan_items", return_value=queue_items), \
         patch("novel_pipeline.operator_ui._load_chapter_source_and_blocks", return_value=(None, blocks)), \
         patch("novel_pipeline.operator_ui._revalidate_glossary_queue_items", return_value=(filtered_items, ["高台"])):
        snapshot = build_glossary_queue_snapshot(config, "batch-ch019-ch023-v1")

    assert snapshot["chapter_ids"] == ["ch020"]
    assert [item["original_term"] for item in snapshot["items"]] == [item["original_term"] for item in filtered_items]
    assert all("intersections" in item for item in snapshot["items"])
    assert snapshot["removed_terms"] == ["高台"]


def test_execute_operator_action_requires_bounded_resume():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    try:
        execute_operator_action(
            config=config,
            action="resume",
            run_id="batch-ch019-ch023-v1",
            payload={},
        )
        assert False, "Expected ValueError for unbounded resume"
    except ValueError as exc:
        assert "until_chapter or until_block" in str(exc)


def test_execute_operator_action_resume_uses_stop_mode_and_returns_snapshot():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    config.ensure_translation_ready.return_value = {"readiness": "degraded"}
    snapshot = {"run_id": "batch-ch019-ch023-v1", "status": {"next_effective_action": "none"}}
    with patch("novel_pipeline.operator_ui.resume_pipeline") as resume_pipeline_mock, \
         patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value=snapshot):
        result = execute_operator_action(
            config=config,
            action="resume",
            run_id="batch-ch019-ch023-v1",
            payload={"until_chapter": "ch022"},
        )

    resume_pipeline_mock.assert_called_once_with(
        config=config,
        run_id="batch-ch019-ch023-v1",
        force=False,
        manual_action_mode="stop",
        until_chapter="ch022",
        until_block=None,
    )
    config.ensure_translation_ready.assert_called_once_with(bounded=True)
    assert result["snapshot"] == snapshot


def test_execute_operator_action_rerun_block_dispatches_expected_args():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    config.ensure_translation_ready.return_value = {"readiness": "degraded"}
    snapshot = {"run_id": "batch-ch019-ch023-v1", "status": {}}
    with patch("novel_pipeline.operator_ui.rerun_block_pipeline") as rerun_mock, \
         patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value=snapshot):
        result = execute_operator_action(
            config=config,
            action="rerun-block",
            run_id="batch-ch019-ch023-v1",
            payload={"block_id": "ch019-block-002", "from_stage": "qa"},
        )

    rerun_mock.assert_called_once_with(
        config=config,
        run_id="batch-ch019-ch023-v1",
        block_id="ch019-block-002",
        from_stage="qa",
    )
    config.ensure_translation_ready.assert_called_once_with(bounded=True)
    assert result["snapshot"] == snapshot


def test_execute_operator_action_run_batch_scan_only_dispatches_expected_args():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    snapshot = {"run_id": "batch-ch004-ch008-v1", "status": {}}
    with patch("novel_pipeline.operator_ui.parse_chapter_range", return_value=["ch004", "ch005", "ch006"]), \
         patch("novel_pipeline.operator_ui.run_batch_pipeline") as run_batch_mock, \
         patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value=snapshot):
        result = execute_operator_action(
            config=config,
            action="run-batch",
            run_id="batch-ch004-ch008-v1",
            payload={"chapter_range": "ch004-ch006", "stop_after": "glossary-scan"},
        )

    run_batch_mock.assert_called_once_with(
        config=config,
        chapter_ids=["ch004", "ch005", "ch006"],
        run_id="batch-ch004-ch008-v1",
        force=False,
        stop_after="glossary-scan",
        manual_action_mode="stop",
    )
    config.ensure_translation_ready.assert_not_called()
    assert result["snapshot"] == snapshot


def test_execute_operator_action_run_batch_bounded_dispatches_expected_args():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    config.ensure_translation_ready.return_value = {"readiness": "degraded"}
    snapshot = {"run_id": "batch-ch004-ch008-v1", "status": {}}
    with patch("novel_pipeline.operator_ui.parse_chapter_range", return_value=["ch004", "ch005", "ch006"]), \
         patch("novel_pipeline.operator_ui.run_batch_pipeline") as run_batch_mock, \
         patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value=snapshot):
        result = execute_operator_action(
            config=config,
            action="run-batch",
            run_id="batch-ch004-ch008-v1",
            payload={"chapter_range": "ch004-ch006", "stop_after": ""},
        )

    config.ensure_translation_ready.assert_called_once_with(bounded=True)
    run_batch_mock.assert_called_once_with(
        config=config,
        chapter_ids=["ch004", "ch005", "ch006"],
        run_id="batch-ch004-ch008-v1",
        force=False,
        stop_after=None,
        manual_action_mode="stop",
    )
    assert result["snapshot"] == snapshot


def test_execute_operator_action_run_batch_rejects_invalid_stop_after():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    try:
        execute_operator_action(
            config=config,
            action="run-batch",
            run_id="batch-ch004-ch008-v1",
            payload={"chapter_range": "ch004-ch006", "stop_after": "review"},
        )
        assert False, "Expected ValueError for invalid stop_after"
    except ValueError as exc:
        assert "stop_after" in str(exc)


def test_execute_operator_action_run_batch_rejects_missing_run_id_or_chapter_range():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    cases = [
        {"run_id": "", "payload": {"chapter_range": "ch004-ch006", "stop_after": ""}},
        {"run_id": "batch-ch004-ch008-v1", "payload": {"chapter_range": "", "stop_after": ""}},
    ]
    for case in cases:
        try:
            execute_operator_action(
                config=config,
                action="run-batch",
                run_id=case["run_id"],
                payload=case["payload"],
            )
            assert False, "Expected ValueError for missing batch inputs"
        except ValueError as exc:
            assert "run-batch requires run_id and chapter_range" in str(exc)


def test_execute_operator_action_init_novel_dispatches_expected_args():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    snapshot = {"run_id": None, "status": {}}
    with patch("novel_pipeline.operator_ui.initialize_novel_project", return_value={
        "project_root": Path(r"D:\Temp\Novel"),
        "config_path": Path(r"D:\Temp\Novel\.system\config.yaml"),
        "profile_path": Path(r"D:\Temp\Novel\NOVEL_PROFILE.yaml"),
        "research_profile_path": Path(r"D:\Temp\Novel\RESEARCH_PROFILE.yaml"),
    }) as init_mock, patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value=snapshot):
        result = execute_operator_action(
            config=config,
            action="init-novel",
            run_id="",
            payload={
                "project_root": r"D:\Temp\Novel",
                "title": "Deep Sea Embers",
                "source_url": "https://example.com/toc",
                "novel_id": "deep-sea-embers",
                "aliases": "深海余烬,  Deep Sea Embers\n  Ember Tide  ,",
                "source_language": "zh",
                "target_language": "th",
                "genre": "dark fantasy",
                "adapter": "piaotia",
                "style_profile": "deep_sea_embers",
            },
        )

    init_mock.assert_called_once_with(
        template_config=config,
        project_root=Path(r"D:\Temp\Novel"),
        title="Deep Sea Embers",
        source_url="https://example.com/toc",
        novel_id="deep-sea-embers",
        aliases=["深海余烬", "Deep Sea Embers", "Ember Tide"],
        source_language="zh",
        target_language="th",
        genre="dark fantasy",
        adapter="piaotia",
        style_profile="deep_sea_embers",
    )
    assert result["paths"] == {
        "project_root": r"D:\Temp\Novel",
        "config_path": r"D:\Temp\Novel\.system\config.yaml",
        "profile_path": r"D:\Temp\Novel\NOVEL_PROFILE.yaml",
        "research_profile_path": r"D:\Temp\Novel\RESEARCH_PROFILE.yaml",
    }
    assert result["snapshot"]["init_novel_paths"] == result["paths"]


def test_execute_operator_action_init_novel_rejects_missing_required_fields():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    cases = [
        {"project_root": "", "title": "Deep Sea Embers", "source_url": "https://example.com/toc"},
        {"project_root": r"D:\Temp\Novel", "title": "", "source_url": "https://example.com/toc"},
        {"project_root": r"D:\Temp\Novel", "title": "Deep Sea Embers", "source_url": ""},
    ]
    for payload in cases:
        try:
            execute_operator_action(
                config=config,
                action="init-novel",
                run_id="",
                payload=payload,
            )
            assert False, "Expected ValueError for missing init-novel fields"
        except ValueError as exc:
            assert "init-novel requires project_root, title, and source_url" in str(exc)


def test_execute_operator_action_init_novel_parses_aliases_from_ui_payload():
    from novel_pipeline.operator_ui import execute_operator_action

    config = Mock()
    snapshot = {"run_id": None, "status": {}}
    with patch("novel_pipeline.operator_ui.initialize_novel_project", return_value={
        "project_root": Path(r"D:\Temp\Novel"),
        "config_path": Path(r"D:\Temp\Novel\.system\config.yaml"),
        "profile_path": Path(r"D:\Temp\Novel\NOVEL_PROFILE.yaml"),
        "research_profile_path": Path(r"D:\Temp\Novel\RESEARCH_PROFILE.yaml"),
    }) as init_mock, patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value=snapshot):
        execute_operator_action(
            config=config,
            action="init-novel",
            run_id="",
            payload={
                "project_root": r"D:\Temp\Novel",
                "title": "Deep Sea Embers",
                "source_url": "https://example.com/toc",
                "aliases": "  深海余烬,  Deep Sea Embers\n\n Ember Tide , ,",
            },
        )

    init_mock.assert_called_once()
    assert init_mock.call_args.kwargs["aliases"] == ["深海余烬", "Deep Sea Embers", "Ember Tide"]


def test_execute_operator_action_save_research_profile_updates_yaml():
    from novel_pipeline.operator_ui import execute_operator_action
    from novel_pipeline.config import load_app_config

    import tempfile
    import yaml

    base = Path(tempfile.mkdtemp(prefix="novel-save-research-profile-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Old Title
source_url: https://example.com/toc
status: drafted
synopsis: Old synopsis
tags:
  - old tag
style_notes: Preserve the original voice.
reader_expectations: Existing readers
review_summary: Existing review
last_reviewed_at: 2026-05-01T00:00:00+00:00
reviewed_by: Old reviewer
terminology:
  - ember
reference_links:
  - https://example.com/ref
notes: Keep notes
""",
    )
    config = load_app_config(config_path)

    result = execute_operator_action(
        config=config,
        action="save-research-profile",
        run_id="",
        payload={
            "title": "Updated Title",
            "aliases": "Alias One, Alias Two",
            "source_url": "https://example.com/toc",
            "status": "active",
            "synopsis": "Updated synopsis",
            "tags": "new tag\nsecond tag",
            "style_notes": "New style notes",
            "reader_expectations": "Updated expectations",
            "review_summary": "Updated review summary",
            "last_reviewed_at": "2026-05-09T00:00:00+07:00",
            "reviewed_by": "Editor",
            "terminology": "ember, abyss",
            "reference_links": "https://example.com/ref\nhttps://example.com/review",
            "notes": "Updated notes",
        },
    )

    saved_profile_path = config.workspace.root / "RESEARCH_PROFILE.yaml"
    saved_payload = yaml.safe_load(saved_profile_path.read_text(encoding="utf-8"))
    assert saved_payload == {
        "schema_version": 1,
        "title": "Updated Title",
        "aliases": ["Alias One", "Alias Two"],
        "source_url": "https://example.com/toc",
        "status": "active",
        "synopsis": "Updated synopsis",
        "tags": ["new tag", "second tag"],
        "style_notes": "New style notes",
        "reader_expectations": "Updated expectations",
        "review_summary": "Updated review summary",
        "last_reviewed_at": "2026-05-09T00:00:00+07:00",
        "reviewed_by": "Editor",
        "terminology": ["ember", "abyss"],
        "reference_links": ["https://example.com/ref", "https://example.com/review"],
        "notes": "Updated notes",
    }
    assert config.research_profile is not None
    assert config.research_profile.title == "Updated Title"
    assert config.research_profile.aliases == ("Alias One", "Alias Two")
    assert config.research_profile.status == "active"
    assert config.research_profile.reader_expectations == "Updated expectations"
    assert config.research_profile.review_summary == "Updated review summary"
    assert config.research_profile.terminology == ("ember", "abyss")
    assert config.research_profile.reference_links == ("https://example.com/ref", "https://example.com/review")
    assert config.research_profile.notes == "Updated notes"
    assert result["snapshot"]["research_profile"]["title"] == "Updated Title"
    assert result["snapshot"]["research_profile"]["aliases"] == ["Alias One", "Alias Two"]
    assert result["snapshot"]["research_profile"]["reader_expectations"] == "Updated expectations"
    assert result["snapshot"]["research_profile"]["review_summary"] == "Updated review summary"
    assert result["snapshot"]["research_profile"]["terminology"] == ["ember", "abyss"]
    assert result["snapshot"]["research_profile"]["reference_links"] == ["https://example.com/ref", "https://example.com/review"]
    assert result["snapshot"]["research_profile"]["notes"] == "Updated notes"
    assert result["snapshot"]["research_readiness"]["status"] == "active"
    assert result["snapshot"]["research_readiness"]["translation_ready"] is True
    assert "Saved research profile to" in result["output"]


def test_operator_snapshot_includes_research_readiness():
    """Operator bootstrap snapshot includes research profile path and readiness summary."""
    import tempfile
    from novel_pipeline.config import load_app_config
    from novel_pipeline.operator_ui import build_operator_snapshot

    base = Path(tempfile.mkdtemp(prefix="novel-operator-snapshot-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
aliases:
  - Deep Sea
  - DSE
source_url: https://example.com/toc
status: drafted
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
  - mystery
style_notes: Blend eerie maritime atmosphere with grounded reactions.
reader_expectations: Expect slow-burn reveals and practical protagonist logic.
review_summary: Reviews emphasize atmosphere, mystery, and immersive worldbuilding.
terminology:
  - ember
  - abyss
reference_links:
  - https://example.com/review
""",
    )
    config = load_app_config(config_path)
    snapshot = build_operator_snapshot(config, run_id="batch-ch019-ch023-v1")

    assert snapshot["research_profile_path"].endswith("RESEARCH_PROFILE.yaml")
    assert snapshot["research_readiness"]["status"] == "drafted"
    assert snapshot["research_readiness"]["bounded_translation_ready"] is True
    assert snapshot["research_readiness"]["translation_ready"] is False
    assert snapshot["research_readiness"]["path"].endswith("RESEARCH_PROFILE.yaml")


def test_operator_snapshot_includes_research_profile_data():
    """Operator bootstrap snapshot exposes editable research profile data."""
    import tempfile
    from novel_pipeline.config import load_app_config
    from novel_pipeline.operator_ui import build_operator_snapshot

    base = Path(tempfile.mkdtemp(prefix="novel-operator-research-profile-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
aliases:
  - Deep Sea
  - DSE
source_url: https://example.com/toc
status: drafted
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
  - mystery
style_notes: Blend eerie maritime atmosphere with grounded reactions.
reader_expectations: Expect slow-burn reveals and practical protagonist logic.
review_summary: Reviews emphasize atmosphere, mystery, and immersive worldbuilding.
last_reviewed_at: 2026-05-01T00:00:00+07:00
reviewed_by: Editor
terminology:
  - ember
reference_links:
  - https://example.com/review
notes: Preserve ship names and source-linked canon.
""",
    )
    config = load_app_config(config_path)
    snapshot = build_operator_snapshot(config, run_id="batch-ch019-ch023-v1")

    assert snapshot["research_profile"]["title"] == "Deep Sea Embers"
    assert snapshot["research_profile"]["aliases"] == ["Deep Sea", "DSE"]
    assert snapshot["research_profile"]["source_url"] == "https://example.com/toc"
    assert snapshot["research_profile"]["status"] == "drafted"
    assert snapshot["research_profile"]["synopsis"].startswith("Nautical dark fantasy")
    assert snapshot["research_profile"]["tags"] == ["nautical dark fantasy", "mystery"]
    assert snapshot["research_profile"]["style_notes"].startswith("Blend eerie maritime atmosphere")
    assert snapshot["research_profile"]["reader_expectations"].startswith("Expect slow-burn reveals")
    assert snapshot["research_profile"]["review_summary"].startswith("Reviews emphasize atmosphere")
    assert snapshot["research_profile"]["last_reviewed_at"] == "2026-05-01T00:00:00+07:00"
    assert snapshot["research_profile"]["reviewed_by"] == "Editor"
    assert snapshot["research_profile"]["terminology"] == ["ember"]
    assert snapshot["research_profile"]["reference_links"] == ["https://example.com/review"]
    assert snapshot["research_profile"]["notes"] == "Preserve ship names and source-linked canon."


def test_operator_snapshot_includes_preflight():
    """Operator snapshot includes a preflight summary."""
    import tempfile
    from novel_pipeline.config import load_app_config
    from novel_pipeline.operator_ui import build_operator_snapshot

    base = Path(tempfile.mkdtemp(prefix="novel-operator-preflight-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/toc
status: drafted
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
style_notes: Blend eerie maritime atmosphere with grounded reactions.
""",
    )
    config = load_app_config(config_path)
    with patch("novel_pipeline.operator_ui.build_preflight_summary", return_value={"status": "degraded", "warnings": ["dirty"], "blocking_reasons": []}):
        snapshot = build_operator_snapshot(config, run_id="batch-ch019-ch023-v1")

    assert snapshot["preflight"]["status"] == "degraded"


def test_operator_snapshot_includes_command_hints_and_quick_links():
    """Operator snapshot exposes copyable command hints and existing canonical/report links."""
    import tempfile
    from novel_pipeline.config import load_app_config
    from novel_pipeline.operator_ui import build_operator_snapshot

    base = Path(tempfile.mkdtemp(prefix="novel-operator-links-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/toc
status: active
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
style_notes: Blend eerie maritime atmosphere with grounded reactions.
last_reviewed_at: 2026-05-10T00:00:00+07:00
reviewed_by: Operator
""",
    )
    workspace_root = base / "workspace"
    (workspace_root / "PROJECT_BRAIN.md").write_text("brain\n", encoding="utf-8")
    (workspace_root / "IMPLEMENT_PLAN.md").write_text("plan\n", encoding="utf-8")
    (workspace_root / "OPERATOR_MANUAL.md").write_text("manual\n", encoding="utf-8")
    reports_dir = workspace_root / "07_Reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "preflight_report.md").write_text("preflight\n", encoding="utf-8")
    (reports_dir / "recovery_drill.md").write_text("recovery\n", encoding="utf-8")
    (reports_dir / "product_review_batch-ch019-ch023-v1.md").write_text("product\n", encoding="utf-8")

    config = load_app_config(config_path)
    with patch("novel_pipeline.operator_ui.build_preflight_summary", return_value={"status": "ready", "next_safe_action": "Preflight is ready for normal production."}), \
         patch("novel_pipeline.operator_ui.status_run", return_value={"next_effective_action": "none", "manual_actions": [], "current_failed_blocks": []}):
        snapshot = build_operator_snapshot(config, run_id="batch-ch019-ch023-v1")

    assert "preflight" in snapshot["command_hints"]
    assert "report recovery-drill" in snapshot["command_hints"]["recovery_drill"]
    assert any(item["label"] == "Project Brain" for item in snapshot["quick_links"])
    assert any(item["label"] == "Recovery Drill" for item in snapshot["quick_links"])
    assert any(item["label"] == "Product Review" for item in snapshot["quick_links"])


def test_operator_snapshot_separates_active_and_archived_reports():
    """Operator snapshot separates active report surface from archived history."""
    import tempfile
    from novel_pipeline.config import load_app_config
    from novel_pipeline.operator_ui import build_operator_snapshot

    base = Path(tempfile.mkdtemp(prefix="novel-operator-report-surface-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/toc
status: active
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
style_notes: Blend eerie maritime atmosphere with grounded reactions.
last_reviewed_at: 2026-05-10T00:00:00+07:00
reviewed_by: Operator
""",
    )
    workspace_root = base / "workspace"
    reports_dir = workspace_root / "07_Reports"
    archive_history = reports_dir / "archive" / "history" / "v3_9"
    archive_bench = reports_dir / "archive" / "benchmarks"
    archive_history.mkdir(parents=True, exist_ok=True)
    archive_bench.mkdir(parents=True, exist_ok=True)
    (reports_dir / "v3_10_repeatable_rollout_protocol.md").write_text("protocol\n", encoding="utf-8")
    (reports_dir / "preflight_report.md").write_text("preflight\n", encoding="utf-8")
    (reports_dir / "product_review_batch-ch019-ch023-v1.md").write_text("product\n", encoding="utf-8")
    (archive_history / "spot_check_batch_ch019_ch023_v1.md").write_text("spot\n", encoding="utf-8")
    (archive_bench / "refinement_benchmark.md").write_text("bench\n", encoding="utf-8")

    config = load_app_config(config_path)
    with patch("novel_pipeline.operator_ui.build_preflight_summary", return_value={"status": "ready", "next_safe_action": "Preflight is ready for normal production."}), \
         patch("novel_pipeline.operator_ui.status_run", return_value={"next_effective_action": "none", "manual_actions": [], "current_failed_blocks": []}):
        snapshot = build_operator_snapshot(config, run_id="batch-ch019-ch023-v1")

    surfaces = snapshot["report_surfaces"]
    assert any(item["label"] == "Rollout Protocol" for item in surfaces["active"]["reference"])
    assert any(item["label"] == "Product Review" for item in surfaces["active"]["generated"])
    assert any(item["label"] == "history" for item in surfaces["archive"]["groups"])
    assert any(item["label"] == "benchmarks" for item in surfaces["archive"]["groups"])
    assert any(
        item["label"] == "archive/history/v3_9/spot_check_batch_ch019_ch023_v1.md"
        for item in surfaces["archive"]["recent"]
    )


def test_operator_snapshot_includes_dashboard_guardrails():
    """Operator snapshot exposes the accepted bounded-action model for the dashboard."""
    import tempfile
    from novel_pipeline.config import load_app_config
    from novel_pipeline.operator_ui import build_operator_snapshot

    base = Path(tempfile.mkdtemp(prefix="novel-operator-guardrails-"))
    config_path = _write_research_profile_test_workspace(
        base,
        """schema_version: 1
title: Deep Sea Embers
source_url: https://example.com/toc
status: active
synopsis: Nautical dark fantasy with a slow-burn mystery.
tags:
  - nautical dark fantasy
style_notes: Blend eerie maritime atmosphere with grounded reactions.
last_reviewed_at: 2026-05-10T00:00:00+07:00
reviewed_by: Operator
""",
    )
    config = load_app_config(config_path)
    with patch("novel_pipeline.operator_ui.build_preflight_summary", return_value={"status": "ready", "next_safe_action": "Preflight is ready for normal production."}), \
         patch("novel_pipeline.operator_ui.status_run", return_value={"next_effective_action": "none", "manual_actions": [], "current_failed_blocks": []}):
        snapshot = build_operator_snapshot(config, run_id="batch-ch019-ch023-v1")

    guardrails = snapshot["dashboard_guardrails"]
    assert "run-batch" in guardrails["allowed_state_actions"]
    assert "rerun-block" in guardrails["allowed_state_actions"]
    assert "product-review" in guardrails["visible_report_kinds"]
    assert guardrails["run_batch_requires_run_id"] is True
    assert guardrails["resume_manual_action_mode"] == "stop"
    assert guardrails["broad_unbounded_actions_exposed"] is False


def test_render_operator_html_contains_v6_dashboard_elements():
    from novel_pipeline.operator_ui import _render_operator_html

    html = _render_operator_html()
    assert "Task Workspace" in html
    assert "Task Guide" in html
    assert 'id="taskGuide"' in html
    assert 'id="jumpBatchControlsBtn"' not in html
    assert "Paste a run ID or pick one from the known-run list" in html
    assert 'data-focus-target="operate"' in html
    assert 'data-focus-target="glossary"' in html
    assert 'data-task-role="navigation"' in html
    assert 'data-action-role="read-only"' in html
    assert 'data-action-role="state-changing"' in html
    assert 'data-action-role="setup-action"' in html
    assert 'id="runSelector"' in html
    assert 'id="statusStrip"' in html
    assert 'id="runOverview"' in html
    assert 'id="batchControlsPanel"' in html
    assert 'id="chapterMatrix"' in html
    assert 'id="currentBlocker"' in html
    assert 'id="activityLog"' in html
    assert 'id="batchPreview"' in html
    assert 'id="resumePreview"' in html
    assert 'id="rerunPreview"' in html
    assert 'id="glossaryProgress"' in html
    assert 'id="glossaryDecisionPreview"' in html
    assert 'id="reportWorkspace"' in html
    assert 'id="dashboardGuardrails"' in html


def test_build_glossary_suggestion_snapshot_returns_provider_options():
    from novel_pipeline.operator_ui import build_glossary_suggestion_snapshot
    from novel_pipeline.types import TermSuggestion

    config = Mock()
    config.workspace = Mock()
    config.workspace.prompts = Path("prompts")
    config.provider_for_stage.return_value = Mock()
    with patch("novel_pipeline.operator_ui.build_glossary_queue_snapshot", return_value={
        "items": [{
            "original_term": "实太阳神",
            "chapter_id": "ch020",
            "first_seen_block": "ch020-block-004",
            "category": "title",
            "context": "ctx",
        }]
    }), patch("novel_pipeline.operator_ui.build_term_suggestion", return_value=TermSuggestion(
        original_term="实太阳神",
        category="title",
        context=("ctx",),
        options=("สุริยเทพที่แท้จริง", "สุริยเทพแท้", "เทพสุริยะองค์จริง"),
        rationales=("a", "b", "c"),
        rationale="summary",
        provider="claude",
    )):
        snapshot = build_glossary_suggestion_snapshot(config, "batch-1", "实太阳神")

    assert snapshot["term"] == "实太阳神"
    assert snapshot["options"][0] == "สุริยเทพที่แท้จริง"
    assert snapshot["provider"] == "claude"


def test_execute_glossary_decision_approve_commits_when_queue_is_empty():
    from novel_pipeline.operator_ui import execute_glossary_decision
    from novel_pipeline.types import TextBlock

    config = Mock()
    config.workspace = Mock()
    config.workspace.glossary_dir = Path("01_Glossary")
    config.workspace.templates_dir = Path("templates")
    config.workspace.work = Path("04_Work")
    config.ledger_path = Path("06_Logs/run_ledger.jsonl")
    config.source_language = "zh"
    config.novel_id = "deep-sea-embers"

    artifact = {"schema_version": 1, "scope": {"type": "batch", "id": "batch-1"}, "chapter_ids": ["ch020"], "items": []}
    initial_queue = {"items": [{
        "original_term": "实太阳神",
        "chapter_id": "ch020",
        "first_seen_block": "ch020-block-004",
        "category": "title",
        "source_language": "zh",
        "novel": "deep-sea-embers",
    }]}
    refreshed_queue = {"items": [{
        "original_term": "实太阳神",
        "chapter_id": "ch020",
        "first_seen_block": "ch020-block-004",
        "category": "title",
        "source_language": "zh",
        "novel": "deep-sea-embers",
    }]}
    final_queue = {"run_id": "batch-1", "chapter_ids": ["ch020"], "items": [], "removed_terms": []}
    blocks = [TextBlock(block_id="ch020-block-004", chapter_id="ch020", block_index=4, source_text="...", text="...")]

    with patch("novel_pipeline.operator_ui._read_batch_glossary_artifact", return_value=artifact), \
         patch("novel_pipeline.operator_ui.build_glossary_queue_snapshot", side_effect=[initial_queue, refreshed_queue, final_queue]), \
         patch("novel_pipeline.operator_ui._load_chapter_source_and_blocks", return_value=(None, blocks)), \
         patch("novel_pipeline.operator_ui._revalidate_glossary_queue_items", return_value=([], [])), \
         patch("novel_pipeline.operator_ui._write_batch_glossary_artifact") as write_artifact, \
         patch("novel_pipeline.operator_ui.write_glossary_note") as write_note, \
         patch("novel_pipeline.operator_ui._load_term_template", return_value="template"), \
         patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value={"run_id": "batch-1"}), \
         patch("novel_pipeline.operator_ui.RunLedger") as MockLedger, \
         patch("novel_pipeline.operator_ui._commit_stage") as commit_stage:
        ledger = Mock()
        ledger.has_committed.return_value = False
        MockLedger.return_value = ledger
        result = execute_glossary_decision(
            config=config,
            run_id="batch-1",
            term="实太阳神",
            decision="approve",
            thai_term="สุริยเทพที่แท้จริง",
            note="operator note",
        )

    write_note.assert_called_once()
    written_entry = write_note.call_args.kwargs["entry"]
    assert written_entry.status == "approved"
    assert written_entry.thai_term == "สุริยเทพที่แท้จริง"
    write_artifact.assert_called_once()
    commit_stage.assert_called_once()
    assert result["committed"] is True


def test_execute_glossary_decision_reject_updates_queue_without_commit():
    from novel_pipeline.operator_ui import execute_glossary_decision
    from novel_pipeline.types import TextBlock

    config = Mock()
    config.workspace = Mock()
    config.workspace.glossary_dir = Path("01_Glossary")
    config.workspace.templates_dir = Path("templates")
    config.workspace.work = Path("04_Work")
    config.ledger_path = Path("06_Logs/run_ledger.jsonl")
    config.source_language = "zh"
    config.novel_id = "deep-sea-embers"

    artifact = {"schema_version": 1, "scope": {"type": "batch", "id": "batch-1"}, "chapter_ids": ["ch020"], "items": []}
    initial_queue = {"items": [{
        "original_term": "面具神",
        "chapter_id": "ch020",
        "first_seen_block": "ch020-block-004",
        "category": "entity",
        "source_language": "zh",
        "novel": "deep-sea-embers",
    }]}
    refreshed_queue = {"items": [{
        "original_term": "面具神",
        "chapter_id": "ch020",
        "first_seen_block": "ch020-block-004",
        "category": "entity",
        "source_language": "zh",
        "novel": "deep-sea-embers",
    }]}
    final_queue = {"run_id": "batch-1", "chapter_ids": ["ch020"], "items": [{"original_term": "实太阳神"}], "removed_terms": ["面具神"]}
    blocks = [TextBlock(block_id="ch020-block-004", chapter_id="ch020", block_index=4, source_text="...", text="...")]

    with patch("novel_pipeline.operator_ui._read_batch_glossary_artifact", return_value=artifact), \
         patch("novel_pipeline.operator_ui.build_glossary_queue_snapshot", side_effect=[initial_queue, refreshed_queue, final_queue]), \
         patch("novel_pipeline.operator_ui._load_chapter_source_and_blocks", return_value=(None, blocks)), \
         patch("novel_pipeline.operator_ui._revalidate_glossary_queue_items", return_value=([{"original_term": "实太阳神"}], ["面具神"])), \
         patch("novel_pipeline.operator_ui._write_batch_glossary_artifact") as write_artifact, \
         patch("novel_pipeline.operator_ui.write_glossary_note") as write_note, \
         patch("novel_pipeline.operator_ui._load_term_template", return_value="template"), \
         patch("novel_pipeline.operator_ui.build_operator_snapshot", return_value={"run_id": "batch-1"}), \
         patch("novel_pipeline.operator_ui._commit_stage") as commit_stage:
        result = execute_glossary_decision(
            config=config,
            run_id="batch-1",
            term="面具神",
            decision="reject",
            note="generic term",
        )

    written_entry = write_note.call_args.kwargs["entry"]
    assert written_entry.status == "rejected"
    assert written_entry.thai_term == ""
    write_artifact.assert_called_once()
    commit_stage.assert_not_called()
    assert result["committed"] is False


def test_cli_rejects_stop_after_without_range():
    """--stop-after without --range returns error."""
    from novel_pipeline.cli import cmd_run
    from unittest.mock import Mock, patch
    import sys
    
    # Mock config
    config = Mock()
    config.novel_id = "test"
    config.source.adapter = ""
    config.workspace.output = Mock()
    
    # Mock parse_chapter_range to avoid import errors
    with patch('novel_pipeline.text_utils.parse_chapter_range'):
        # Simulate args with stop_after but no chapter_range
        args = Mock(
            chapter_range="",
            stop_after="glossary-scan",
            chapter_id=None,
            adapter="",
            style_profile=None,
            run_id="batch-ch004-ch008-v2",
            force=False,
            input_file=None,
            text=None,
            title=""
        )
        # Redirect stderr to capture error
        original_stderr = sys.stderr
        sys.stderr = sys.stdout
        try:
            result = cmd_run(args, config)
            assert result == 1, f"Expected exit code 1, got {result}"
        finally:
            sys.stderr = original_stderr
    print("✓ CLI rejects stop-after without range")


def test_max_calls_per_scan_zero_disables_provider():
    """max_calls_per_scan=0 should disable provider calls entirely."""
    from novel_pipeline.types import AppConfig, TextBlock
    from novel_pipeline.stages.glossary import build_glossary_scan_queue
    from unittest.mock import Mock, patch
    
    # Create a mock config with max_calls_per_scan=0
    config = Mock(spec=AppConfig)
    config.stage_routing = {
        "term_extraction": Mock(
            provider="gemini",
            model="pro",
            max_calls_per_scan=0,
            max_failures_per_scan=1,
        )
    }
    config.provider_for_stage = Mock(return_value=Mock(name="gemini"))
    config.stage_routing_for = Mock(return_value=config.stage_routing["term_extraction"])
    config.workspace.glossary_dir = Mock()
    config.source_language = "zh"
    config.novel_id = "test"
    config.workspace.prompts = Mock()

    # Create blocks with real Chinese text where terms appear multiple times
    # Using text where "邓肯" appears 3 times, "失乡号" appears 3 times, etc.
    blocks = [
        TextBlock(
            block_id="ch001-block-001",
            chapter_id="ch001",
            source_text="白橡木号驶入幽邃深海。邓肯听见呼啸声。失乡号仍在雾中。邓肯看着失乡号。邓肯船长在船上。",
            source_language="zh",
            block_index=0,
            start_offset=0,
            end_offset=60
        ),
        TextBlock(
            block_id="ch001-block-002",
            chapter_id="ch001",
            source_text="周铭站在甲板上，望着浓雾中的失乡号。周铭看着邓肯。周铭船长也在。",
            source_language="zh",
            block_index=1,
            start_offset=60,
            end_offset=100
        )
    ]

    # Mock PromptStore and ProviderRunner
    with patch('novel_pipeline.stages.glossary.PromptStore') as MockPromptStore:
        mock_render = Mock(return_value="extract prompt")
        MockPromptStore.return_value.render = mock_render
        with patch('novel_pipeline.stages.glossary.ProviderRunner') as MockRunner:
            mock_instance = Mock()
            MockRunner.return_value = mock_instance
            with patch('novel_pipeline.stages.glossary.load_glossary_index') as mock_load:
                mock_load.return_value = {}
                queue = build_glossary_scan_queue(config, blocks, exclude_existing=False)

    # ProviderRunner should NEVER be called when max_calls_per_scan=0
    assert MockRunner.call_count == 0, "ProviderRunner should not be instantiated"
    assert mock_instance.run_with_retry.call_count == 0, "run_with_retry should not be called"
    
    # Queue should still contain deterministic candidates
    assert len(queue) > 0, "Queue should contain deterministic candidates"
    
    # Verify some expected deterministic candidates
    candidate_terms = [item["original_term"] for item in queue]
    print(f"Deterministic candidates found: {candidate_terms}")
    
    # Check for expected terms from the Chinese text
    # "邓肯" appears 4 times, "失乡号" appears 3 times, "周铭" appears 3 times
    expected_terms = ["邓肯", "失乡号", "周铭"]
    found_terms = [term for term in expected_terms if any(term in candidate for candidate in candidate_terms)]
    print(f"Found expected terms: {found_terms}")
    # At least some terms should be found
    assert len(found_terms) > 0, f"Expected at least some terms from {expected_terms}, found none"
    
    print("✓ max_calls_per_scan=0 disables provider calls while still producing deterministic candidates")


def test_run_batch_pipeline_stop_after_glossary_scan():
    """run_batch_pipeline with stop-after glossary-scan does not enter approval."""
    from novel_pipeline.pipeline import run_batch_pipeline
    from unittest.mock import Mock, patch, MagicMock
    
    # Mock config
    config = Mock()
    config.source.adapter = ""
    config.source_language = "zh"
    config.novel_id = "test"
    config.chunking.chinese_character_limit = 600
    config.chunking.non_chinese_word_limit = 300
    config.workspace.work = Mock()
    config.workspace.raw = Mock()
    config.workspace.output = Mock()
    config.workspace.logs_dir = Mock()
    config.workspace.prompts = Mock()
    config.workspace.glossary_dir = Mock()
    config.workspace.templates_dir = Mock()
    config.ledger_path = Mock()
    config.default_style_profile = "default"
    config.stage_routing = {}
    config.provider_for_stage = Mock(return_value=Mock(name="gemini"))
    config.fallback_provider_for_stage = Mock(return_value=None)
    config.stage_model_for = Mock(return_value="")
    config.fallback_model_for = Mock(return_value="")
    
    # Mock ledger
    mock_ledger = Mock()
    mock_ledger.has_committed = Mock(return_value=False)
    mock_ledger.append_stage = Mock()
    mock_ledger.path.exists = Mock(return_value=True)
    
    # Mock other dependencies
    with patch('novel_pipeline.pipeline.RunLedger', return_value=mock_ledger), \
         patch('novel_pipeline.pipeline.PromptStore'), \
         patch('novel_pipeline.pipeline.run_fetch_stage') as mock_fetch, \
         patch('novel_pipeline.pipeline.split_blocks') as mock_split, \
         patch('novel_pipeline.pipeline.build_glossary_scan_queue') as mock_scan_queue, \
         patch('novel_pipeline.pipeline._write_glossary_scan_artifact'), \
         patch('novel_pipeline.pipeline._load_glossary_index_from_queue'), \
         patch('novel_pipeline.pipeline._read_glossary_scan_artifact'), \
         patch('novel_pipeline.pipeline.build_term_suggestion') as mock_suggestion, \
         patch('novel_pipeline.pipeline.choose_option_interactively') as mock_choose, \
         patch('novel_pipeline.pipeline.write_glossary_note'), \
         patch('novel_pipeline.pipeline._process_block'):
        
        # Setup mocks
        mock_fetch.return_value = Mock(raw_text="dummy", chapter_id="ch004")
        mock_split.return_value = []
        mock_scan_queue.return_value = []
        
        # Call run_batch_pipeline with stop_after
        results = run_batch_pipeline(
            config=config,
            chapter_ids=["ch004", "ch005"],
            stop_after="glossary-scan"
        )
        
        # Should return empty list
        assert results == []
        # Should NOT call term suggestion or interactive approval
        mock_suggestion.assert_not_called()
        mock_choose.assert_not_called()
        # Should have called fetch and scan queue
        mock_fetch.assert_called()
        mock_scan_queue.assert_called()
    print("✓ run_batch_pipeline stop-after glossary-scan works")


def test_classify_command_too_long():
    """classify_provider_response returns 'command_too_long' for Gemini error."""
    from novel_pipeline.providers.base import classify_provider_response, ProviderResponse
    # Simulate Gemini exit with "The command line is too long."
    response = ProviderResponse(
        provider="gemini",
        command=(),
        stdout="",
        stderr="The command line is too long.",
        returncode=1,
    )
    assert classify_provider_response(response) == "command_too_long"
    # Also test our preflight error message
    response2 = ProviderResponse(
        provider="gemini",
        command=(),
        stdout="",
        stderr="Command line would exceed safe Windows length (estimated 25000 chars > limit 24000). Configure prompt_transport: stdin or reduce prompt size.",
        returncode=126,
    )
    assert classify_provider_response(response2) == "command_too_long"
    # Also test "argument list too long" (Unix-like)
    response3 = ProviderResponse(
        provider="gemini",
        command=(),
        stdout="",
        stderr="argument list too long",
        returncode=1,
    )
    assert classify_provider_response(response3) == "command_too_long"
    print("✓ classify_command_too_long passes")


def test_preflight_blocks_long_argv_prompt():
    """ProviderRunner preflight prevents subprocess call for long argv prompt."""
    from novel_pipeline.providers.base import ProviderRunner, ProviderSpec, ProviderRequest, ProviderResponse
    from unittest.mock import patch, Mock
    import os
    # Create spec with low limit
    spec = ProviderSpec(
        name="gemini",
        executable=("gemini",),
        prompt_flag="-p",
        prompt_position="flag",
        prompt_transport="argv",
        model_flag="--model",
        default_model="pro",
        max_command_chars=1000,
    )
    runner = ProviderRunner(spec)
    request = ProviderRequest(
        prompt="x" * 2000,
        provider="gemini",
        stage="qa_judge",
        model="pro",
    )
    # Patch os.name to be Windows
    with patch("os.name", "nt"):
        # Patch subprocess.run to ensure it's not called
        with patch("subprocess.run") as mock_subprocess:
            response = runner.run(request, check=False)
            # subprocess.run should NOT be called
            mock_subprocess.assert_not_called()
            # Verify response indicates command_too_long
            assert response.returncode == 126
            assert "command line would exceed" in response.stderr.lower()
            assert "estimated" in response.stderr.lower() and "limit" in response.stderr.lower()
            # Verify classification
            from novel_pipeline.providers.base import classify_provider_response
            assert classify_provider_response(response) == "command_too_long"
            # Verify command does NOT contain the huge prompt
            assert any("OMITTED" in str(arg) for arg in response.command)
    print("✓ preflight_blocks_long_argv_prompt passes")


def test_preflight_blocks_before_unicode_wrapper():
    """Long Unicode argv prompts are blocked before temp wrapper creation."""
    from novel_pipeline.providers.base import ProviderRunner, ProviderSpec, ProviderRequest
    from unittest.mock import patch
    spec = ProviderSpec(
        name="gemini",
        executable=("gemini",),
        prompt_flag="-p",
        prompt_position="flag",
        prompt_transport="argv",
        model_flag="--model",
        default_model="pro",
        max_command_chars=1000,
    )
    runner = ProviderRunner(spec)
    request = ProviderRequest(
        prompt="ภาษาไทย" * 400,
        provider="gemini",
        stage="qa_judge",
        model="pro",
    )
    with patch("os.name", "nt"), \
         patch("novel_pipeline.providers.base._build_windows_unicode_wrapper") as mock_wrapper, \
         patch("subprocess.run") as mock_subprocess:
        response = runner.run(request, check=False)
        mock_wrapper.assert_not_called()
        mock_subprocess.assert_not_called()
        assert response.returncode == 126
        assert "command line would exceed" in response.stderr.lower()
        assert any("OMITTED" in str(arg) for arg in response.command)
    print("preflight_blocks_before_unicode_wrapper passes")


def test_stdin_providers_not_blocked():
    """stdin providers are not blocked by long prompt."""
    from novel_pipeline.providers.base import ProviderRunner, ProviderSpec, ProviderRequest
    from unittest.mock import patch, Mock
    import subprocess
    # Create spec with stdin transport
    spec = ProviderSpec(
        name="claude",
        executable=("claude",),
        prompt_flag="-p",
        prompt_position="flag",
        prompt_transport="stdin",
        model_flag="--model",
        default_model="sonnet",
        max_command_chars=1000,
    )
    runner = ProviderRunner(spec)
    request = ProviderRequest(
        prompt="x" * 2000,
        provider="claude",
        stage="refinement",
        model="sonnet",
    )
    # Mock subprocess.run to return success
    with patch("subprocess.run") as mock_subprocess:
        mock_completed = Mock()
        mock_completed.returncode = 0
        mock_completed.stdout = "mock output"
        mock_completed.stderr = ""
        mock_subprocess.return_value = mock_completed
        # Run on Windows (os.name nt)
        with patch("os.name", "nt"):
            response = runner.run(request, check=False)
            # subprocess.run should have been called
            mock_subprocess.assert_called_once()
            # Verify prompt was passed via stdin (input parameter)
            call_kwargs = mock_subprocess.call_args[1]
            assert "input" in call_kwargs
            assert call_kwargs["input"] == request.prompt
            # Verify command includes prompt_flag but not prompt in argv
            command_args = call_kwargs["args"]
            assert "-p" in command_args
            assert request.prompt not in command_args
            # Ensure response is successful
            assert response.returncode == 0
    print("✓ stdin_providers_not_blocked passes")


def test_config_parses_max_command_chars():
    """ProviderSpec.from_mapping parses max_command_chars."""
    from novel_pipeline.types import ProviderSpec
    # Valid value
    spec = ProviderSpec.from_mapping("gemini", {"max_command_chars": 1234})
    assert spec.max_command_chars == 1234
    # Default
    spec2 = ProviderSpec.from_mapping("gemini", {})
    assert spec2.max_command_chars == 24000
    # Invalid low value raises ValueError
    try:
        ProviderSpec.from_mapping("gemini", {"max_command_chars": 500})
        assert False, "Expected ValueError for max_command_chars < 1000"
    except ValueError as e:
        assert "max_command_chars must be >= 1000" in str(e)
    print("✓ config_parses_max_command_chars passes")


if __name__ == "__main__":
    test_format_glossary_subset()
    test_parse_literal_pairs()
    test_format_inline_dialogue_quotes()
    test_format_non_dialogue_quotes()
    test_format_non_dialogue_quoted_term_followed_by_prose()
    test_format_space_handling()
    test_format_standalone_sound_effect()
    test_format_sound_effect_inside_prose()
    test_format_long_paragraph_splitting()
    test_format_no_quote_only_lines()
    test_format_standalone_khruet_sound_effect()
    test_format_quote_block_non_sound_not_italic()
    test_format_quote_block_sound_effect_italic()
    test_next_pending_stage_no_records()
    test_retry_quota_success()
    test_retry_auth_not_retried()
    test_retry_auth_nonzero_not_retried()
    test_retry_backoff_delay()
    test_retry_nonzero_exit_with_retry_on_nonzero()
    test_stage_routing_parses_ordered_fallbacks()
    test_codex_stdin_command_shape_for_refinement_fallback()
    test_config_refinement_fallback_chain_order()
    test_extract_provider_candidate_terms_retry_quota_success()
    test_build_term_suggestion_rejects_quota_meta()
    test_build_term_suggestion_returns_provider_options()
    test_piaotia_extract_legacy_content_div()
    test_piaotia_extract_h1_anonymous_wrapper()
    test_piaotia_extract_content_class_variant()
    test_piaotia_extract_stops_on_ad_comment_or_text()
    test_piaotia_extract_ignores_head_stop_marker()
    test_piaotia_extract_does_not_treat_ad_content_class_as_body()
    test_piaotia_extract_closes_explicit_content_container()
    test_piaotia_extract_raises_on_empty_body()
    test_piaotia_toc_accepts_relative_absolute_and_dedupes()
    test_piaotia_extract_rejects_mojibake()
    test_batch_glossary_artifact_path()
    test_glossary_scan_validates_source_mojibake()
    test_stage_routing_parses_timeout_and_retry()
    test_term_extraction_timeout_override()
    test_provider_timeout_fallback()
    test_batch_artifact_write()
    test_status_run_fetched_only_pre_batch()
    test_status_run_reports_effective_failure_fields()
    test_validate_formatted_text_detects_problem_markers()
    test_qa_escalation_stop_raises_without_input()
    test_qa_rule_warning_does_not_block_ai_pass()
    test_qa_glossary_missing_term_blocks_when_refinement_removed_literal_term()
    test_qa_ai_judge_finding_still_blocks()
    test_format_command_rejects_invalid_formatted_text()
    # New tests for scan-level circuit breaker
    test_stage_routing_parses_scan_budget_fields()
    test_scan_level_failure_circuit_breaker()
    test_scan_level_max_call_cap()
    test_provider_meta_quota_output_rejected()
    test_cli_parser_accepts_stop_after_flag()
    test_cli_parser_accepts_resume_manual_action_mode_stop()
    test_cli_parser_accepts_resume_bounded_flags()
    test_cli_parser_accepts_inspect_block()
    test_cli_parser_accepts_report_subcommands()
    test_cli_parser_accepts_init_novel()
    test_style_profile_from_mapping_parses_structured_fields_and_legacy_description()
    test_initialize_novel_project_scaffolds_expected_files_and_rewrites_codex_cd()
    test_initialize_novel_project_selects_style_profile_from_genre_or_default()
    test_research_profile_from_config_and_context_text()
    test_research_profile_readiness_classification()
    test_research_profile_missing_file_is_visible_but_not_blocking()
    test_research_profile_config_loads_review_metadata()
    test_research_profile_invalid_status_rejected()
    test_build_preflight_summary_reports_provider_and_git_state()
    test_preflight_report_generation_writes_expected_markdown()
    test_recovery_drill_report_generation_writes_expected_markdown()
    test_literal_translation_stage_uses_research_context()
    test_refine_stage_uses_research_context()
    test_qa_stage_uses_research_context()
    test_refine_stage_uses_structured_style_instructions()
    test_qa_stage_uses_structured_style_instructions()
    test_cmd_resume_returns_two_on_manual_action_required()
    test_cmd_preflight_returns_one_when_blocked()
    test_resume_pipeline_stops_before_chapter_after_until_chapter()
    test_resume_chapter_stops_after_until_block()
    test_resume_chapter_stops_after_completed_until_block()
    test_resume_chapter_force_stops_after_until_block_and_uses_stop_mode()
    test_inspect_block_command_reports_artifacts_and_validation()
    test_checkpoint_report_generation_writes_expected_markdown()
    test_cleanliness_report_flags_body_issues_and_ignores_title_han()
    test_cmd_report_cleanliness_returns_nonzero_on_missing_output()
    test_product_review_report_generation_writes_expected_markdown()
    test_provider_usage_report_generation_writes_expected_markdown()
    test_glossary_decisions_report_generation_writes_expected_markdown()
    test_glossary_conflicts_report_generation_writes_expected_markdown()
    test_glossary_audit_report_generation_writes_expected_markdown()
    test_build_glossary_queue_snapshot_revalidates_items()
    test_execute_operator_action_requires_bounded_resume()
    test_execute_operator_action_resume_uses_stop_mode_and_returns_snapshot()
    test_execute_operator_action_rerun_block_dispatches_expected_args()
    test_execute_operator_action_run_batch_scan_only_dispatches_expected_args()
    test_execute_operator_action_run_batch_bounded_dispatches_expected_args()
    test_execute_operator_action_run_batch_rejects_invalid_stop_after()
    test_execute_operator_action_run_batch_rejects_missing_run_id_or_chapter_range()
    test_execute_operator_action_init_novel_dispatches_expected_args()
    test_execute_operator_action_init_novel_rejects_missing_required_fields()
    test_execute_operator_action_init_novel_parses_aliases_from_ui_payload()
    test_execute_operator_action_save_research_profile_updates_yaml()
    test_operator_snapshot_includes_research_readiness()
    test_operator_snapshot_includes_research_profile_data()
    test_operator_snapshot_includes_preflight()
    test_operator_snapshot_includes_command_hints_and_quick_links()
    test_operator_snapshot_separates_active_and_archived_reports()
    test_build_glossary_suggestion_snapshot_returns_provider_options()
    test_execute_glossary_decision_approve_commits_when_queue_is_empty()
    test_execute_glossary_decision_reject_updates_queue_without_commit()
    test_generate_operator_report_dispatches_supported_kinds()
    test_cli_rejects_stop_after_without_range()
    test_run_batch_pipeline_stop_after_glossary_scan()
    test_classify_command_too_long()
    test_preflight_blocks_long_argv_prompt()
    test_preflight_blocks_before_unicode_wrapper()
    test_stdin_providers_not_blocked()
    test_config_parses_max_command_chars()
    print("All tests passed!")
