from pathlib import Path


class Diff:
    def __init__(self, offset: int | str, original: int | str, new: int | str):
        self.offset = offset if isinstance(offset, int) else int(offset, 16)
        self.original = original if isinstance(original, int) else int(original, 16)
        self.new = new if isinstance(new, int) else int(new, 16)

    def to_json(self):
        return f'{{"offset": {self.offset}, "original": {self.original}, "new": {self.new}}}'

    @classmethod
    def from_json(cls, json_content: dict):
        return cls(**json_content)


class Patch:

    def __init__(self, diffs: list[Diff], meaning: str | None = None):
        self.diffs = diffs
        self.meaning = meaning if meaning is not None else ""

    def to_json(self) -> str:
        return '[' + "".join(([diff.to_json() for diff in self.diffs])) + ']'

    @classmethod
    def from_json(cls, json_content: dict) -> 'Patch':
        return cls(**json_content)

    def check_if_content_is_expected(self, buffer: list[int]):
        for diff in self.diffs:
            byte_pos = diff.offset
            byte_val = buffer[byte_pos]
            if byte_val != diff.original:
                return byte_pos, byte_val, False
        return None, None, True

    def apply_patch(self, buffer: list[int]):
        byte_pos, byte_val, result = self.check_if_content_is_expected(buffer)
        if not result:
            raise ValueError(
                f"Found mismatching content at offset {byte_pos} with value {byte_val} (byte {byte_pos}")
        for diff in self.diffs:
            buffer[diff.offset] = diff.new


class Patcher:
    def __init__(self, original_buffer: list[int], patches: list[Patch]):
        self.original_buffer = original_buffer
        self.patched_buffer = original_buffer.copy()
        self.patches = patches

    def apply_patches(self):
        for patch in self.patches:
            patch.apply_patch(self.patched_buffer)

    def save_to_file(self, filepath: str | Path):
        with open(filepath, "wb") as f:
            f.write(bytes(self.patched_buffer))
