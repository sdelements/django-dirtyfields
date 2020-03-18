import sys


def get_m2m_with_model(given_model):
    return [
        (f, f.model if f.model != given_model else None)
        for f in given_model._meta.get_fields()
        if f.many_to_many and not f.auto_created
    ]


def is_buffer(value):
    if sys.version_info < (3, 0, 0):
        return isinstance(value, buffer)  # noqa
    else:
        return isinstance(value, memoryview)
