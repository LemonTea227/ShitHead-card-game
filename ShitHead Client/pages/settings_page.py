def settings_menu(event, pos):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.settings_menu(event, pos)
