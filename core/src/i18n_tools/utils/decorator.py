from __future__ import annotations

import functools
import inspect
import threading
from typing import Any, Callable, Literal, ParamSpec, TypeVar

from .logger import logger

P = ParamSpec("P")
R = TypeVar("R")

MethodKind = Literal["instance", "class", "any"]


class DecoratorFactoryHelper:
    # @start> static functions:
    @staticmethod
    def first_param_name(params) -> str | None:
        for p in params:
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
                return p.name
        return None

    @staticmethod
    def raise_static_error():
        raise TypeError("@decorator_factory(...): staticmethod is not allowed; set allow_static=True to permit.")

    @staticmethod
    def raise_instance_error():
        raise TypeError("@decorator_factory(...): expected an instance method with first parameter named 'self'.")

    @staticmethod
    def raise_class_error():
        raise TypeError(
            "@decorator_factory(...): expected a class method with first parameter named 'cls'. "
            "Tip: stack with @classmethod and keep this decorator closest to 'def', or in any order "
            "(this decorator supports both)."
        )

    @staticmethod
    def raise_any_error():
        raise TypeError(
            "@decorator_factory(...): expected a method with first parameter 'self' or 'cls'. "
            "If you intend a staticmethod, either mark it with @staticmethod and set allow_static=True, "
            "or set allow_static=True."
        )

    @staticmethod
    def get_descriptor_kind(func):
        if isinstance(func, classmethod):
            return "classmethod", func.__func__
        elif isinstance(func, staticmethod):
            return "staticmethod", func.__func__
        else:
            return "none", func

    @staticmethod
    def build_wrapper(target, is_async):
        if is_async:

            @functools.wraps(target)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                result = await target(*args, **kwargs)
                return result
        else:

            @functools.wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                result = target(*args, **kwargs)
                return result

        return wrapper

    @staticmethod
    def reapply_descriptor(descriptor_kind, wrapper):
        if descriptor_kind == "classmethod":
            return classmethod(wrapper)  # type: ignore[assignment]
        elif descriptor_kind == "staticmethod":
            return staticmethod(wrapper)  # type: ignore[assignment]
        else:
            return wrapper

    @classmethod
    def validate_first_param_name(
        cls,
        descriptor_kind: str | None,
        first_name: str | None,
        enforce: MethodKind,
        allow_static: bool,
    ):
        if descriptor_kind == "staticmethod" and not allow_static:
            cls.raise_static_error()
        if enforce == "instance" and first_name != "self":
            cls.raise_instance_error()
        if enforce == "class" and first_name != "cls":
            cls.raise_class_error()
        if enforce == "any" and first_name not in ("self", "cls"):
            if allow_static:
                logger.debug("Decorator factory: accepting callable without 'self'/'cls' under allow_static=True.")
            else:
                cls.raise_any_error()

    # @end> static functions.


def decorator_factory(
    *factory_args: Any,
    enforce: MethodKind = "any",
    allow_static: bool = False,
    **factory_kwargs: Any,
) -> Callable[[Callable[P, R] | classmethod | staticmethod], Callable[P, R] | classmethod | staticmethod]:
    """
    Decorator factory with optional method-only enforcement.

    Parameters
    ----------
    enforce : {"instance","class","any"}, default "any"
        - "instance": require first parameter to be named 'self'
        - "class":    require first parameter to be named 'cls'
        - "any":      require either 'self' or 'cls'; unless a staticmethod,
                      which is allowed only if allow_static=True
    allow_static : bool, default False
        Whether to accept @staticmethod (no 'self'/'cls').

    Notes
    -----
    - Works regardless of whether it's stacked above or below @classmethod/@staticmethod.
    - Preserves async-ness: async functions remain async after decoration.
    - Uses parameter name conventions ('self'/'cls') to determine method-ness,
        which is the practical approach at decoration time.
    """

    fn = DecoratorFactoryHelper  # alias for brevity.

    def fn_wrapper(func: Callable[P, R] | classmethod | staticmethod):
        descriptor_kind, target = fn.get_descriptor_kind(func)

        if not callable(target):
            raise TypeError(f"@decorator_factory(...): expected a callable, got {type(target)!r}")

        sig = inspect.signature(target)
        params = list(sig.parameters.values())
        is_async = inspect.iscoroutinefunction(target)
        first_name = fn.first_param_name(params)

        fn.validate_first_param_name(descriptor_kind, first_name, enforce, allow_static)

        logger.debug(
            "Decorator factory for %s%r with kwargs=%r (descriptor=%s, enforce=%s, allow_static=%s)",
            getattr(target, "__qualname__", getattr(target, "__name__", str(target))),
            factory_args,
            factory_kwargs,
            descriptor_kind,
            enforce,
            allow_static,
        )

        wrapper = fn.build_wrapper(target, is_async)
        wrapped = fn.reapply_descriptor(descriptor_kind, wrapper)
        # return the final wrapped function/method:
        return wrapped

    return fn_wrapper


def simple_singleton(cls):
    """
    Thread-safe singleton decorator. This is simplest form of singleton pattern, just to ensure
    only one instance of the class is created.

    !! ⚠️ Use with caution:
    ----
    - this decorator is not supported inheritance.
    - this is using per-class storage (closure).
    - for a complex singleton, consider using a metaclass or mixin approach.
    """
    instances = {}
    lock = threading.RLock()

    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
