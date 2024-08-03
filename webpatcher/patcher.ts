var buffer: Uint8Array;

function loadExecutable() {
    // Query for file
    // Load it into memory
    // Compute hash
    // Compare with required hash
    var uw2_gog_hash = "BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9";
    buffer = new Uint8Array(675184);
}

function applyPatches() {
    // Query all checkboxes
    var inputs = document.getElementsByClassName("options");
    var selectedInputs: Array<HTMLInputElement> = Array.prototype.filter.call(inputs, (input: Element) => (<HTMLInputElement>input).checked);
    var functionMaps = {
        "increase_carry_weight": applyCarryWeightPatch,
        "allow_sequential_lore_checks": applySequentialLoreChecks,
        default: () => { console.log("Unknown patch. BUG! REPORT!"); return; }
    }
    for (var input of selectedInputs) {
        functionMaps[input.id](buffer);
    }
}

function applySequentialLoreChecks() {
    if (buffer === undefined) { throw new Error("buffer wasn't loaded!"); }
    if (buffer[0x28DA0] != 0x04) {
        throw new Error("Unexpected value at 'applySequentialLoreChecks'!")
    }
    buffer[0x28DA0] = 0x00;
}

function applyCarryWeightPatch() {
    // apply checks
    var ele = <HTMLInputElement>document.getElementById("carry_weight_multiplier")!;
    var value = parseFloat(ele.value);
}