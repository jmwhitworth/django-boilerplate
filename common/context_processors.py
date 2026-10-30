from .utils import is_local, is_production, is_staging, is_testing


def environment(request):
    return {
        "is_local": is_local(),
        "is_production": is_production(),
        "is_staging": is_staging(),
        "is_testing": is_testing(),
    }
