"""Execute unchanged vendor sources with package-private standalone aliases.

Upstream's script loaders use bare ``sue_challenge``/``sue_runner`` names.
Only the executed vendor modules receive private views of sys/importlib through
their own builtins dictionary. Python's global importer, importlib functions
and existing bare sys.modules entries are never replaced, even temporarily.
"""

import builtins
from collections.abc import MutableMapping
from importlib import util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType


_PREFIX = __package__ + "._vendor.sue."
_ALIASES = {name: _PREFIX + name for name in ("sue_challenge", "sue_runner", "sue_lenses")}


class _ModuleAliases(MutableMapping):
    def __getitem__(self, name):
        return sys.modules[_ALIASES.get(name, name)]

    def __setitem__(self, name, value):
        sys.modules[_ALIASES.get(name, name)] = value

    def __delitem__(self, name):
        del sys.modules[_ALIASES.get(name, name)]

    def __iter__(self):
        names = set(sys.modules).difference(_ALIASES)
        for alias, private in _ALIASES.items():
            if private in names:
                names.remove(private)
                names.add(alias)
        return iter(names)

    def __len__(self):
        return sum(1 for _ in self)


class _ModuleView(ModuleType):
    def __init__(self, original, **overrides):
        super().__init__(original.__name__)
        self._original = original
        self.__dict__.update(overrides)

    def __getattr__(self, name):
        return getattr(self._original, name)


class _CanonicalLoader(SourceFileLoader):
    def exec_module(self, module):
        previous = sys.modules.get(module.__name__)
        sys.modules[module.__name__] = module
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=_private_import)
        try:
            super().exec_module(module)
        except BaseException:
            if previous is None:
                sys.modules.pop(module.__name__, None)
            else:
                sys.modules[module.__name__] = previous
            raise
        parent, _, child = module.__name__.rpartition(".")
        if parent in sys.modules:
            setattr(sys.modules[parent], child, module)


def _private_spec(name, location, *args, **kwargs):
    if name in _ALIASES:
        name = _ALIASES[name]
        kwargs["loader"] = _CanonicalLoader(name, str(location))
    return util.spec_from_file_location(name, location, *args, **kwargs)


_SYS = _ModuleView(sys, modules=_ModuleAliases())
_UTIL = _ModuleView(util, spec_from_file_location=_private_spec)
_IMPORTLIB = _ModuleView(sys.modules["importlib"], util=_UTIL)


def _private_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level == 0:
        if name == "sys":
            return _SYS
        if name == "importlib.util":
            return _UTIL if fromlist else _IMPORTLIB
    return builtins.__import__(name, globals, locals, fromlist, level)


def load_vendor():
    """Initialize canonical dialectic code under its qualified package name."""
    from ._vendor import sue

    name = _PREFIX + "sue_dialectic"
    if name in sys.modules:
        return
    path = Path(sue.__file__).parent / "sue_dialectic.py"
    spec = util.spec_from_file_location(name, path, loader=_CanonicalLoader(name, str(path)))
    spec.loader.exec_module(util.module_from_spec(spec))
