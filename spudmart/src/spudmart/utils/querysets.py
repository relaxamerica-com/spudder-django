from django.shortcuts import _get_queryset


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    results = queryset.filter(*args, **kwargs)
    return results[0] if len(results) > 0 else None