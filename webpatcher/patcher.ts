let buffer: Uint8Array;

function loadExecutable() {
    // Query for file
    // Load it into memory
    // Compute hash
    // Compare with required hash
    var uw2_gog_hash = "BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9";
    buffer = new Uint8Array(20);
}

function applyPatches() {
    // Query all checkboxes
    // For each checkbox that's checked
    // Apply that specific function, which might query for other info
}

function applySequentialLoreChecks(buffer: Uint8Array) {
    if (buffer[0x28DA0] != 0x04) {
        throw new Error("Unexpected value at 'applySequentialLoreChecks'!")
    }
    buffer[0x28DA0] = 0x00;
}

function applyCarryWeightPatch(buffer: Uint8Array) {
    // apply checks
    var ele = <HTMLInputElement>document.getElementById("carry_weight_multiplier")!;
    var value = parseFloat(ele.value);
}