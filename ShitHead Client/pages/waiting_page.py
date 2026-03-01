def wait_to_full(event, pos, room, p_now, people):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.wait_to_full(event, pos, room, p_now, people)
