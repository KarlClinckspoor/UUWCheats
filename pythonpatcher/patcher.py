from pathlib import Path
from hashlib import sha256
import json


class Diff:
    def __init__(self, offset: int | str, original: int | str, new: int | str):
        self.offset = offset if isinstance(offset, int) else int(offset, 16)
        self.original = original if isinstance(original, int) else int(original, 16)
        self.new = new if isinstance(new, int) else int(new, 16)

    def to_json(self):
        return f'{{"offset": {str(self.offset)}, "original": {str(self.original)}, "new": {str(self.new)}}}'

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

    def revert_patch(self, buffer: list[int]):
        for diff in self.diffs:
            buffer[diff.offset] = diff.original


class CollectionOfPatches:
    def __init__(self, patches: list[Patch], exec_hash: str):
        self.patches = patches
        self.exec_hash = exec_hash

    def to_json(self) -> str:
        p1 = '{"patches":[' + "".join(([patch.to_json() for patch in self.patches])) + '],'
        p2 = p1 + '"exec_hash":"' + self.exec_hash + '"}'
        return p2

    @classmethod
    def from_json(cls, json_content: dict) -> 'CollectionOfPatches':
        return cls(**json_content)


class Patcher:
    def __init__(self, original_buffer: list[int], collection_of_patches: CollectionOfPatches):
        current_sha = sha256(bytes(original_buffer)).hexdigest().upper()
        if current_sha != collection_of_patches.exec_hash:
            raise Warning(f"Expected SHA-256 checksum {collection_of_patches.exec_hash} but got {current_sha}")

        self.original_buffer = original_buffer
        self.patched_buffer = original_buffer.copy()
        self.collection_of_patches = collection_of_patches

    def apply_all_patches(self):
        for patch in self.collection_of_patches.patches:
            patch.apply_patch(self.patched_buffer)
        print("Applied all patches")

    def revert_all_patches(self):
        for patch in self.collection_of_patches.patches:
            patch.revert_patch(self.patched_buffer)
        print("Reverted all patches")

    def select_and_apply_specific_patches(self):
        for i, patch in self.collection_of_patches.patches:
            print(f"{i + 1:02d}: {patch.meaning}")
        inp = input("Type the patch numbers separated by commas (e.g. 1,3,4): ")
        selected = list(map(lambda x: int(x.strip()), inp.split(",")))
        for i in selected:
            patch = self.collection_of_patches.patches[i - 1]
            patch.apply_patch(self.patched_buffer)
            print(f"Applied patch: {patch.meaning}")
        print("Done")

    def save_to_file(self, filepath: str | Path):
        with open(filepath, "wb") as f:
            f.write(bytes(self.patched_buffer))


def test():
    patch_Lore = Patch([Diff(0x28DA0, 0x04, 0x01)], "Allow sequential Lore checks on the same item")
    patch_skill_check_critical_success = Patch(meaning="Every skill check is a critical success",
                                               diffs=[
                                                   Diff(0x35022, 0x1, 0x2),
                                                   Diff(0x3502B, 0x33, 0x66),
                                                   Diff(0x3502C, 0xC0, 0x90),
                                                   Diff(0x35030, 0xFF, 0x02),
                                                   Diff(0x35031, 0xFF, 0x00)
                                               ]
                                               )
    collection = CollectionOfPatches([patch_Lore, patch_skill_check_critical_success], "BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9")
    json_content_test = json.dumps(json.loads(collection.to_json()), indent=2)
    json_content_manual = open("patches/uw2_gog.json").read()
    assert json_content_test == json_content_manual

if __name__ == '__main__':
    test()
