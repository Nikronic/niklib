__all__ = [
    'add_percentage_axes',
]

# core
import matplotlib.pyplot as plt


def add_percentage_axes(ax: plt.Axes, n: int) -> None:
    """Add percentage on top of bar (matplotlib and seaborn) plots

    args:
        ax (plt.Axes): the axes to apply this function
        n (int): total number of items for computing percentage

    Note:
        it can be used on ``seaborn.countplot`` too

    Reference:

        * https://stackoverflow.com/a/63479557/18971263

    """

    for p in ax.patches:
        percentage = '{:1.1f}%'.format(100 * p.get_height()/float(n))
        x = p.get_x() + p.get_width() / 2
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y), ha='center', color='black')
