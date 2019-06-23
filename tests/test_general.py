

def test_serialization_and_caching():
    import imagepypelines as ip
    import pkgutil
    from types import ModuleType

    if not ip.cache.enabled():
        ip.cache.secure_enable()

    def serialize_blocks_and_pipelines(mod):
        for varname, var in vars(mod).items():
            print(var)
            if isinstance(var, (ip.Pipeline,ip.BaseBlock) ):
                print('serializing %s...' % varname)
                ip.cache[varname] = var
                ip.cache.remove(varname)

    serialize_blocks_and_pipelines(ip.blocks)
    serialize_blocks_and_pipelines(ip.pipelines)
    serialize_blocks_and_pipelines(ip)

if __name__ == "__main__":
    test_serialization_and_caching()
