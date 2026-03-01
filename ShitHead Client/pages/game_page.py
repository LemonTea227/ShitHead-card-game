def game_manager(event, pos, cards_message, cards_to_throw, to_who):
    from pages import gameplay_pages

    return gameplay_pages.game_manager(
        event, pos, cards_message, cards_to_throw, to_who
    )
