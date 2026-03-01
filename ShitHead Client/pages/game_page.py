def game_manager(event, pos, cards_message, cards_to_throw, to_who):
    from pages._client_ref import get_client_module

    pc = get_client_module()

    return pc.game_manager(event, pos, cards_message, cards_to_throw, to_who)
