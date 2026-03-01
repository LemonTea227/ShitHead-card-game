def choose_a_room_menu(event, pos, games_message, page):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.choose_a_room_menu(event, pos, games_message, page)
