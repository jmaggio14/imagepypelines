

def test_serialization_and_caching():
    import imagepypelines as ip
    import pkgutil
    from types import ModuleType

    if not ip.cache.enabled():
        ip.cache.secure_enable()

    def serialize_blocks_and_pipelines(mod):
        for varname, var in vars(mod).items():
            if isinstance(var, ModuleType):
                serialize_blocks_and_pipelines(var)

            if isinstance(var, (ip.Pipeline,ip.BaseBlock) ):
                print('serializing %s...' % varname)
                ip.cache[varname] = var
                ip.cache.remove(varname)

    for importer, modname, ispkg in pkgutil.walk_packages(
                                                      path=ip.__path__,
                                                      prefix=ip.__name__+'.',
                                                      onerror=lambda x: None):
        if ispkg:
            mod = importer.find_module(modname).load_module(modname)
            serialize_blocks_and_pipelines(mod)
