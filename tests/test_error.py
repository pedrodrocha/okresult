from resultpy import TaggedError
from typing import TypeAlias, Union


class NotFoundError(TaggedError):
    __slots__ = ("id",)

    @property
    def tag(self) -> str:
        return "NotFoundError"

    def __init__(self, id: str) -> None:
        self.id = id
        super().__init__(f"Not found: {id}")


class ValidationError(TaggedError):
    __slots__ = ("field",)

    @property
    def tag(self) -> str:
        return "ValidationError"

    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"Invalid field: {field}")


class NetworkError(TaggedError):
    __slots__ = ("url",)

    @property
    def tag(self) -> str:
        return "NetworkError"

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"Network error: {url}")


AppError: TypeAlias = Union[NotFoundError, ValidationError, NetworkError]


def handle_not_found(e: NotFoundError) -> str:
    return f"Not found: {e.id}"


def handle_validation(e: ValidationError) -> str:
    return f"Invalid field: {e.field}"


def handle_network(e: NetworkError) -> str:
    return f"Network error: {e.url}"


def match_app_error(error: AppError) -> str:
    return TaggedError.match(
        error,
        {
            NotFoundError: handle_not_found,
            ValidationError: handle_validation,
            NetworkError: handle_network,
        },
    )


class TestTaggedError:
    class TestConstruction:
        def test_has_tag_descriminator(self) -> None:
            error = NotFoundError("123")
            assert error.tag == "NotFoundError"

            error = ValidationError("name")
            assert error.tag == "ValidationError"

            error = NetworkError("https://example.com")
            assert error.tag == "NetworkError"

        def test_sets_message(self) -> None:
            error = NotFoundError("123")
            assert error.message == "Not found: 123"

            error = ValidationError("name")
            assert error.message == "Invalid field: name"

            error = NetworkError("https://example.com")
            assert error.message == "Network error: https://example.com"

        def test_preserves_custom_properties(self) -> None:
            error = NotFoundError("123")
            assert error.id == "123"

            error = ValidationError("name")
            assert error.field == "name"

            error = NetworkError("https://example.com")
            assert error.url == "https://example.com"

        def test_chains_cause_via_dunder_cause(self) -> None:
            cause = ValueError("root cause")

            class ErrorWithCause(TaggedError):
                __slots__ = ()

                @property
                def tag(self) -> str:
                    return "ErrorWithCause"

                def __init__(self) -> None:
                    super().__init__("wrapper", cause)

            error = ErrorWithCause()
            assert error.__cause__ is cause
            assert str(error.__cause__) == "root cause"
            assert error.message == "wrapper"

    class TestIsError:
        def test_returns_true_for_exceptions(self) -> None:
            assert TaggedError.is_error(ValueError("test"))

        def test_returns_true_for_tagged_errors(self) -> None:
            assert TaggedError.is_error(NotFoundError("123"))
            assert TaggedError.is_error(ValidationError("name"))
            assert TaggedError.is_error(NetworkError("https://example.com"))

        def test_returns_false_for_non_exceptions(self) -> None:
            assert not TaggedError.is_error(123)
            assert not TaggedError.is_error("test")

    class TestIsTaggedError:
        def test_returns_true_for_tagged_errors(self) -> None:
            assert TaggedError.is_tagged_error(NotFoundError("123"))
            assert TaggedError.is_tagged_error(ValidationError("name"))
            assert TaggedError.is_tagged_error(NetworkError("https://example.com"))

        def test_returns_false_for_plain_exceptions(self) -> None:
            assert not TaggedError.is_tagged_error(ValueError("test"))

        def test_returns_false_for_non_exceptions(self) -> None:
            assert not TaggedError.is_tagged_error(123)
            assert not TaggedError.is_tagged_error("test")

    class TestMatch:
        pass
