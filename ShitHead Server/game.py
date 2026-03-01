import random


def get_num(item):
    return item[0]


def sort_hand_viable(hand, visible):
    all = []
    for i in range(len(hand)):
        all.append(hand.pop(0))
    for i in range(len(visible)):
        all.append(visible.pop(0))
    for card in all:
        if len(visible) < 3:
            if card[0] == 10 or card[0] == 14:
                visible.append(card)
    for card in all:
        if len(visible) < 3:
            if card[0] == 2 or card[0] == 3:
                visible.append(card)
    for card in all:
        if len(visible) < 3:
            if card[0] == 1:
                visible.append(card)
    for card in visible:
        all.remove(card)
    all = sorted(all, key=get_num)
    while len(visible) < 3:
        visible.append(all.pop())
    while len(hand) < 3:
        hand.append(all.pop())


def sort_hand(hand):
    h = []
    for i in range(len(hand)):
        h.append(hand.pop(0))
    for card in h:
        if card[0] == 10 or card[0] == 14:
            hand.append(card)
    for card in h:
        if card[0] == 2 or card[0] == 3:
            hand.append(card)
    for card in h:
        if card[0] == 1:
            hand.append(card)
    for card in hand:
        h.remove(card)
    h = sorted(h, key=get_num)
    while h:
        hand.append(h.pop())


class Game:
    def __init__(self, num_room, max_players, players=None):
        if players is None:
            players = []
        self.num_room = num_room
        self.max_players = max_players
        self.players = players
        self.__deck = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1),
                       (12, 1),
                       (13, 1), (14, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2),
                       (10, 2),
                       (11, 2), (12, 2), (13, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
                       (9, 3),
                       (10, 3), (11, 3), (12, 3), (13, 3), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4),
                       (8, 4), (9, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4)]
        self.__throw_deck = []
        self.__out_deck = []
        self.turn = 0
        self.player_cards = {}
        self.send_dict = {}
        self.started = False
        self.finished = False

    def add_player(self, sock_player):
        """
        this function is responsible for adding a player
        :param sock_player:
        :return: None
        """
        self.players.append(sock_player)

    def remove_player(self, sock_player):
        """
        this function is responsible for removing a player
        :param sock_player:
        :return: None
        """
        if sock_player in self.players:
            self.players.remove(sock_player)
            del self.send_dict[sock_player]
            if self.started:
                self.finish()

    def shuffle_card(self):
        """
        this function shuffles the deck she get to shuffle
        :return: shuffled deck
        """
        random.shuffle(self.__deck)

    def start_game(self):
        """
        this function is responsible for starting a game
        :return:
        """
        self.shuffle_card()
        for player in self.players:
            hand = []
            visible = []
            secret = []
            for j in range(3):
                secret.append(self.__deck.pop())
                visible.append(self.__deck.pop())
                hand.append(self.__deck.pop())
            sort_hand_viable(hand, visible)
            self.player_cards[player] = []
            self.player_cards[player].append(secret)
            self.player_cards[player].append(visible)
            self.player_cards[player].append(hand)
        self.started = True
        self.update()

    def update(self):
        """
        this function is responsible for updating the players for a change in the board
        :return: None
        """
        for player in self.players:
            sort_hand(self.player_cards[player][2])
        for player in self.players:
            message = 'GAME~UPDATE~' + str(len(self.__deck)) + '~'
            if self.__throw_deck:
                message += str(self.__throw_deck[-1][0]) + ',' + str(self.__throw_deck[-1][1])
            else:
                message += '0,0'
            message += '~Hand:'
            for card in self.player_cards[player][2]:
                message += str(card[0]) + ',' + str(card[1]) + '|'
            message += '~Visible:'
            for card in self.player_cards[player][1]:
                message += str(card[0]) + ',' + str(card[1]) + '|'
            message += '~Secret:' + str(len(self.player_cards[player][0]))
            message += '~Turn:' + str(self.turn)
            for p in self.players:
                if p != player:
                    num_p = 0
                    for i in range(len(self.players)):
                        if self.players[i] == p:
                            num_p = i
                    message += '~Player:' + str(num_p + 1)
                    message += '~Hand:' + str(len(self.player_cards[p][2]))
                    message += '~Visible:'
                    for card in self.player_cards[p][1]:
                        message += str(card[0]) + ',' + str(card[1]) + '|'
                    message += '~Secret:' + str(len(self.player_cards[p][0]))
            message += '~~~'
            if player not in self.send_dict:
                self.send_dict[player] = []
            self.send_dict[player].append(message)

    def throw(self, player, cards, to_who):
        """
        this function is responsible for the throws of the players
        :param player:
        :param cards:
        :param to_who:
        :return: None
        """
        if len(cards) < 4:
            if self.players[self.turn] == player:
                change_turn = False
                if self.player_cards[player][2] or self.player_cards[player][1] and cards != []:
                    for card in cards:
                        if self.is_ok_to_throw(card[0]):
                            change_turn = True
                            if card[0] == 14:
                                if to_who != 0:
                                    self.give_deck(self.players[to_who - 1])
                                else:
                                    self.give_deck(self.players[self.last_turn()])
                                if self.player_cards[player][2]:
                                    self.player_cards[player][2].remove(card)
                                    if self.__deck and len(self.player_cards[player][2]) < 3:
                                        self.player_cards[player][2].append(self.__deck.pop())
                                elif self.player_cards[player][1]:
                                    self.player_cards[player][1].remove(card)
                                self.__out_deck.append(card)
                            else:
                                if self.player_cards[player][2]:
                                    self.player_cards[player][2].remove(card)
                                    if self.__deck and len(self.player_cards[player][2]) < 3:
                                        self.player_cards[player][2].append(self.__deck.pop())
                                elif self.player_cards[player][1]:
                                    self.player_cards[player][1].remove(card)
                                self.__throw_deck.append(card)
                                if not self.effect_of_throw(card[0], player):
                                    change_turn = False
                elif self.player_cards[player][0] and not cards:
                    card = self.player_cards[player][0].pop()
                    if card[0] == 14:
                        if to_who != 0:
                            self.give_deck(self.players[to_who - 1])
                        else:
                            self.give_deck(self.players[self.last_turn()])
                        self.__out_deck.append(card)
                    if self.is_ok_to_throw(card[0]):
                        change_turn = True
                        self.__throw_deck.append(card)
                        if not self.effect_of_throw(card[0], player):
                            change_turn = False
                    else:
                        self.take_deck(player)
                        self.player_cards[player][2].append(card)

                if change_turn:
                    self.change_turn(1)
                if self.is_over():
                    self.finish()
            else:
                if not self.__throw_deck:
                    if self.player_cards[player][2] or self.player_cards[player][1] and cards != []:
                        change_turn = False
                        for card in cards:
                            if card[0] == 4:
                                change_turn = True
                                self.effect_of_throw(card[0], player)
                                if self.player_cards[player][2]:
                                    self.player_cards[player][2].remove(card)
                                    if self.__deck and len(self.player_cards[player][2]) < 3:
                                        self.player_cards[player][2].append(self.__deck.pop())
                                elif self.player_cards[player][1]:
                                    self.player_cards[player][1].remove(card)
                                self.__throw_deck.append(card)

                        if change_turn:
                            for i in range(len(self.players)):
                                if self.players[i] == player:
                                    self.turn = i
                            self.change_turn(1)
        elif len(cards) == 4:
            for card in cards:
                if self.player_cards[player][2]:
                    self.player_cards[player][2].remove(card)
                    self.__out_deck.append(card)
                elif self.player_cards[player][1]:
                    self.player_cards[player][1].remove(card)
                    self.__out_deck.append(card)
            self.__out_deck.extend(self.__throw_deck)
            self.__throw_deck = []
            while self.__deck and len(self.player_cards[player][2]) < 3:
                self.player_cards[player][2].append(self.__deck.pop())
            for i in range(len(self.players)):
                if self.players[i] == player:
                    self.turn = i
        self.update()

    def take_deck(self, player):
        """
        this function is responsible for giving a player the throw deck
        :param player:
        :return:
        """
        if self.players[self.turn] == player and self.__throw_deck:
            self.player_cards[player][2].extend(self.__throw_deck)
            self.__throw_deck = []
            self.change_turn(1)
            self.update()

    def give_deck(self, player):
        """
        this function is responsible for giving a player the throw deck
        :param player:
        :return:
        """
        if self.__throw_deck:
            self.player_cards[player][2].extend(self.__throw_deck)
            self.__throw_deck = []
            self.change_turn(1)
            self.update()

    def change_turn(self, times):
        """
        this function is responsible for changing the turns
        :param times:
        :return: None
        """
        for i in range(times):
            if self.turn == len(self.players) - 1:
                self.turn = 0
            else:
                self.turn += 1

    def last_turn(self):
        """
        this function is responsible for returning who was in the last turn
        :return:
        """
        if self.turn == 0:
            return len(self.players) - 1
        else:
            return self.turn - 1

    def is_ok_to_throw(self, card_number):
        """
        this function is responsible for checking if it is ok to throw
        :param card_number:
        :return: ok: True, not ok: False.
        """
        if self.__throw_deck:
            if self.__throw_deck[-1][0] == 1 and (card_number <= 3 or card_number == 10 or card_number == 14):
                return True
            elif self.__throw_deck[-1][0] == 2:
                return True
            elif self.__throw_deck[-1][0] == 3:
                last_card = self.__throw_deck.pop()
                bool_ret = self.is_ok_to_throw(card_number)
                self.__throw_deck.append(last_card)
                return bool_ret
            elif self.__throw_deck[-1][0] == 4:
                return True
            elif self.__throw_deck[-1][0] == 5 and (card_number != 4):
                return True
            elif self.__throw_deck[-1][0] == 6 and not (3 < card_number < 6):
                return True
            elif self.__throw_deck[-1][0] == 7 and (1 < card_number <= 7 or card_number == 10 or card_number == 14):
                return True
            elif self.__throw_deck[-1][0] == 8 and not (3 < card_number < 8):
                return True
            elif self.__throw_deck[-1][0] == 9 and not (3 < card_number < 9):
                return True
            elif self.__throw_deck[-1][0] == 10:
                return True
            elif self.__throw_deck[-1][0] == 11 and not (3 < card_number < 10):
                return True
            elif self.__throw_deck[-1][0] == 12 and not (3 < card_number < 10 or card_number == 11):
                return True
            elif self.__throw_deck[-1][0] == 13 and not (3 < card_number < 10 or 11 < card_number < 13):
                return True
            elif self.__throw_deck[-1][0] == 14:
                return True
            else:
                return False
        else:
            return True

    def effect_of_throw(self, card_number, player):
        """
        this function is responsible for making the effect of the throw
        :param card_number:
        :param player:
        :return:
        """
        if not self.__throw_deck and card_number == 4:
            for i in range(len(self.players)):
                if self.players[i] == player:
                    self.turn = i
                    self.change_turn(1)
            return False
        if card_number == 8:
            self.change_turn(1)
            return True
        if card_number == 10:
            self.__out_deck.extend(self.__throw_deck)
            self.__throw_deck = []
            for i in range(len(self.players)):
                if self.players[i] == player:
                    self.turn = i
            return False
        return True

    def is_over(self):
        """
        this function is responsible for checking if the game is over
        :return: ok: True, not ok: False.
        """
        if self.started:
            for player in self.players:
                player_finish = (True, player)
                if player not in self.player_cards:
                    self.player_cards[player] = []
                for deck in self.player_cards[player]:
                    if deck:
                        player_finish = (False, player)
                if player_finish[0]:
                    return player_finish
        return False

    def finish(self):
        """
        this function is responsible for checking if the game can't continue
        :return: None
        """
        if not self.finished and self.started:
            if len(self.players) != self.max_players:
                for player in self.players:
                    if player not in self.send_dict:
                        self.send_dict[player] = []
                    self.send_dict[player].append('GAME~FINISH~player disconnected~~~')
                self.finished = True

            else:
                finish = self.is_over()
                if finish:
                    for player in self.players:
                        if not self.player_cards[player][2] and not self.player_cards[player][1] and not \
                        self.player_cards[player][0]:
                            self.send_dict[player].append('GAME~FINISH~You Won!~~~')
                        else:
                            self.send_dict[player].append('GAME~FINISH~You are the ShitHead!~~~')
                    self.finished = True
