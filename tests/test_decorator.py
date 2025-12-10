from ..type_checking.decorator import TypeCheckDecorator, type_check, _apply_annotation_type_checks

def test_type_check_decorator():
    @type_check # type: ignore
    def func1(a: int, b: str) -> None:
        return

    func1(10, "hello")

    try:
        func1("not an int", "hello") # type: ignore istg pylance I'm trying to get an error
    except TypeError as e:
        assert str(e) == "Invalid type for argument 'a': expected int, got str"

    @type_check(a=int, b=str)
    def func2(a, b):
        return

    func2(20, "world")

    try:
        func2(20, 30)
    except TypeError as e:
        assert str(e) == "Invalid type for argument 'b': expected str, got int"

    @type_check(on_failure=lambda errors: print(f"Validation failed: {errors}"), a=int)
    def func3(a):
        return

    func3(100)

    try:
        func3("oops")
    except TypeError:
        pass  # on_failure handler should print the error message

