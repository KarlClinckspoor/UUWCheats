class Patch:

    def __init__(self, offset: int, original: list[int], new: list[int], meaning: str | None = None):
        if len(original) != len(new):
            raise ValueError("original and new must be the same length")
        self.offset = offset
        self.original = original
        self.new = new
        self.meaning = meaning if meaning is not None else ""

    def to_json(self) -> str:
        return f'{{"offset": {self.offset}, "original": {self.original}, "new": {self.new}, "meaning": "{self.meaning}"}}'

    @classmethod
    def from_json(cls, json_content: dict) -> 'Patch':
        return cls(**json_content)

    def check_if_content_is_expected(self, buffer: list[int]):
        for i, byte in enumerate(buffer[self.offset: self.offset + len(self.original)]):
            if byte != self.original[i]:
                return i, byte, False
        return -1, -1, True

    def apply_patch(self, buffer: list[int]):
        byte_pos, byte_val, result = self.check_if_content_is_expected(buffer)
        if not result:
            raise ValueError(
                f"Found mismatching content at offset {byte_pos} with value {byte_val} (byte {byte_pos}")
        for i, byte in enumerate(self.new):
            buffer[self.offset + i] = byte


class Patcher:
    def __init__(self, original_content: list[int], patches: list[Patch]):
        self.original_content = original_content
        self.patched_content = original_content.copy()
        self.patches = patches

    def apply_patches(self):
        for patch in self.patches:
            patch.apply_patch(self.patched_content)

    def to_json(self) -> str:
        return str([patch.to_json() for patch in self.patches])

    @classmethod
    def from_json(cls, json_content: dict) -> 'Patcher':
        return cls(**json_content)

    def save_to_file(self, filename: str):
        with open(filename, "wb") as f:
            f.write(bytes(self.patched_content))
