# discounts/__init__.py
import importlib
import pkgutil
from types import SimpleNamespace

REGISTRY = {}

def register(ns_or_module):
    """
    Accept either a module object or a globals() dict from a module.
    """
    if isinstance(ns_or_module, dict):
        ns = ns_or_module
        verb = ns.get("VERB")
        if not verb:
            raise ValueError("Discount module missing VERB.")
        REGISTRY[verb] = SimpleNamespace(**ns)
    else:
        module = ns_or_module
        verb = getattr(module, "VERB", None)
        if not verb:
            raise ValueError(f"Discount module {getattr(module, '__name__', '<unknown>')} missing VERB.")
        REGISTRY[verb] = module

def load_all():
    pkg = __name__  # 'discounts'
    for _, modname, ispkg in pkgutil.iter_modules(__path__):
        if ispkg:
            continue
        importlib.import_module(f"{pkg}.{modname}")
