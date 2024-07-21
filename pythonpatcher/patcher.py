from pathlib import Path
from hashlib import sha256
import json


class Diff:
    def __init__(self, offset: int | str, original: int | str, new: int | str):
        self.offset = offset if isinstance(offset, int) else int(offset, 16)
        self.original = original if isinstance(original, int) else int(original, 16)
        self.new = new if isinstance(new, int) else int(new, 16)

    def to_dict(self):
        return {
            "offset": hex(self.offset).upper()[2:],
            "original": hex(self.original).upper()[2:],
            "new": hex(self.new).upper()[2:],
        }


class Patch:
    def __init__(self, diffs: list[Diff], meaning: str | None = None):
        self.diffs = diffs
        self.meaning = meaning if meaning is not None else ""

    def to_dict(self) -> dict:
        return {
            "meaning": self.meaning,
            "diffs": [diff.to_dict() for diff in self.diffs],
        }

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
                f"Found mismatching content at offset {byte_pos} with value {byte_val} (byte {byte_pos}"
            )
        for diff in self.diffs:
            buffer[diff.offset] = diff.new

    def revert_patch(self, buffer: list[int]):
        for diff in self.diffs:
            buffer[diff.offset] = diff.original


class CollectionOfPatches:
    def __init__(self, patches: list[Patch], exec_hash: str):
        self.patches = patches
        self.exec_hash = exec_hash

    def to_dict(self) -> dict:
        return {
            "patches": [patch.to_dict() for patch in self.patches],
            "exec_hash": self.exec_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class Patcher:
    def __init__(
        self, original_buffer: list[int], collection_of_patches: CollectionOfPatches
    ):
        current_sha = sha256(bytes(original_buffer)).hexdigest().upper()
        if current_sha != collection_of_patches.exec_hash:
            raise Warning(
                f"Expected SHA-256 checksum {collection_of_patches.exec_hash} but got {current_sha}"
            )

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


def make_uw2_json_file():
    patch_Lore = Patch(
        [Diff(0x28DA0, 0x04, 0x01)], "Allow sequential Lore checks on the same item"
    )
    patch_skill_check_critical_success = Patch(
        meaning="Every skill check is a critical success",
        diffs=[
            Diff(0x35022, 0x1, 0x2),
            Diff(0x3502B, 0x33, 0x66),
            Diff(0x3502C, 0xC0, 0x90),
            Diff(0x35030, 0xFF, 0x02),
            Diff(0x35031, 0xFF, 0x00),
        ],
    )
    patch_increased_inventory_carry_capacity = Patch(
        meaning="Increase inventory carry capacity on level up",
        diffs=[
            Diff(0x9AE3A, 0x0D, 0x0E),
            Diff(0x9AE3B, 0x00, 0x00),
            Diff(0x9AE3F, 0x2C, 0x2D),
            Diff(0x9AE40, 0x01, 0x01),
        ],
    )
    patch_increased_max_vitality = Patch(
        meaning="Increase max vitality on level up",
        diffs=[
            Diff(0x9AE03, 0x1E, 0x1F),
            Diff(0x9ADFD, 0x05, 0x04),
        ],
    )
    patch_increase_max_mana = Patch(
        meaning="Increase max mana on level up",
        diffs=[
            Diff(0x9AE22, 0x3, 0x2),
        ],
    )

    patch_change_exp_for_level_up = Patch(
        meaning="Change experience for level up",
        diffs=[
            Diff(0x69376, 0x06, 0x05),
            Diff(0x69377, 0x08, 0x06),  # ... and so on
            Diff(0x35199, 0xF4, 0xFA),  # the multiplier
            Diff(0x3519A, 0x01, 0x00),
        ],
    )

    patch_increase_skill_points_earned = Patch(
        meaning="Increase skill points earned on level up",
        diffs=[
            Diff(0x350BB, 0xDC, 0xE8),
            Diff(0x350BC, 0x05, 0x03),
        ],
    )

    patch_increase_exp_points = Patch(
        meaning="Increase exp points gained", diffs=[Diff(0x3504A, 0x02, 0x01)]
    )

    patch_immortal = Patch(
        meaning="Prevents death",
        diffs=[
            Diff(0x27F46, 0x9A, 0x90),
            Diff(0x27F47, 0x75, 0x90),
            Diff(0x27F48, 0x00, 0x90),
            Diff(0x27F49, 0x99, 0x90),
            Diff(0x27F4A, 0x65, 0x90),
        ],
    )

    collection = CollectionOfPatches(
        [
            patch_Lore,
            patch_skill_check_critical_success,
            patch_increased_inventory_carry_capacity,
            patch_increased_max_vitality,
            patch_increase_max_mana,
            patch_change_exp_for_level_up,
            patch_increase_skill_points_earned,
            patch_increase_exp_points,
            patch_immortal,
        ],
        "BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9",
    )

    with open("patches/uw2_gog.json", "w") as f:
        f.write(collection.to_json())
