from nose.selector import Selector
from nose.plugins import Plugin
import os
import django.test


class TestDiscoverySelector(Selector):
    def wantClass(self, cls):
        return issubclass(cls, FormattedOutputTestCase)

    def wantFile(self, filename):
        parts = filename.split(os.path.sep)
        return 'test' in parts and filename.endswith('.py')

    def wantModule(self, module):
        parts = module.__name__.split('.')
        return 'test' in parts


class TestDiscoveryPlugin(Plugin):
    enabled = True

    def configure(self, options, conf):
        pass

    def prepareTestLoader(self, loader):
        loader.selector = TestDiscoverySelector(loader.config)


class FormattedOutputTestCase(django.test.TestCase):
    def shortDescription(self):
        doc = self._testMethodDoc
        doc = doc and doc.split("\n")[0].strip() or None
        if doc:
            return "%s [%s:%s.%s]" % (doc, self.__class__.__module__, self.__class__.__name__, self._testMethodName)
        else:
            return "%s [%s:%s.%s]" % (self._testMethodName, self.__class__.__module__, self.__class__.__name__, self._testMethodName)