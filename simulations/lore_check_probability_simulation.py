import random
from collections import Counter
import matplotlib.pyplot as plt

def skill_check(player_skill, magic_number_difficulty):
    die_roll = random.randint(0, 0x7FFF) % 0x1F # iVar1 % 0x1F
    check = (player_skill - magic_number_difficulty) + die_roll
    if check < 0x1d: # 29
        if check < 0x10: # 16
            if check < 3:
                result = -1 # 0xFFFF
            else:
                result = 0
        else:
            result = 1
    else:
        result = 2
    return result

def lore_check(player_skill):
    return skill_check(player_skill, 8)

def simulations():
    lores = list(range(1, 31))
    tries = 10000
    counts = []
    ratios = []
    for lore in lores:
        results = []
        for i in range(tries):
            results.append(lore_check(lore))
        c = Counter(results)
        counts.append(c)
        r = {}
        r['critical_failure'] = c.get(-1, 0) / tries
        r['failure'] = c.get(0, 0) / tries
        r['corrected_failure'] = (c.get(-1, 0) + c.get(0, 0)) / tries
        r['success'] = c.get(1, 0) / tries
        r['critical_success'] = c.get(2, 0) / tries
        ratios.append(r)
    with open('lore_simulation.txt', 'w') as fhand:
        for lore, count, ratio in zip(lores, counts, ratios):
            print(lore, count, ratio)
            fhand.write(str(lore) + ' ' + str(count) + ' ' + str(ratio) + '\n')

    return lores, counts, ratios

def plot_simulation(skills, counts, ratios):
    x = skills
    y1 = [i['critical_success']*100 for i in ratios]
    y2 = [i['success']*100 for i in ratios]
    y3 = [i['corrected_failure']*100 for i in ratios]
    plt.plot(x, y1, label='Fully identified')
    plt.plot(x, y2, label='Partially identified')
    plt.plot(x, y3, label='Unidentified')
    plt.xlabel('Player lore skill')
    plt.ylabel('Percentage')
    plt.legend()
    plt.tight_layout()
    plt.savefig('vanilla_lore_probability.png', dpi=300)

if __name__ == '__main__':
    plot_simulation(*simulations())




