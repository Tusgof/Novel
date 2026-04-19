from __future__ import annotations

import re
from typing import List

from novel_pipeline.text_utils import normalize_whitespace


def _convert_standalone_quotes(text: str) -> str:
    """Remove standalone quote lines (quotes on separate lines) keeping content.

    Pattern:
        "
        content
        "
    Removes the quote lines, leaving the content line as-is.
    """
    lines = text.splitlines()
    i = 0
    new_lines = []
    while i < len(lines):
        if i + 2 < len(lines) and lines[i].strip() == '"' and lines[i+2].strip() == '"':
            # Keep content line as-is (may be empty)
            new_lines.append(lines[i+1])
            i += 3
            continue
        new_lines.append(lines[i])
        i += 1
    return "\n".join(new_lines)


# Thai speech cues that indicate dialogue before a quote
_THAI_SPEECH_CUES = {
    'พูดว่า', 'ถามว่า', 'ตอบว่า', 'ร้องว่า', 'ตะโกนว่า', 'กล่าวว่า', 'เอ่ยว่า',
    'พูด', 'ถาม', 'ตอบ', 'ร้อง', 'ตะโกน', 'กล่าว', 'เอ่ย', 'เสียง',
}
# Thai onomatopoeia patterns (sound-effect words)
_THAI_ONOMATOPOEIA = {
    'แคร็ก', 'กริ้ง', 'กริ่ง', 'ปรื๊ด', 'ปื๊ด', 'คราง', 'ครืด', 'ฮึ', 'เฮือก',
    'โครม', 'ครืน', 'แกร๊ก', 'กึก', 'กัก', 'ก้อง', 'ตึง', 'ตาย', 'ตูม',
    'ตุ้ม', 'ปัง', 'เปรี๊ยะ', 'ฟิ้ว', 'หวือ', 'หืม', 'ฮืม',
}
_SENTENCE_END_PUNCTUATION = '.?!。？！'
_MAX_NONDIALOGUE_LENGTH = 40


def _strip_non_dialogue_quotes(text: str) -> str:
    """Remove quotes around short inline non-dialogue terms/labels.

    Conservative heuristic:
    - Quoted content length <= _MAX_NONDIALOGUE_LENGTH
    - No sentence-ending punctuation inside
    - Not preceded by colon or Thai speech cue
    - Not followed by Thai speech attribution
    - Not part of a longer dialogue paragraph
    """
    # Process paragraph by paragraph to keep context local
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    for para in paragraphs:
        # Find all quoted segments
        # We'll iterate over matches and decide replacement
        # Use a while loop with regex search
        new_para = para
        # We need to replace from end to start to avoid offset issues
        # Collect matches with positions
        matches = list(re.finditer(r'"([^"]+)"', para))
        replacements = []
        for match in matches:
            quoted_content = match.group(1)
            start, end = match.start(), match.end()
            # Determine if dialogue
            is_dialogue = False
            # Length check
            if len(quoted_content) > _MAX_NONDIALOGUE_LENGTH:
                is_dialogue = True
            # Sentence-ending punctuation inside
            if any(punc in quoted_content for punc in _SENTENCE_END_PUNCTUATION):
                is_dialogue = True
            # Preceding context (up to 20 chars before quote)
            preceding = para[max(0, start-20):start]
            if ':' in preceding or any(cue in preceding for cue in _THAI_SPEECH_CUES):
                is_dialogue = True
            # Following context (up to 20 chars after quote)
            following = para[end:min(len(para), end+20)]
            if any(cue in following for cue in _THAI_SPEECH_CUES):
                is_dialogue = True
            # If not dialogue, mark for quote removal
            if not is_dialogue:
                replacements.append((start, end, quoted_content))
        # Apply replacements from end to start
        for start, end, content in reversed(replacements):
            new_para = new_para[:start] + content + new_para[end:]
        # Collapse multiple spaces that may have been introduced
        new_para = re.sub(r' +', ' ', new_para)
        new_paragraphs.append(new_para)
    return '\n\n'.join(new_paragraphs)


def _format_sound_effects(text: str) -> str:
    """Convert standalone sound-effect paragraphs to italic.
    
    A paragraph qualifies if:
    - After stripping punctuation/ellipsis/repeated punctuation and whitespace,
      it is a short sound-effect token or a short sequence of such tokens.
    - Length of stripped paragraph <= 30 characters.
    - Contains at least one known onomatopoeia token.
    """
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    for para in paragraphs:
        stripped = para.strip()
        # Remove surrounding quotes if present (already handled by standalone quotes)
        if stripped.startswith('"') and stripped.endswith('"'):
            stripped = stripped[1:-1].strip()
        # Check length
        if len(stripped) > 30:
            new_paragraphs.append(para)
            continue
        # Remove punctuation/ellipsis, repeated punctuation
        # Keep only Thai characters and spaces
        cleaned = re.sub(r'[^\u0E00-\u0E7F\s]+', '', stripped)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # Split into tokens
        tokens = cleaned.split()
        # Check if any token is in onomatopoeia set
        if any(token in _THAI_ONOMATOPOEIA for token in tokens):
            # Italicize the original stripped paragraph
            new_paragraphs.append(f"*{stripped}*")
        else:
            new_paragraphs.append(para)
    return '\n\n'.join(new_paragraphs)


def _split_long_paragraphs(text: str, max_len: int = 550) -> str:
    """Split paragraphs longer than max_len at sentence boundaries.
    
    Only splits at sentence punctuation boundaries.
    Accumulates sentences into new paragraphs up to max_len.
    """
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    for para in paragraphs:
        if len(para) <= max_len:
            new_paragraphs.append(para)
            continue
        # Split into sentences
        # Use regex to split at sentence punctuation followed by space
        sentences = re.split(r'(?<=[.?!。？！…])\s+', para)
        if len(sentences) <= 1:
            # No safe split point
            new_paragraphs.append(para)
            continue
        # Recombine sentences into paragraphs
        current_chunk = []
        current_len = 0
        for sent in sentences:
            sent_len = len(sent)
            if current_len + sent_len + (1 if current_chunk else 0) > max_len and current_chunk:
                # Flush current chunk
                new_paragraphs.append(' '.join(current_chunk))
                current_chunk = [sent]
                current_len = sent_len
            else:
                current_chunk.append(sent)
                current_len += sent_len + (1 if current_chunk else 0)
        if current_chunk:
            new_paragraphs.append(' '.join(current_chunk))
    return '\n\n'.join(new_paragraphs)


def format_block_text(text: str) -> str:
    cleaned = normalize_whitespace(text)
    # Remove standalone quote lines while keeping their content.
    cleaned = _convert_standalone_quotes(cleaned)
    # Remove quote-splitting regexes (no longer needed)
    # Strip quotes from short non-dialogue terms
    cleaned = _strip_non_dialogue_quotes(cleaned)
    # Format standalone sound effects
    cleaned = _format_sound_effects(cleaned)
    # Split long paragraphs
    cleaned = _split_long_paragraphs(cleaned)
    # Ensure single blank line between paragraphs
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    # Final normalization of whitespace (remove extra spaces)
    cleaned = normalize_whitespace(cleaned)
    return cleaned.strip()
