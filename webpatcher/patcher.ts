var buffer: Uint8Array;

async function loadExecutable() {
    var uw2_gog_hash = "BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9";
    // buffer = new Uint8Array(675184);
    const fileInput = <HTMLInputElement>document.getElementById("path_to_executable")!;
    const filePath = fileInput.files[0];
    if (filePath) {
        buffer = new Uint8Array(await (<Blob> filePath).arrayBuffer());
        if (buffer) {
            var hash = await getHash();
            document.getElementById("executable_hash").innerText = hash;
            document.getElementById("hash_ok").innerText = hash === uw2_gog_hash ? "MATCHES" : "NO MATCH";
        };

    }
}

async function getHash() {
    const hashBuffer = await window.crypto.subtle.digest("SHA-256", buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    return hashHex.toUpperCase();
}

function separateShortIntoTwoBytes(int: number) {
    return [int & 0xFF, (int >> 8) & 0xFF];
}

function applyPatches() {
    if (buffer === undefined) { throw new Error("buffer wasn't loaded!"); }
    var inputs = document.getElementsByClassName("options");
    var selectedInputs: Array<HTMLInputElement> = Array.prototype.filter.call(inputs, (input: Element) => (<HTMLInputElement>input).checked);
    var functionMaps = {
        "increase_carry_weight": applyCarryWeightPatch,
        "critical_skill_checks": applyCriticalSkillChecks,
        "allow_sequential_lore_checks": applySequentialLoreChecks,
        default: () => { console.log("Unknown patch. BUG! REPORT!"); return; }
    }
    for (var input of selectedInputs) {
        functionMaps[input.id](buffer);
    }
}

function applySequentialLoreChecks() {
    if (buffer[0x28DA0] != 0x04) {
        throw new Error("Unexpected value at 'applySequentialLoreChecks'!")
    }
    buffer[0x28DA0] = 0x00;
}

function applyCriticalSkillChecks() {
    if (buffer[0x35022] != 0x01 || buffer[0x3502B] != 0x33 || buffer[0x3502C] != 0xC0 || buffer[0x35030] != 0xFF || buffer[0x35031] != 0xFF) {
        throw new Error("Unexpected value at 'applySequentialLoreChecks'!")
    };
    buffer[0x35022] = 0x02;
    buffer[0x3502B] = 0x66;
    buffer[0x3502C] = 0x90;
    buffer[0x35030] = 0x02;
    buffer[0x35031] = 0x00;
}

function applyCarryWeightPatch() {
    if (buffer[0x9AE3A] != 0x0D || buffer[0x9AE3B] != 0x00 || buffer[0x9AE3F] != 0x2C || buffer[0x9AE40] != 0x01) {
        throw new Error("Original buffer doesn't match expected value at 'applyCarryWeightPatch'!");
    }
    var multiplier = parseInt((<HTMLInputElement>document.getElementById("carry_weight_multiplier")!).value);
    var offset = parseInt((<HTMLInputElement>document.getElementById("carry_weight_offset")!).value);
    let multiplier_low: number, multiplier_high: number, offset_low: number, offset_high: number;
    [multiplier_low, multiplier_high] = separateShortIntoTwoBytes(multiplier);
    [offset_low, offset_high] = separateShortIntoTwoBytes(offset);
    buffer[0x9AE3A] = multiplier_low;
    buffer[0x9AE3B] = multiplier_high;
    buffer[0x9AE3F] = offset_low;
    buffer[0x9AE40] = offset_high;
}