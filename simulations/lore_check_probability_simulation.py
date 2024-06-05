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

def lore_check(player_skill, magic_number_difficulty = 8):
    return skill_check(player_skill, magic_number_difficulty)

def simulations():
    lores = list(range(1, 31))
    tries = 1000000
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
    plt.plot(x, y1, label='Fully identified', marker='o', lw=0)
    plt.plot(x, y2, label='Partially identified', marker='o', lw=0)
    plt.plot(x, y3, label='Unidentified', marker='o', lw=0)
    # plt.xticks(range(0, 31, 1), range(0, 31, 5))
    plt.xlabel('Player lore skill')
    plt.ylabel('Percentage')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig('vanilla_lore_probability.png', dpi=300)

if __name__ == '__main__':
    plot_simulation(*simulations())

def simulations2():
    magic_numbers = list(range(0, 15))
    collection = []
    for magic_number in magic_numbers:
        lores = list(range(1, 31))
        tries = 10000
        counts = []
        ratios = []
        for lore in lores:
            results = []
            for i in range(tries):
                results.append(lore_check(lore, magic_number))
            c = Counter(results)
            counts.append(c)
            r = {}
            r['critical_failure'] = c.get(-1, 0) / tries
            r['failure'] = c.get(0, 0) / tries
            r['corrected_failure'] = (c.get(-1, 0) + c.get(0, 0)) / tries
            r['success'] = c.get(1, 0) / tries
            r['critical_success'] = c.get(2, 0) / tries
            ratios.append(r)
        with open(f'lore_simulation_magic{magic_number}.txt', 'w') as fhand:
            for lore, count, ratio in zip(lores, counts, ratios):
                fhand.write(str(lore) + ' ' + str(count) + ' ' + str(ratio) + '\n')

        collection.append((magic_number, lores, counts, ratios))

    return collection

def plot_simulation2(magic_number, skills, counts, ratios):
    x = skills
    y1 = [i['critical_success']*100 for i in ratios]
    y2 = [i['success']*100 for i in ratios]
    y3 = [i['corrected_failure']*100 for i in ratios]
    plt.figure()
    plt.title(magic_number)
    plt.plot(x, y1, label='Fully identified')
    plt.plot(x, y2, label='Partially identified')
    plt.plot(x, y3, label='Unidentified')
    plt.xlabel('Player lore skill')
    plt.ylabel('Percentage')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'lore_probability_magic{magic_number}.png', dpi=300)

# if __name__ == '__main__':
#     plot_simulation(*simulations())
if __name__ == '__main__':
    c = simulations2()
    for magic_number, skills, counts, ratios in c:
        plot_simulation2(magic_number, skills, counts, ratios)





