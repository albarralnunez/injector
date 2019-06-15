from contextvars import ContextVar
from typing import Any, Dict, Optional

from injector import InstanceProvider, Provider, Scope, ScopeDecorator


class AioTaskScope(Scope):
    cache: Optional[Dict[str, ContextVar[InstanceProvider]]] = None

    def cleanup(self) -> None:
        self.cache: Dict[str, ContextVar[InstanceProvider]] = {}

    def configure(self) -> None:
        self.cache: Dict[str, ContextVar[InstanceProvider]] = {}

    def _get_or_set_context_var(self, key: str) -> ContextVar:
        try:
            context_var = self.cache[key]
        except LookupError:
            context_var = self.cache[key] = ContextVar(key)
        return context_var

    def _get_or_set_provider(self, context_var, provider) -> InstanceProvider:
        try:
            value = context_var.get()
        except LookupError:
            value = InstanceProvider(provider.get(self.injector))
            context_var.set(value)
        return value

    def get(self, key: Any, provider: Provider) -> InstanceProvider:
        id_key = repr(key)
        context_var = self._get_or_set_context_var(id_key)
        value = self._get_or_set_provider(context_var, provider)
        return value


aio_task = ScopeDecorator(AioTaskScope)
