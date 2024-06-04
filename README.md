## Introduction

### Objective

Create a series of small patches to the original games where some mechanics are adjusted or circumvented. This won't create large patches, like those found in [UltimaHacks](https://github.com/JohnGlassmyer/UltimaHacks), only minor things.

This repo is temporary, just to store some thoughts and "publish" what I've been doing. Maybe I'll convert these into their own patcher, make HackProtos to use with UltimaHacks, or just keep them as-is.

### Origins

Once I saw a conversation on reddit about how Lore worked, and how it's a kinda annoying mechanic. You can only try to identify an item once per skill level, the item won't self-identify if you use it, paying for services can be quite expensive.

Some time later, when viewing another player going through UUW, I remembered that conversation and [hankmorgan's Reverse Engineering project](https://github.com/hankmorgan/UWReverseEngineering). I picked that up and probed around the notes, together with his implementation in the [UnderworldGodot](https://github.com/hankmorgan/UnderworldGodot) (and archived [UnderworldUnity](https://github.com/hankmorgan/UnderworldExporter)), and I was able to make a few minor mods. I wanted to share them, so here we are

## Applying the patches

Right now, you'll have to download a hex editor and edit the executables yourself. I use [HxD](https://mh-nexus.de/en/hxd/). I'll provide an offset (position) in the file and the values that need to be changed.

## Workflow

To make these patches, I load up the disassembly file from the Reverse Engineering project in IDA Pro 5. Then, I search for text occurrences of whatever I want to study. For example, I looked around for "Lore", among the results, you can find this:

![lore1.PNG](lore1.PNG)

This looks very promising. First, there's some mention of the player's lore skill, then there's a call to a function named "SkillCheck...". So if I can modify the file around this region, I'll get the result I want.

However, this is easier said than done, especially when looking at assembly. I load up the executable on [Ghidra](https://ghidra-sre.org/). To sync Ghidra and IDA, I do something a bit dumb (I'm looking into transferring the labels from one program to another). In IDA, I change to Hex view around a instruction, copy the whole line, then on Ghidra I search though Memory, and paste the line I copied earlier. Sometimes the result is garbled, so I click on the listing and use the disassemble command (D) to convert it to something useful. I then compare the listing from IDA and Ghidra, to confirm they're equal, and look at the reconstructed C code Ghidra provides.

Here's an example. I focused on the "test DI,0x4" line, which has a useful magic constant, copied the line highlighted in yellow on the left (this or the next line are fine), and the corresponding location in Ghidra on the right, with the "test DI,0x4" and the "if ((uVar4 & 4) == 0)" corresponding C code. This looks promising.

![lore2.PNG](lore2.PNG)

Looking up the listing in UnderworldGodot, the [correspondence is quite close](https://github.com/hankmorgan/UnderworldGodot/blob/e20d3d3590bef80021414db895514b71259330a7/src/interaction/look.cs#L10):

```C#
public static int LoreCheck(uwObject obj)
{
    if (
        CanBeIdentified(obj)
        )
    {//can be identified
        if ((obj.heading & 0x4) == 0)
        {//no attempt has been made yet. try and id now
            var result = (int)playerdat.SkillCheck(playerdat.Lore, 8);
            result++;
            if (result == 0)
            {
                result = 1;
            }
            if (result < (obj.heading & 0x3))
            {
                result = obj.heading & 0x3;//make sure identification does not lose a previous ID attempt if bit 3 has changed due to a lore skill increase
            }
            obj.heading = (short)(4 | result); //store result and flag that attempt was made.
            return result; //1,2 or 3
        }
        else
        {
            return obj.heading & 0x3; //return previous result
        }
    }
    return 1;//fail or cannot be identified
}
```

If I want the lore test to be repeatable, I can modify the test. Since it checks if the third bit is set (`0x100` is `4` decimal), I can just change `4` to be `0`, meaning this test is skipped, since anything ANDed with 0 is 0. With Ghidra, I can use the "Patch Instruction" function to modify the file, then use "File-Export Program" in the "Original File" format with a good name. This is convenient. To get the linear offset, I go back to IDA, because it provides the offset at the bottom of the hex view window (since I haven't yet figured out the weird offset addressing Ghidra provides).

The result of this is just a set of offsets and bytes that you have to change.

## Cheats themselves

These are provided with minimal testing 

### UUW2 original 

- SHA-256 checksum: BF233ABBFEB5B664564B954FC70C615C4023AD2276DD3326FCD34700C10AFDB9

#### Allow sequential Lore checks on the same item (mildly tested)

| offset | Original | New value |
|--------|----------|-----------|
| 28DA0  | 04       | 00        |

#### Every skill check is a critical success (untested!)

| offset | Original | New value |
|--------|---------|-----------|
| 35022  | 01      | 02        |
| 3502B  | 33      | 66        |
| 3502C  | C0      | 90        |
| 35030  | FF      | 02        |
| 35031  | FF      | 00        |

## TODOs

* Check how easy it is to transfer the cheats from the Underworlds, and the UltimaHacks versions.

## Ideas

* Change skillpoint gain per level
* Adjust difficulty of skill checks
* Adjust health and mana regen
* Adjust hunger gain/loss