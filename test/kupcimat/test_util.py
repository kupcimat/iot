import functools

from kupcimat.util import unwrap_partial


def test_unwrap_partial():
    def func(x, y, z):
        pass

    partial1_func = functools.partial(func, 1)
    partial2_func = functools.partial(partial1_func, 2)
    partial3_func = functools.partial(partial2_func, 3)

    assert unwrap_partial(func) == func
    assert unwrap_partial(partial1_func) == func
    assert unwrap_partial(partial2_func) == func
    assert unwrap_partial(partial3_func) == func
