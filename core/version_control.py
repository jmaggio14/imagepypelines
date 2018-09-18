
import imsciutils as iu


DEFAULT_PRINTER = 'version conTROLL'


def depreciated_msg(depreciation_msg, printer=None):
    if printer is None:
        printer = iu.get_printer(DEFAULT_PRINTER)
    else:
        printer = iu.get_printer(printer)

    def _depreciated(func):
        def _depreciated_(*args,**kwargs):
            printer.warning("DEPRECIATION WARNING:", depreciation_msg)
            return func(*args,**kwargs)

        return _depreciated_
    return _depreciated



def experimental_msg(experimental_msg=None, printer=None):
    if printer is None:
        printer = iu.get_printer(DEFAULT_PRINTER)
    else:
        printer = iu.get_printer(printer)

    create_message = False
    if experimental_msg is None:
        create_message = True

    def _experimental(func):
        def _experimental_(*args,**kwargs):
            if create_message:
                experimental_msg = "'{}' is an experimental feature. Its functionality may be buggy or exhibit undefined behavior!".format(func.__name__)
            printer.warning("EXPERIMENTAL WARNING:", experimental_msg)
            return func(*args,**kwargs)

        return _experimental_
    return _experimental
