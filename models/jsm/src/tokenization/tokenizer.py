"""Minimal, deterministic, dependency-free UTF-8 tokenizer for JSM MVP previews.

This is REAL reversible byte tokenization, not a trained BPE/SentencePiece
tokenizer. Never label token IDs from this version as a production vocabulary.
Changing the mapping or special tokens requires a new tokenizer ID.
"""

class JSMByteTokenizer:
    """Map each UTF-8 byte b to b + 1; reserve explicit special token IDs.

    0 = PAD, 1..256 = raw UTF-8 byte values + 1,
    257 = BOS, 258 = EOS. Does not train or modify any model weights.
    """

    tokenizer_id = "jsm-byte-utf8-v0"
    pad_token_id = 0
    bos_token_id = 257
    eos_token_id = 258
    vocab_size = 259

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a Unicode string")
        body = [b + 1 for b in text.encode("utf-8")]
        if not add_special_tokens:
            return body
        return [self.bos_token_id, *body, self.eos_token_id]

    def decode(self, ids: list[int], *, strip_special_tokens: bool = True) -> str:
        if not isinstance(ids, (list, tuple)):
            raise TypeError("ids must be a list or tuple")
        if any(not isinstance(i, int) or isinstance(i, bool) or i < 0 or i >= self.vocab_size for i in ids):
            raise ValueError("Invalid token ID")
        raw = list(ids)
        if strip_special_tokens:
            if raw and raw[0] == self.bos_token_id:
                raw = raw[1:]
            if raw and raw[-1] == self.eos_token_id:
                raw = raw[:-1]
        if any(i < 1 or i > 256 for i in raw):
            raise ValueError("Unexpected special token in UTF-8 byte sequence")
        return bytes(i - 1 for i in raw).decode("utf-8", errors="strict")
