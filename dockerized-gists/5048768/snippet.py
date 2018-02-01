"""
This test module exercises the IPython qt import logic using pytest

It should be run with PyQt4 and PySide installed, as

py.test test_ipython_qt.py --boxed

It requires pytest and pytest-xdist
"""
from subprocess import check_output
import pytest
import os
import sys

def set_sip(version):
    import sip
    sip.setapi('QString', version)
    sip.setapi('QVariant', version)


def disable(*modules):
    """ Simualte the non-existance of modules

    :param modules: One or more modules to mock-uninstall, for the rest of the
                    process
    """
    class ID(object):
        def __init__(self, modules):
            self.forbidden = modules
        def find_module(self, mod_name, pth):
            if mod_name in self.forbidden:
                return self
        def load_module(self, mod_name):
            raise ImportError("forbidden")

    id = ID(modules)
    import sys
    sys.meta_path.append(id)


class TestQtLoaders(object):
    def test_prevent_multi_import_pyside(self):
        from IPython.external.qt_loaders import load_qt
        load_qt(['pyside'])
        with pytest.raises(ImportError) as exc:
            import PyQt4
        assert exc.value.args[0].strip().startswith('Importing PyQt4 disabled')

    def test_prevent_multi_import_qt4v2(self):
        from IPython.external.qt_loaders import load_qt
        load_qt(['pyqt'])
        with pytest.raises(ImportError) as exc:
            import PySide
        assert exc.value.args[0].strip().startswith('Importing PySide')

    def test_prevent_multi_import_qt4v1(self):
        from IPython.external.qt_loaders import load_qt
        load_qt(['pyqtv1'])
        with pytest.raises(ImportError) as exc:
            import PySide
        assert exc.value.args[0].strip().startswith('Importing PySide')

    def test_prevent_multi_import_qtdefault(self):
        from IPython.external.qt_loaders import load_qt
        load_qt(['pyqtdefault'])
        with pytest.raises(ImportError) as exc:
            import PySide
        assert exc.value.args[0].strip().startswith('Importing PySide')

    def test_prevent_incompatible_qt_multimport(self):
        from IPython.external.qt_loaders import load_qt
        load_qt(['pyqt'])
        with pytest.raises(ImportError) as exc:
            load_qt(['pyqtv1'])
        assert exc.value.args[0].strip().startswith('Could not load')


class TestQt(object):
    def assert_api(self, version):
        from IPython.external import qt
        from IPython.external.qt_loaders import loaded_api
        assert loaded_api() == version

    def test_default_pyside(self):
        self.assert_api('pyside')

    def test_qt4_if_no_pyside(self):
        disable('PySide')
        self.assert_api('pyqt')

    def test_ets_var_qt(self):
        import os
        os.environ['QT_API'] = 'pyqt'
        self.assert_api('pyqt')

    def test_ets_var_qt_missing(self):
        import os
        disable('PyQt4')
        os.environ['QT_API'] = 'pyqt'
        with pytest.raises(ImportError) as exc:
            self.assert_api(None)
        assert exc.value.args[0].strip().startswith('Could not load requested')

    def test_ets_var_pyside(self):
        import os
        os.environ['QT_API'] = 'pyside'
        self.assert_api('pyside')

    def test_ets_var_qt_missing(self):
        import os
        disable('PySide')
        os.environ['QT_API'] = 'pyside'
        with pytest.raises(ImportError) as exc:
            self.assert_api(None)
        assert exc.value.args[0].strip().startswith('Could not load requested')

    def test_pyside_with_bare_qt(self):
        import PyQt4
        self.assert_api('pyside')

    def test_pyqt_with_bare_pyside(self):
        import PySide
        import os
        os.environ['QT_API'] = 'pyqt'
        self.assert_api('pyqt')

    def test_obsolete_pyside(self):
        import PySide
        PySide.__version__ = '0.1.0'
        self.assert_api('pyqt')


class TestQtForKernel(object):

    def assert_api(self, version):
        from IPython.external import qt_for_kernel
        from IPython.external.qt_loaders import loaded_api
        assert loaded_api() == version

    def setup_mpl(self, version='1.2', backend=None):
        if version is None:
            return

        import matplotlib
        matplotlib.__version__ = version
        matplotlib.rcParams.pop('backend.qt4')

        if backend is not None:
            matplotlib.rcParams['backend.qt4'] = backend

    def test_qt4_py2_noinfo(self):
        self.assert_api('pyqtv1')

    def test_qt4_py2_api2(self):
        set_sip(2)
        self.assert_api('pyqt')

    def test_noqt4_py2(self):
        disable('PyQt4')
        self.assert_api('pyside')

    def test_noqt4_py2_api2(self):
        set_sip(2)
        disable('PyQt4')
        self.assert_api('pyside')

    def test_pickup_default(self):
        from PySide import QtCore
        self.assert_api('pyside')

    def test_no_api(self):
        disable('PyQt4', 'PySide')
        with pytest.raises(ImportError) as e:
            from IPython.external import qt_for_kernel
        assert e.value.args[0].strip().startswith("Could not load")

    def test_post_import(self):
        from IPython.external import qt_for_kernel
        self.assert_api('pyqtv1')
        with pytest.raises(ImportError) as e:
            import PySide
        assert e.value.args[0].strip().startswith('Importing PySide disabled')

    def test_pyqt_var(self):
        os.environ['QT_API'] = 'pyqt'
        self.assert_api('pyqt')

    def test_pyside_var(self):
        os.environ['QT_API'] = 'pyside'
        self.assert_api('pyside')

    def test_matplotlib_import(self):
        self.setup_mpl()
        self.assert_api('pyqtv1')

    def test_matplotlib_rc_pyside(self):
        self.setup_mpl(backend='PySide')
        self.assert_api('pyside')

    def test_matplotlib_rc_pyqt(self):
        self.setup_mpl(backend='PyQt4')
        self.assert_api('pyqtv1')

    def test_matplotlib_old(self):
        self.setup_mpl(version='1.0', backend='PySide')
        self.assert_api('pyqtv1')

    def tet_matplotlib_rc_bad(self):
        class MockMpl(object):
            rcParams = {}

        mpl = MockMpl()
        sys.modules['matplotlib'] = Mpl()
        matplotlib.rcParams['backend.qt4'] = 'bad'

        with pytest.raises(ImportError) as e:
            self.assert_api('_')
        assert e.value.args[0].startswith('unhandled value for backend.qt4')


@pytest.mark.parametrize(('commit', 'forbidden'),
                         (('pyside', 'PyQt4'),
                          ('pyqt', 'PySide'),
                          ('pyqtv1', 'PySide'),
                          ('pyqtdefault', 'PySide')))
def test_commit(commit, forbidden):
    from IPython.external.qt_loaders import commit_api

    commit_api(commit)

    with pytest.raises(ImportError) as exc:
        __import__(forbidden)
    assert exc.value.args[0].strip().startswith("Importing %s disabled" %
                                                forbidden)

def test_qtapi_version():
    from IPython.external.qt_loaders import qtapi_version
    assert qtapi_version() is None
    import sip
    sip.setapi('QString', 2)
    assert qtapi_version() == 2


def test_can_import():
    from IPython.external.qt_loaders import can_import

    assert can_import('pyqt')
    assert can_import('pyside')
    import PySide

    PySide.__version__ = '0.1.0'
    assert can_import('pyqt')
    assert can_import('pyqtv1')
    assert can_import('pyqtdefault')
    assert not can_import('pyside')

    from PyQt4 import QtCore
    assert not can_import('pyqt')
    assert can_import('pyqtdefault')
    assert can_import('pyqtv1')
