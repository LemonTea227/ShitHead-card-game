def create_a_room_menu(event, pos, num):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.create_a_room_menu(event, pos, num)
