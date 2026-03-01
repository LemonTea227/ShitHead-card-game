import sys


def get_client_module():
    main_module = sys.modules.get("__main__")
    if main_module and hasattr(main_module, "screen"):
        return main_module

    import project_client as pc

    return pc
