from resultpy import Result


def f(x: int) -> Result[int, str]:
    return Result.ok(x * 2)


def g(x: int) -> Result[int, str]:
    return Result.ok(x + 10)


class TestMonadLaws:
    """
    For a proper implementation of a Monad, we need to ensure that it satisfies the following laws:
        1. Left identity: return a >>= f  ≡  f a
        2. Right identity: m >>= return  ≡  m
        3. Associativity: (m >>= f) >>= g  ≡  m >>= (λx. f x >>= g)
    In Result terms:
        - result = Result.ok
        - >>= = and_then

    """

    # class TestLeftIdentity:
    #     def test_it_holds_for_ok(self):
    #         a = 5
    #         left = Result.ok(a).and_then(f)
    #         right = f(a)
    #         assert left.unwrap()
