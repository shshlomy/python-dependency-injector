import asyncio
import random
import unittest

from dependency_injector import containers, providers, errors

# Runtime import to get asyncutils module
import os
_TOP_DIR = os.path.abspath(
    os.path.sep.join((
        os.path.dirname(__file__),
        '../',
    )),
)
import sys
sys.path.append(_TOP_DIR)

from asyncutils import AsyncTestCase


RESOURCE1 = object()
RESOURCE2 = object()


async def init_resource(resource):
    await asyncio.sleep(random.randint(1, 10) / 1000)
    yield resource
    await asyncio.sleep(random.randint(1, 10) / 1000)


class Client:
    def __init__(self, resource1: object, resource2: object) -> None:
        self.resource1 = resource1
        self.resource2 = resource2


class Service:
    def __init__(self, client: Client) -> None:
        self.client = client


class Container(containers.DeclarativeContainer):
    resource1 = providers.Resource(init_resource, providers.Object(RESOURCE1))
    resource2 = providers.Resource(init_resource, providers.Object(RESOURCE2))

    client = providers.Factory(
        Client,
        resource1=resource1,
        resource2=resource2,
    )

    service = providers.Factory(
        Service,
        client=client,
    )


class FactoryTests(AsyncTestCase):

    def test_args_injection(self):
        class ContainerWithArgs(containers.DeclarativeContainer):
            resource1 = providers.Resource(init_resource, providers.Object(RESOURCE1))
            resource2 = providers.Resource(init_resource, providers.Object(RESOURCE2))

            client = providers.Factory(
                Client,
                resource1,
                resource2,
            )

            service = providers.Factory(
                Service,
                client,
            )

        container = ContainerWithArgs()

        client1 = self._run(container.client())
        client2 = self._run(container.client())

        self.assertIsInstance(client1, Client)
        self.assertIs(client1.resource1, RESOURCE1)
        self.assertIs(client1.resource2, RESOURCE2)

        self.assertIsInstance(client2, Client)
        self.assertIs(client2.resource1, RESOURCE1)
        self.assertIs(client2.resource2, RESOURCE2)

        service1 = self._run(container.service())
        service2 = self._run(container.service())

        self.assertIsInstance(service1, Service)
        self.assertIsInstance(service1.client, Client)
        self.assertIs(service1.client.resource1, RESOURCE1)
        self.assertIs(service1.client.resource2, RESOURCE2)

        self.assertIsInstance(service2, Service)
        self.assertIsInstance(service2.client, Client)
        self.assertIs(service2.client.resource1, RESOURCE1)
        self.assertIs(service2.client.resource2, RESOURCE2)

        self.assertIsNot(service1.client, service2.client)

    def test_kwargs_injection(self):
        container = Container()

        client1 = self._run(container.client())
        client2 = self._run(container.client())

        self.assertIsInstance(client1, Client)
        self.assertIs(client1.resource1, RESOURCE1)
        self.assertIs(client1.resource2, RESOURCE2)

        self.assertIsInstance(client2, Client)
        self.assertIs(client2.resource1, RESOURCE1)
        self.assertIs(client2.resource2, RESOURCE2)

        service1 = self._run(container.service())
        service2 = self._run(container.service())

        self.assertIsInstance(service1, Service)
        self.assertIsInstance(service1.client, Client)
        self.assertIs(service1.client.resource1, RESOURCE1)
        self.assertIs(service1.client.resource2, RESOURCE2)

        self.assertIsInstance(service2, Service)
        self.assertIsInstance(service2.client, Client)
        self.assertIs(service2.client.resource1, RESOURCE1)
        self.assertIs(service2.client.resource2, RESOURCE2)

        self.assertIsNot(service1.client, service2.client)

    def test_args_kwargs_injection(self):
        class ContainerWithArgsAndKwArgs(containers.DeclarativeContainer):
            resource1 = providers.Resource(init_resource, providers.Object(RESOURCE1))
            resource2 = providers.Resource(init_resource, providers.Object(RESOURCE2))

            client = providers.Factory(
                Client,
                resource1,
                resource2=resource2,
            )

            service = providers.Factory(
                Service,
                client=client,
            )

        container = ContainerWithArgsAndKwArgs()

        client1 = self._run(container.client())
        client2 = self._run(container.client())

        self.assertIsInstance(client1, Client)
        self.assertIs(client1.resource1, RESOURCE1)
        self.assertIs(client1.resource2, RESOURCE2)

        self.assertIsInstance(client2, Client)
        self.assertIs(client2.resource1, RESOURCE1)
        self.assertIs(client2.resource2, RESOURCE2)

        service1 = self._run(container.service())
        service2 = self._run(container.service())

        self.assertIsInstance(service1, Service)
        self.assertIsInstance(service1.client, Client)
        self.assertIs(service1.client.resource1, RESOURCE1)
        self.assertIs(service1.client.resource2, RESOURCE2)

        self.assertIsInstance(service2, Service)
        self.assertIsInstance(service2.client, Client)
        self.assertIs(service2.client.resource1, RESOURCE1)
        self.assertIs(service2.client.resource2, RESOURCE2)

        self.assertIsNot(service1.client, service2.client)

    def test_attributes_injection(self):
        class ContainerWithAttributes(containers.DeclarativeContainer):
            resource1 = providers.Resource(init_resource, providers.Object(RESOURCE1))
            resource2 = providers.Resource(init_resource, providers.Object(RESOURCE2))

            client = providers.Factory(
                Client,
                resource1,
                resource2=None,
            )
            client.add_attributes(resource2=resource2)

            service = providers.Factory(
                Service,
                client=None,
            )
            service.add_attributes(client=client)

        container = ContainerWithAttributes()

        client1 = self._run(container.client())
        client2 = self._run(container.client())

        self.assertIsInstance(client1, Client)
        self.assertIs(client1.resource1, RESOURCE1)
        self.assertIs(client1.resource2, RESOURCE2)

        self.assertIsInstance(client2, Client)
        self.assertIs(client2.resource1, RESOURCE1)
        self.assertIs(client2.resource2, RESOURCE2)

        service1 = self._run(container.service())
        service2 = self._run(container.service())

        self.assertIsInstance(service1, Service)
        self.assertIsInstance(service1.client, Client)
        self.assertIs(service1.client.resource1, RESOURCE1)
        self.assertIs(service1.client.resource2, RESOURCE2)

        self.assertIsInstance(service2, Service)
        self.assertIsInstance(service2.client, Client)
        self.assertIs(service2.client.resource1, RESOURCE1)
        self.assertIs(service2.client.resource2, RESOURCE2)

        self.assertIsNot(service1.client, service2.client)


class SingletonTests(AsyncTestCase):

    def test_injections(self):
        class ContainerWithSingletons(containers.DeclarativeContainer):
            resource1 = providers.Resource(init_resource, providers.Object(RESOURCE1))
            resource2 = providers.Resource(init_resource, providers.Object(RESOURCE2))

            client = providers.Singleton(
                Client,
                resource1=resource1,
                resource2=resource2,
            )

            service = providers.Singleton(
                Service,
                client=client,
            )

        container = ContainerWithSingletons()

        client1 = self._run(container.client())
        client2 = self._run(container.client())

        self.assertIsInstance(client1, Client)
        self.assertIs(client1.resource1, RESOURCE1)
        self.assertIs(client1.resource2, RESOURCE2)

        self.assertIsInstance(client2, Client)
        self.assertIs(client2.resource1, RESOURCE1)
        self.assertIs(client2.resource2, RESOURCE2)

        service1 = self._run(container.service())
        service2 = self._run(container.service())

        self.assertIsInstance(service1, Service)
        self.assertIsInstance(service1.client, Client)
        self.assertIs(service1.client.resource1, RESOURCE1)
        self.assertIs(service1.client.resource2, RESOURCE2)

        self.assertIsInstance(service2, Service)
        self.assertIsInstance(service2.client, Client)
        self.assertIs(service2.client.resource1, RESOURCE1)
        self.assertIs(service2.client.resource2, RESOURCE2)

        self.assertIs(service1, service2)
        self.assertIs(service1.client, service2.client)
        self.assertIs(service1.client, client1)

        self.assertIs(service2.client, client2)
        self.assertIs(client1, client2)

    def test_async_mode(self):
        instance = object()

        async def create_instance():
            return instance

        provider = providers.Singleton(create_instance)

        instance1 = self._run(provider())
        instance2 = self._run(provider())

        self.assertIs(instance1, instance2)
        self.assertIs(instance, instance)


class DelegatedSingletonTests(AsyncTestCase):

    def test_async_mode(self):
        instance = object()

        async def create_instance():
            return instance

        provider = providers.DelegatedSingleton(create_instance)

        instance1 = self._run(provider())
        instance2 = self._run(provider())

        self.assertIs(instance1, instance2)
        self.assertIs(instance, instance)


class ThreadSafeSingletonTests(AsyncTestCase):

    def test_async_mode(self):
        instance = object()

        async def create_instance():
            return instance

        provider = providers.ThreadSafeSingleton(create_instance)

        instance1 = self._run(provider())
        instance2 = self._run(provider())

        self.assertIs(instance1, instance2)
        self.assertIs(instance, instance)


class DelegatedThreadSafeSingletonTests(AsyncTestCase):

    def test_async_mode(self):
        instance = object()

        async def create_instance():
            return instance

        provider = providers.DelegatedThreadSafeSingleton(create_instance)

        instance1 = self._run(provider())
        instance2 = self._run(provider())

        self.assertIs(instance1, instance2)
        self.assertIs(instance, instance)


class ThreadLocalSingletonTests(AsyncTestCase):

    def test_async_mode(self):
        instance = object()

        async def create_instance():
            return instance

        provider = providers.ThreadLocalSingleton(create_instance)

        instance1 = self._run(provider())
        instance2 = self._run(provider())

        self.assertIs(instance1, instance2)
        self.assertIs(instance, instance)


class DelegatedThreadLocalSingletonTests(AsyncTestCase):

    def test_async_mode(self):
        instance = object()

        async def create_instance():
            return instance

        provider = providers.DelegatedThreadLocalSingleton(create_instance)

        instance1 = self._run(provider())
        instance2 = self._run(provider())

        self.assertIs(instance1, instance2)
        self.assertIs(instance, instance)


class ProvidedInstanceTests(AsyncTestCase):

    def test_provided_attribute(self):
        class TestClient:
            def __init__(self, resource):
                self.resource = resource

        class TestService:
            def __init__(self, resource):
                self.resource = resource

        class TestContainer(containers.DeclarativeContainer):
            resource = providers.Resource(init_resource, providers.Object(RESOURCE1))
            client = providers.Factory(TestClient, resource=resource)
            service = providers.Factory(TestService, resource=client.provided.resource)

        container = TestContainer()

        instance1, instance2 = self._run(
            asyncio.gather(
                container.service(),
                container.service(),
            ),
        )

        self.assertIs(instance1.resource, RESOURCE1)
        self.assertIs(instance2.resource, RESOURCE1)
        self.assertIs(instance1.resource, instance2.resource)

    def test_provided_item(self):
        class TestClient:
            def __init__(self, resource):
                self.resource = resource

            def __getitem__(self, item):
                return getattr(self, item)

        class TestService:
            def __init__(self, resource):
                self.resource = resource

        class TestContainer(containers.DeclarativeContainer):
            resource = providers.Resource(init_resource, providers.Object(RESOURCE1))
            client = providers.Factory(TestClient, resource=resource)
            service = providers.Factory(TestService, resource=client.provided['resource'])

        container = TestContainer()

        instance1, instance2 = self._run(
            asyncio.gather(
                container.service(),
                container.service(),
            ),
        )

        self.assertIs(instance1.resource, RESOURCE1)
        self.assertIs(instance2.resource, RESOURCE1)
        self.assertIs(instance1.resource, instance2.resource)

    def test_provided_method_call(self):
        class TestClient:
            def __init__(self, resource):
                self.resource = resource

            def get_resource(self):
                return self.resource

        class TestService:
            def __init__(self, resource):
                self.resource = resource

        class TestContainer(containers.DeclarativeContainer):
            resource = providers.Resource(init_resource, providers.Object(RESOURCE1))
            client = providers.Factory(TestClient, resource=resource)
            service = providers.Factory(TestService, resource=client.provided.get_resource.call())

        container = TestContainer()

        instance1, instance2 = self._run(
            asyncio.gather(
                container.service(),
                container.service(),
            ),
        )

        self.assertIs(instance1.resource, RESOURCE1)
        self.assertIs(instance2.resource, RESOURCE1)
        self.assertIs(instance1.resource, instance2.resource)


class DependencyTests(AsyncTestCase):

    def test_isinstance(self):
        dependency = 1.0

        async def get_async():
            return dependency

        provider = providers.Dependency(instance_of=float)
        provider.override(providers.Callable(get_async))

        dependency1 = self._run(provider())
        dependency2 = self._run(provider())

        self.assertEqual(dependency1, dependency)
        self.assertEqual(dependency2, dependency)

    def test_isinstance_invalid(self):
        async def get_async():
            return {}

        provider = providers.Dependency(instance_of=float)
        provider.override(providers.Callable(get_async))

        with self.assertRaises(errors.Error):
            self._run(provider())

    def test_async_mode(self):
        dependency = 123

        async def get_async():
            return dependency

        def get_sync():
            return dependency

        provider = providers.Dependency(instance_of=int)
        provider.override(providers.Factory(get_async))

        dependency1 = self._run(provider())
        dependency2 = self._run(provider())
        self.assertEqual(dependency1, dependency)
        self.assertEqual(dependency2, dependency)

        provider.override(providers.Factory(get_sync))

        dependency3 = self._run(provider())
        dependency4 = self._run(provider())
        self.assertEqual(dependency3, dependency)
        self.assertEqual(dependency4, dependency)


class OverrideTests(AsyncTestCase):

    def test_provider(self):
        dependency = object()

        async def _get_dependency_async():
            return dependency

        def _get_dependency_sync():
            return dependency

        provider = providers.Provider()

        provider.override(providers.Callable(_get_dependency_async))
        dependency1 = self._run(provider())

        provider.override(providers.Callable(_get_dependency_sync))
        dependency2 = self._run(provider())

        self.assertIs(dependency1, dependency)
        self.assertIs(dependency2, dependency)

    def test_callable(self):
        dependency = object()

        async def _get_dependency_async():
            return dependency

        def _get_dependency_sync():
            return dependency

        provider = providers.Callable(_get_dependency_async)
        dependency1 = self._run(provider())

        provider.override(providers.Callable(_get_dependency_sync))
        dependency2 = self._run(provider())

        self.assertIs(dependency1, dependency)
        self.assertIs(dependency2, dependency)

    def test_factory(self):
        dependency = object()

        async def _get_dependency_async():
            return dependency

        def _get_dependency_sync():
            return dependency

        provider = providers.Factory(_get_dependency_async)
        dependency1 = self._run(provider())

        provider.override(providers.Callable(_get_dependency_sync))
        dependency2 = self._run(provider())

        self.assertIs(dependency1, dependency)
        self.assertIs(dependency2, dependency)


class TestAsyncModeApi(unittest.TestCase):

    def setUp(self):
        self.provider = providers.Provider()

    def test_default_mode(self):
        self.assertFalse(self.provider.is_async_mode_enabled())
        self.assertFalse(self.provider.is_async_mode_disabled())
        self.assertTrue(self.provider.is_async_mode_undefined())

    def test_enable(self):
        self.provider.enable_async_mode()

        self.assertTrue(self.provider.is_async_mode_enabled())
        self.assertFalse(self.provider.is_async_mode_disabled())
        self.assertFalse(self.provider.is_async_mode_undefined())

    def test_disable(self):
        self.provider.disable_async_mode()

        self.assertFalse(self.provider.is_async_mode_enabled())
        self.assertTrue(self.provider.is_async_mode_disabled())
        self.assertFalse(self.provider.is_async_mode_undefined())

    def test_reset(self):
        self.provider.enable_async_mode()

        self.assertTrue(self.provider.is_async_mode_enabled())
        self.assertFalse(self.provider.is_async_mode_disabled())
        self.assertFalse(self.provider.is_async_mode_undefined())

        self.provider.reset_async_mode()

        self.assertFalse(self.provider.is_async_mode_enabled())
        self.assertFalse(self.provider.is_async_mode_disabled())
        self.assertTrue(self.provider.is_async_mode_undefined())