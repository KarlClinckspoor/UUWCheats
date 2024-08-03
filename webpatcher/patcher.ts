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