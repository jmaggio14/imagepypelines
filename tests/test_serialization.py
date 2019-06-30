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



def test_new_uuid_upon_copy_or_serialization():
    import imagepypelines as ip
    from copy import deepcopy
    import pickle

    if not ip.cache.enabled():
        ip.cache.secure_enable()


    # make a pipeline
    pipeline = ip.pipelines.LinearTransform(10,5)
    pipeline.logger.setLevel(0)
    pipeline.logger.warning("I'm about to rename this pipeline... It's ids shouldn't change")
    pipeline.rename("original")


    copied = deepcopy(pipeline)
    copied.rename("deepcopy")

    serialized = pickle.loads( pickle.dumps(pipeline) )
    serialized.rename("serialized")

    # sibling id should be the same among all of them
    assert pipeline.sibling_id == copied.sibling_id
    assert pipeline.sibling_id == serialized.sibling_id

    # these should be different
    assert pipeline.uuid != copied.uuid
    assert pipeline.uuid != serialized.uuid
    assert copied.uuid != serialized.uuid


    pipeline.logger.info("I'm the original!")
    copied.logger.info("I'm the deep copy!")
    serialized.logger.info("I'm the unpickled one!")


if __name__ == "__main__":
    test_logger_serialization()
    test_new_uuid_upon_copy_or_serialization()
