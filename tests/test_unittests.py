import pytest
from decaptcha.notarobot import DispersiveGround


@pytest.fixture()
def bot():
    return DispersiveGround()


def test_edge_collision(bot):
    assert bot.iscollision(tuple([1, 3]), tuple([2, 4]))
    assert bot.iscollision(tuple([1, 3]), tuple([3, 5]))
    assert bot.iscollision(tuple([2, 4]), tuple([1, 3]))
    assert bot.iscollision(tuple([3, 5]), tuple([1, 3]))
    assert not bot.iscollision(tuple([1, 3]), tuple([4, 6]))
    assert not bot.iscollision(tuple([4, 6]), tuple([1, 3]))


def test_nxm(bot):
    assert bot.nxm(4, 4, 0) == (0, 0)
    assert bot.nxm(4, 4, 4) == (1, 0)
    assert bot.nxm(4, 4, 9) == (2, 1)
    assert bot.nxm(3, 3, 0) == (0, 0)
    assert bot.nxm(3, 3, 3) == (1, 0)
    assert bot.nxm(3, 3, 8) == (2, 2)


def test_grid_margins(bot):
    assert bot.grid_margins(4, 4) == (6, 6)
    assert bot.grid_margins(3, 3) == (5, 5)


def test_cell_dimensions(bot):
    assert bot.cell_dimensions(400, 400, 6, 6, 4, 4) == (97, 97)
    assert bot.cell_dimensions(400, 400, 5, 5, 3, 3) == (130, 130)
