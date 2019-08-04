import pytest
from decaptcha.base import GroundState


@pytest.fixture()
def DispersiveGround():
    class DispersiveGround(GroundState):
        def run(self):
            pass

        def next(self):
            pass

    return DispersiveGround


@pytest.fixture()
def bot(DispersiveGround):
    return DispersiveGround()


def test_edge_collision(bot):
    assert bot.iscollision(tuple([1, 3]), tuple([2, 4]))
    assert bot.iscollision(tuple([1, 3]), tuple([3, 5]))
    assert bot.iscollision(tuple([2, 4]), tuple([1, 3]))
    assert bot.iscollision(tuple([3, 5]), tuple([1, 3]))
    assert not bot.iscollision(tuple([1, 3]), tuple([4, 6]))
    assert not bot.iscollision(tuple([4, 6]), tuple([1, 3]))
