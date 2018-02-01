'''
Example code to show how it is possible to mock an entire module by patching
the sys.modules dict using mock ( http://www.voidspace.org.uk/python/mock/ ).
'''

from mock import patch, MagicMock

def test_import_patching():
    module_mock = MagicMock()
    with patch.dict('sys.modules', **{ 
            'unimportable_module': module_mock,
            'unimportable_module.submodule': module_mock,
        }):
        import unimportable_module.submodule
        assert unimportable_module.submodule == module_mock.submodule

