"""Schema module."""

import importlib
from typing import Dict, Any, Type, Optional

from . import containers, providers


Schema = Dict[Any, Any]


class SchemaProcessorV1:

    def __init__(self, schema: Schema) -> None:
        self._schema = schema
        self._container = containers.DynamicContainer()

    def process(self):
        """Process schema."""
        self._create_providers(self._schema)
        self._setup_injections(self._schema)

    def get_providers(self):
        """Return providers."""
        return self._container.providers

    def _create_providers(self, schema: Schema, container: Optional[containers.Container] = None) -> None:
        if container is None:
            container = self._container
        for provider_name, data in schema['providers'].items():
            provider_type = _get_provider_cls(data['provider'])
            args = []

            provides = data.get('provides')
            if provides:
                provides = _import_string(provides)
                if provides:
                    args.append(provides)

            if provider_type is providers.Container:
                provides = containers.DynamicContainer
                args.append(provides)

            provider = provider_type(*args)
            container.set_provider(provider_name, provider)

            if isinstance(provider, providers.Container):
                self._create_providers(schema=data, container=provider)

    def _setup_injections(self, schema: Schema, container: Optional[containers.Container] = None) -> None:
        if container is None:
            container = self._container

        for provider_name, data in schema['providers'].items():
            provider = getattr(container, provider_name)
            args = []
            kwargs = {}

            arg_injections = data.get('args')
            if arg_injections:
                for arg in arg_injections:
                    injection = None

                    if isinstance(arg, str):
                        injection = self._resolve_provider(arg)

                    # TODO: add inline injections

                    if not injection:
                        injection = arg

                    args.append(injection)
            if args:
                provider.add_args(*args)

            kwarg_injections = data.get('kwargs')
            if kwarg_injections:
                for name, arg in kwarg_injections.items():
                    injection = None

                    if isinstance(arg, str):
                        injection = self._resolve_provider(arg)

                    # TODO: refactoring
                    if isinstance(arg, dict):
                        provider_args = []
                        provider_type = _get_provider_cls(arg.get('provider'))
                        provides = arg.get('provides')
                        if provides:
                            provides = _import_string(provides)
                            if provides:
                                provider_args.append(provides)
                        for provider_arg in arg.get('args', []):
                            provider_args.append(self._resolve_provider(provider_arg))
                        injection = provider_type(*provider_args)

                    if not injection:
                        injection = arg

                    kwargs[name] = injection
            if kwargs:
                provider.add_kwargs(**kwargs)

            if isinstance(provider, providers.Container):
                self._setup_injections(schema=data, container=provider)

    def _resolve_provider(self, name: str) -> Optional[providers.Provider]:
        segments = name.split('.')
        try:
            provider = getattr(self._container, segments[0])
        except AttributeError:
            return None

        for segment in segments[1:]:
            if segment == 'as_int()':
                provider = provider.as_int()
            elif segment == 'as_float()':
                provider = provider.as_float()
            elif segment.startswith('is_'):  # TODO
                provider = provider.as_(str)
                ...
            else:
                try:
                    provider = getattr(provider, segment)
                except AttributeError:
                    return None
        return provider


def build_schema(schema: Schema) -> Dict[str, providers.Provider]:
    """Build provider schema."""
    schema_processor = SchemaProcessorV1(schema)
    schema_processor.process()
    return schema_processor.get_providers()


def _get_provider_cls(provider_cls_name: str) -> Type[providers.Provider]:
    std_provider_type = _fetch_provider_cls_from_std(provider_cls_name)
    if std_provider_type:
        return std_provider_type

    custom_provider_type = _import_provider_cls(provider_cls_name)
    if custom_provider_type:
        return custom_provider_type

    raise SchemaError(f'Undefined provider class "{provider_cls_name}"')


def _fetch_provider_cls_from_std(provider_cls_name: str) -> Optional[Type[providers.Provider]]:
    return getattr(providers, provider_cls_name, None)


def _import_provider_cls(provider_cls_name: str) -> Optional[Type[providers.Provider]]:
    try:
        cls = _import_string(provider_cls_name)
    except (ImportError, ValueError) as exception:
        raise SchemaError(f'Can not import provider "{provider_cls_name}"') from exception
    except AttributeError:
        return None
    else:
        if isinstance(cls, type) and not issubclass(cls, providers.Provider):
            raise SchemaError(f'Provider class "{cls}" is not a subclass of providers base class')
        return cls


def _import_string(string_name: str) -> Optional[object]:
    segments = string_name.split('.')

    if len(segments) == 1:
        member = __builtins__.get(segments[0])
        if member:
            return member

    module_name = '.'.join(segments[:-1])
    if not module_name:
        return None

    member = segments[-1]
    module = importlib.import_module(module_name)
    return getattr(module, member, None)


class SchemaError(Exception):
    """Schema-related error."""
