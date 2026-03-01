def open_screen(event, pos):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.open_screen(event, pos)
