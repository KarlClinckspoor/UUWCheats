import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def create_matrix_skillcheck_probabilities(difficulty: int) -> np.ndarray:
    """
    Returns a skill_values (30) x outcomes (4) array with the probabilities of skill checks.
    Layer 0 contains critical success, layer 1 success, layer 2 failure, and layer 3 critical failure.
    :param difficulty: Value that's subtracted from the player skill for the skill check
    :return: np.ndarray
    """
    roll_values = np.arange(0, 31) # 0 - 0x1F
    skill_values = np.arange(1, 31) # 1 - 30 in-game
    # Create grid of values
    matrix_roll_values, matrix_skill_values = np.meshgrid(roll_values, skill_values)
    matrix = matrix_roll_values - difficulty + matrix_skill_values
    critical_successes = (matrix > 29).sum(axis=1) / len(roll_values) * 100
    successes = ((matrix > 16) & (matrix <= 29)).sum(axis=1) / len(roll_values) * 100
    failures = ((matrix > 3) & (matrix <= 16)).sum(axis=1) / len(roll_values) * 100
    critical_failures = (matrix <= 3).sum(axis=1) / len(roll_values) * 100

    stack = np.vstack((critical_successes, successes, failures, critical_failures)).T
    assert np.allclose(stack.sum(axis=1), 100) # Probabilities should add up to 100

    return stack

def create_lore_success_probabilities():
    m = create_matrix_skillcheck_probabilities(difficulty=8)
    df = pd.DataFrame({
        'lore_skill': np.arange(1, 31),
        'critical_success': m[:, 0],
        'success': m[:, 1],
        'failure': m[:, 2] + m[:, 3],
    })
    return df

def plot_and_export_lore():
    df = create_lore_success_probabilities()
    df.to_excel('vanilla_lore_probabilities.xlsx', index=False)
    df.to_csv('vanilla_lore_probabilities.csv', index=False)
    fig, ax = plt.subplots()
    ax.plot(df['lore_skill'], df['critical_success'], label='Fully identified', marker='o', lw=0)
    ax.plot(df['lore_skill'], df['success'], label='Partially identified', marker='o', lw=0)
    ax.plot(df['lore_skill'], df['failure'], label='Unidentified', marker='o', lw=0)
    ax.set_xlabel('Player lore skill')
    ax.set_ylabel('Percentage')
    ax.legend()
    ax.grid()
    fig.savefig('vanilla_lore_probabilities.png')

if __name__ == '__main__':
    plot_and_export_lore()