var buffer;
class BufferMismatchError extends Error {
}
class OptionsError extends Error {
}
async function loadExecutable() {
    var uw2_gog_hash = "BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9";
    const fileInput = document.getElementById("path_to_executable");
    const filePath = fileInput.files[0];
    if (filePath) {
        buffer = new Uint8Array(await filePath.arrayBuffer());
        if (buffer) {
            var hash = await getHash();
            document.getElementById("executable_hash").innerText = hash;
            document.getElementById("hash_ok").innerText = hash === uw2_gog_hash ? "Buffer matches hash, good to go" : "Wrong version - buffer mismatch";
        }
        ;
    }
}
async function getHash() {
    const hashBuffer = await window.crypto.subtle.digest("SHA-256", buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    return hashHex.toUpperCase();
}
function separateShortIntoTwoBytes(int) {
    return [int & 0xFF, (int >> 8) & 0xFF];
}
function applyPatches() {
    if (buffer === undefined) {
        throw new Error("buffer wasn't loaded!");
    }
    var bufferCopy = new Uint8Array(buffer); // Copy in case we need to revert.
    var inputs = document.getElementsByClassName("options");
    var selectedInputs = Array.prototype.filter.call(inputs, (input) => input.checked);
    var functionMaps = {
        "increase_carry_weight": applyCarryWeightPatch,
        "critical_skill_checks": applyCriticalSkillChecks,
        "allow_sequential_lore_checks": applySequentialLoreChecks,
        "increase_max_vitality_on_level_up": applyIncreaseVitalityOnLevelUp,
        "increase_max_mana_on_level_up": applyIncreaseManaOnLevelUp,
        "change_experience_required_for_level_ups": applyEXPThresholds,
        "increase_number_of_skill_points_earned": applyIncreaseNumberOfSkillPointsEarned,
        "increase_exp_point_gain": applyIncreaseEXPPointGain,
        "prevent_death": applyPreventDeath,
        "increase_health_regen": applyHPRegen,
        "increase_mana_regen": applyMPRegen,
        "longer_lasting_light_sources": applyLongerLastingLightSource,
        "neverending_spells": applyLongerLastingSpells,
        default: () => { throw new Error("Unknown patch. BUG! REPORT!"); }
    };
    for (var input of selectedInputs) {
        try {
            functionMaps[input.id](buffer);
        }
        catch (e) {
            buffer = bufferCopy; // Restoring buffer to previous state.
            if (e instanceof BufferMismatchError) {
                log(`${input.id} buffer error: ` + e.message);
            }
            else if (e instanceof OptionsError) {
                log(`${input.id} options error: ` + e.message);
            }
            else {
                log(`${input.id} unknown error: ` + e.message);
            }
        }
    }
    // After patches are applied, download the patched executable.
    var b = new Blob([buffer], { type: "application/octet-stream" });
    var u = URL.createObjectURL(b);
    const a = document.createElement("a");
    a.href = u;
    a.download = "UW2P.exe";
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(u);
    document.body.removeChild(a);
}
function applySequentialLoreChecks() {
    if (buffer[0x28DA0] != 0x04) {
        throw new BufferMismatchError("Sequential lore checks: buffer error.");
    }
    buffer[0x28DA0] = 0x00;
}
function applyCriticalSkillChecks() {
    if (buffer[0x35015] != 0x7E || buffer[0x35016] != 0x05) {
        throw new BufferMismatchError("Critical skill checks: buffer error");
    }
    ;
    buffer[0x35015] = 0x90;
    buffer[0x35016] = 0x90;
}
function applyCarryWeightPatch() {
    if (buffer[0x9AE3A] != 0x0D || buffer[0x9AE3B] != 0x00 || buffer[0x9AE3F] != 0x2C || buffer[0x9AE40] != 0x01) {
        throw new BufferMismatchError("Carry weight: buffer error");
    }
    var multiplier = guardedParseInt(document.getElementById("carry_weight_multiplier").value);
    var offset = guardedParseInt(document.getElementById("carry_weight_offset").value);
    if (multiplier < 0) {
        throw new OptionsError("Carry weight: multiplier must be greater than or equal to 0");
    }
    if (offset < 0) {
        throw new OptionsError("Carry weight: offset must be greater than or equal to 0");
    }
    let multiplier_low, multiplier_high, offset_low, offset_high;
    [multiplier_low, multiplier_high] = separateShortIntoTwoBytes(multiplier);
    [offset_low, offset_high] = separateShortIntoTwoBytes(offset);
    buffer[0x9AE3A] = multiplier_low;
    buffer[0x9AE3B] = multiplier_high;
    buffer[0x9AE3F] = offset_low;
    buffer[0x9AE40] = offset_high;
}
function applyIncreaseVitalityOnLevelUp() {
    if (buffer[0x9AE03] != 0x1E || buffer[0x9ADFD] != 0x05) {
        throw new BufferMismatchError("Increased vitality: buffer mismatch");
    }
    var offset = guardedParseInt(document.getElementById("max_vitality_offset").value);
    var divisor = guardedParseInt(document.getElementById("max_vitality_divisor").value);
    if (offset < 0) {
        throw new OptionsError("Increased vitality: offset must be greater than or equal to 0");
    }
    if (divisor <= 0) {
        throw new OptionsError("Increased vitality: divisor must be greater than 0!");
    }
    buffer[0x9AE03] = offset & 0xFF;
    buffer[0x9ADFD] = divisor & 0xFF;
}
function applyIncreaseManaOnLevelUp() {
    if (buffer[0x9AE22] != 0x03) {
        throw new BufferMismatchError("Increased mana: buffer mismatch");
    }
    var divisor = guardedParseInt(document.getElementById("max_mana_divisor").value);
    if (divisor < 0) {
        throw new OptionsError("Increased mana: Divisor must be greater or equal to 0!");
    }
    if (divisor % 2 != 0) {
        throw new BufferMismatchError("Increased mana: Divisor must be a multiple of 2!");
    }
    buffer[0x9AE22] = divisor / 2;
}
function updateEXP() {
    function updateLine(num) {
        var expVal = guardedParseInt(document.getElementById("exp_lvl_" + num.toString()).value);
        var row = document.getElementById("exp" + num.toString());
        var multiplier = guardedParseInt(document.getElementById("exp_required_level_up_multiplier").value);
        row.innerText = (expVal * multiplier / 10).toString();
    }
    for (let i = 1; i <= 16; i++) {
        updateLine(i);
    }
}
function applyEXPThresholds() {
    var original_offsets_and_values = {
        0x69371: 0x00,
        0x69372: 0x01,
        0x69373: 0x02,
        0x69374: 0x03,
        0x69375: 0x04,
        0x69376: 0x06,
        0x69377: 0x08,
        0x69378: 0x0C,
        0x69379: 0x10,
        0x6937A: 0x18,
        0x6937B: 0x20,
        0x6937C: 0x30,
        0x6937D: 0x40,
        0x6937E: 0x60,
        0x6937F: 0x80,
        0x69380: 0xC0,
    };
    for (let i = 0x69371; i <= 0x69380; i++) {
        if (buffer[i] != original_offsets_and_values[i]) {
            throw new BufferMismatchError("EXP Patch: buffer mismatch");
        }
    }
    if (buffer[0x35199] != 0xF4 || buffer[0x3519A] != 0x01) {
        throw new BufferMismatchError("EXP Patch: buffer mismatch");
    }
    var multiplier = guardedParseInt(document.getElementById("exp_required_level_up_multiplier").value);
    if (multiplier <= 0) {
        throw new OptionsError("EXP Patch: multiplier must be greater than 0!");
    }
    let multiplier_low, multiplier_high;
    [multiplier_low, multiplier_high] = (separateShortIntoTwoBytes(multiplier));
    buffer[0x35199] = multiplier_low;
    buffer[0x3519A] = multiplier_high;
    var base = 0x69371;
    for (let i = 1; i <= 16; i++) {
        var ithExpVal = guardedParseInt(document.getElementById("exp_lvl_" + i.toString()).value);
        if (ithExpVal < 0) {
            throw new OptionsError("EXP Patch: level " + i.toString() + " must be greater than or equal to 0!");
        }
        buffer[base] = ithExpVal & 0xFF;
        base++;
    }
}
function applyIncreaseNumberOfSkillPointsEarned() {
    if (buffer[0x350BB] != 0xDC || buffer[0x350BC] != 0x05) {
        throw new BufferMismatchError("Increased skill points: buffer mismatch");
    }
    var ratio = guardedParseInt(document.getElementById("exp_to_skill_ratio").value);
    if (ratio <= 0) {
        throw new OptionsError("Increased skill points: ratio must be greater than 0");
    }
    buffer[0x350BB] = ratio & 0xFF;
    buffer[0x350BC] = (ratio >> 8) & 0xFF;
}
function applyIncreaseEXPPointGain() {
    if (buffer[0x3504A] != 0x02) {
        throw new BufferMismatchError("Increased EXP point gain: buffer mismatch");
    }
    buffer[0x3504A] = 0x01;
}
function applyPreventDeath() {
    if (buffer[0x27F46] != 0x9A || buffer[0x27F47] != 0x75 || buffer[0x27F48] != 0x00 || buffer[0x27F49] != 0x99 || buffer[0x27F4A] != 0x65) {
        throw new BufferMismatchError("Prevent death: buffer mismatch");
    }
    buffer[0x27F46] = 0x90;
    buffer[0x27F47] = 0x90;
    buffer[0x27F48] = 0x90;
    buffer[0x27F49] = 0x90;
    buffer[0x27F4A] = 0x90;
}
function applyHPRegen() {
    if (buffer[0x92C16] != 0xFF) {
        throw new BufferMismatchError("HP Regen: buffer mismatch");
    }
    var newRegen = guardedParseInt((document.getElementById("health_regen").value));
    if (newRegen < 0) {
        throw new Error("HP Regen: value must be greater than or equal to 0!");
    }
    buffer[0x92C16] = (newRegen * -1) & 0xFF;
}
function applyMPRegen() {
    if (buffer[0x92C2F] != 0xFF) {
        throw new BufferMismatchError("MP Regen: buffer mismatch");
    }
    var newRegen = guardedParseInt(document.getElementById("mana_regen").value);
    if (newRegen < 0) {
        throw new OptionsError("MP Regen: value must be greater than or equal to 0!");
    }
    buffer[0x92C2F] = (newRegen * -1) & 0xFF;
}
function applyLongerLastingLightSource() {
    if (buffer[0x92F74] != 0x8B || buffer[0x92F75] != 0x46 || buffer[0x92F76] != 0x06 || buffer[0x92BB3] != 0xE8 || buffer[0x92BB4] != 0x2D || buffer[0x92BB5] != 0x03) {
        throw new BufferMismatchError("Longer lasting light: buffer mismatch");
    }
    var doSpeed = document.getElementById("light_source_speed").checked;
    var doDisable = document.getElementById("light_source_disable").checked;
    if (doSpeed && doDisable) {
        throw new OptionsError("Light source speed and disable cannot both be enabled!");
    }
    if (doSpeed) {
        buffer[0x92F74] = 0xB4;
        buffer[0x92F75] = 0x01;
        buffer[0x92F76] = 0x90;
    }
    if (doDisable) {
        buffer[0x92BB3] = 0x90;
        buffer[0x92BB4] = 0x90;
        buffer[0x92BB5] = 0x90;
    }
}
function applyLongerLastingSpells() {
    if (buffer[0x92B82] != 0x4A || buffer[0x92B65] != 0xE8 || buffer[0x92B66] != 0x98 || buffer[0x92B67] != 0xFE) {
        throw new BufferMismatchError("Longer lasting spells: buffer mismatch");
    }
    var doSpeed = document.getElementById("spell_speed").checked;
    var doDisable = document.getElementById("spell_disable").checked;
    if (doSpeed && doDisable) {
        throw new OptionsError("Spell speed and disable cannot both be enabled!");
    }
    if (doSpeed) {
        buffer[0x92B82] = 0x90;
    }
    if (doDisable) {
        buffer[0x92B65] = 0x90;
        buffer[0x92B66] = 0x90;
        buffer[0x92B67] = 0x90;
    }
}
function log(message) {
    document.getElementById("log").innerText += message + "\n";
}
function guard(n) {
    if (isNaN(n)) {
        throw new OptionsError(`Value (${n}) must be a number!`);
    }
    return n;
}
function guardedParseInt(str, radix = 10) {
    return guard(parseInt(str, radix));
}
//# sourceMappingURL=patcher.js.map