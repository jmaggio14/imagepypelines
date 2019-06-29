#
#
# def test_serialization_and_caching():
#     import imagepypelines as ip
#     import pkgutil
#     from types import ModuleType
#
#     if not ip.cache.enabled():
#         ip.cache.secure_enable()
#
#     def serialize_blocks_and_pipelines(mod):
#         for varname, var in vars(mod).items():
#             repr(var)
#             str(var)
#             if isinstance(var, (ip.Pipeline,ip.BaseBlock) ):
#                 print('serializing %s...' % varname)
#                 ip.cache[varname] = var
#                 ip.cache.remove(varname)
#
#     serialize_blocks_and_pipelines(ip.blocks)
#     serialize_blocks_and_pipelines(ip.pipelines)
#     serialize_blocks_and_pipelines(ip)
#
#



def test_logger_serialization():
    import imagepypelines as ip
    if not ip.cache.enabled():
        ip.cache.secure_enable()

    ip.cache['master_logger'] = ip.MASTER_LOGGER
    ip.cache['master_logger.child'] = ip.get_logger('testChild')

    master = ip.cache['master_logger']
    child = ip.cache['master_logger.child']

    assert master ==  ip.MASTER_LOGGER
    assert child == ip.get_logger('testChild')

if __name__ == "__main__":
    test_logger_serialization()
