import socket
import threading
import time

import game
from tcp_by_size import send_with_size, recv_by_size

IP = '0.0.0.0'
PORT = 22073
SEND = {}
THREAD = []
ONLINE_GAMES = []
QUICK_GAMES = []
AVAILABLE_GAMES = []


def main():
    server_socket = socket.socket()
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    while True:
        # open socket with client
        client_socket, address = server_socket.accept()
        print('connected to: SOCKET-{} : ADDRESS-{}'.format(client_socket, address))
        client_socket.settimeout(0.1)
        SEND[client_socket] = []
        t = threading.Thread(target=async_send_receive, args=(client_socket,))
        t.start()
        THREAD.append(t)

    server_socket.close()
    for t in THREAD:
        t.join()


def quick_game(sock, preferences):
    """
    this function is responsible for finding a quick game
    :param sock:
    :param preferences:
    :return: None
    """
    the_game = None
    for room in QUICK_GAMES:
        if room.max_players == preferences and len(room.players) != room.max_players:
            the_game = room

    if not the_game:
        create_a_room(sock, preferences)
    else:
        if not join_game(sock, the_game):
            print('RETRY')
            quick_game(sock, preferences)


def choose_a_room(sock):
    """
    this function is responsible for sending all the games to the client
    :param sock:
    :return:
    """
    message = 'GAMES~'
    for room in AVAILABLE_GAMES:
        message += str(room.num_room) + ',' + str(len(room.players)) + ',' + str(room.max_players) + '~'
    for room in QUICK_GAMES:
        message += str(room.num_room) + ',' + str(len(room.players)) + ',' + str(room.max_players) + '~'
    for room in ONLINE_GAMES:
        message += str(room.num_room) + ',' + str(len(room.players)) + ',' + str(room.max_players) + '~'
    message += '~~'
    SEND[sock].append(message)


def create_a_private_room(sock, num_players):
    """
    this function is responsible for creating a private room
    :param sock:
    :param num_players:
    :return:
    """
    room = game.Game(len(QUICK_GAMES) + len(ONLINE_GAMES) + len(AVAILABLE_GAMES), num_players, [])
    AVAILABLE_GAMES.append(room)
    print('CREATED PRIVATE ROOM:{} MAX{}'.format(room.num_room, room.max_players))
    join_private_game(sock, room)


def create_a_room(sock, num_players):
    """
    this function is responsible for creating a room
    :param sock:
    :param num_players:
    :return:
    """
    room = game.Game(len(QUICK_GAMES) + len(ONLINE_GAMES) + len(AVAILABLE_GAMES), num_players, [])
    QUICK_GAMES.append(room)
    print('CREATED ROOM:{} MAX:{}'.format(room.num_room, room.max_players))
    join_game(sock, room)
    print('ROOM: {} MAX: {} HAVE_NOW: {}'.format(room.num_room, room.max_players, len(room.players)))


def join_private_game(sock, room):
    """
    this function is responsible for joining a private room
    :param sock:
    :param room:
    :return: if joined: True, if not joined: False.
    """
    # print 'num_room: ' + str(room.num_room)

    if room and room.max_players == len(room.players):
        AVAILABLE_GAMES.remove(room)
        ONLINE_GAMES.append(room)
        return False
    if room and sock not in room.players:
        room.add_player(sock)

    for player in room.players:
        SEND[player].append(
            'UPDATE' + '~' + str(room.num_room) + ',' + str(
                len(room.players)) + ',' + str(
                room.max_players) + '~~~')

    if room.max_players == len(room.players) and not room.started:
        room.start_game()
    while not room.finished:
        try:
            if SEND[sock]:
                send_with_size(sock, SEND[sock].pop(0))
            if sock in room.send_dict:
                if room.send_dict[sock]:
                    message = room.send_dict[sock].pop(0)
                    send_with_size(sock, message)
                    if 'GAME~FINISH~' in message:
                        room.finished = True
            if not room.max_players == len(room.players):
                time.sleep(1)
            data = recv_by_size(sock)
            if not data:
                raise socket.error
            receive_handler_thread = threading.Thread(target=receive_game_handler, args=(sock, data, room,))
            receive_handler_thread.start()
            THREAD.append(receive_handler_thread)

        except socket.timeout:
            continue

        except socket.error:
            room.remove_player(sock)
            if not room.started:
                del_player_from_waiting(sock)

    if room in ONLINE_GAMES:
        ONLINE_GAMES.remove(room)
    elif room in AVAILABLE_GAMES:
        AVAILABLE_GAMES.remove(room)

    return True


def join_game(sock, room):
    """
    this function is responsible for joining a room (game)
    :param sock:
    :param room:
    :return: if joined: True, if not joined: False.
    """
    # print 'num_room: ' + str(room.num_room)

    if room.max_players == len(room.players):
        QUICK_GAMES.remove(room)
        ONLINE_GAMES.append(room)
        return False
    if sock not in room.players:
        room.add_player(sock)

    for player in room.players:
        SEND[player].append(
            'UPDATE' + '~' + str(room.num_room) + ',' + str(
                len(room.players)) + ',' + str(
                room.max_players) + '~~~')

    if room.max_players == len(room.players) and not room.started:
        room.start_game()
    finished = False
    while not finished:
        try:
            if SEND[sock]:
                send_with_size(sock, SEND[sock].pop(0))
            if sock in room.send_dict:
                if room.send_dict[sock]:
                    message = room.send_dict[sock].pop(0)
                    send_with_size(sock, message)
                    if 'GAME~FINISH~' in message:
                        finished = True
            if not room.max_players == len(room.players):
                time.sleep(1)
            data = recv_by_size(sock)
            if not data:
                raise socket.error
            receive_handler_thread = threading.Thread(target=receive_game_handler, args=(sock, data, room,))
            receive_handler_thread.start()
            THREAD.append(receive_handler_thread)

        except socket.timeout:
            continue

        except socket.error:
            room.remove_player(sock)
            if not room.started:
                del_player_from_waiting(sock)

    if room in ONLINE_GAMES:
        ONLINE_GAMES.remove(room)
    elif room in QUICK_GAMES:
        QUICK_GAMES.remove(room)

    return True


def receive_game_handler(sock, receive, room):
    """
    this function is responsible for handling game receives
    :param sock:
    :param receive:
    :param room:
    :return: None
    """
    receive = receive[:-2]
    message = receive.split('~')
    if message[0].upper() == 'GAME' and len(message) > 2:
        if message[1].upper() == 'THROW':
            if len(message[2]) > 1:
                cards = message[2]
                cards_lst = cards.split('|')
                card_lst = []
                for card in cards_lst:
                    if card != '':
                        card = card.split(',')
                        num_card = int(card[0])
                        shape_card = int(card[1])
                        card_lst.append((num_card, shape_card))
                to_who = 0
                if message[3] != '':
                    to_who = int(message[3])
                room.throw(sock, card_lst, to_who)
            else:
                to_who = 0
                if message[2] != '':
                    to_who = int(message[2])
                room.throw(sock, [], to_who)
        elif message[1].upper() == 'TAKE_DECK_TO_HAND':
            room.take_deck(sock)


def find_room_by_num_room(num_room):
    """
    this function is responsible for finding a room by the number of the room
    :param num_room:
    :return:
    """
    for room in QUICK_GAMES:
        if room.num_room == num_room:
            return room

    for room in AVAILABLE_GAMES:
        if room.num_room == num_room:
            return room

    print('false')


def del_player_from_waiting(sock):
    """
    this function is responsible for deleting a player from a room and if the room gets empty also the room
    :param sock:
    :return:
    """
    found = False
    for room in QUICK_GAMES:
        if sock in room.players:
            room.players.remove(sock)
            if len(room.players) == 0:
                QUICK_GAMES.remove(room)
            found = True
            break

    if not found:
        for room in AVAILABLE_GAMES:
            if sock in room.players:
                room.players.remove(sock)
                if len(room.players) == 0:
                    AVAILABLE_GAMES.remove(room)
                found = True
                break

    return found


def async_send_receive(sock):
    """
    this function is responsible for the sending and receiving with the client
    :param sock: the client's socket :type socket._socketobject
    :return: None
    """
    while True:
        try:
            try:
                if SEND[sock]:
                    send_with_size(sock, SEND[sock].pop(0))
                data = recv_by_size(sock)
                if not data:
                    raise socket.error
                receive_handler(sock, data)

            except socket.timeout:
                continue
        except socket.error:
            print('disconnecting player')
            del_player_from_waiting(sock)
            SEND.pop(sock, None)
            break


def receive_handler(sock, recv):
    """
    this function is responsible for handeling with the received messages and adding messages to the SEND by the
    protocol.
    :param  :type
    :return:
    """
    recv = recv[:-2]
    message = recv.split('~')
    if message[0].upper() == 'QUICK_GAME' and len(message) == 3:
        quick_game(sock, int(message[1]))
    elif message[0].upper() == 'SCREEN' and len(message) > 2:
        if message[1].upper() == 'CHOOSE_A_ROOM':
            choose_a_room(sock)
        elif message[1].upper() == 'CREATE_A_ROOM':
            create_a_private_room(sock, int(message[2]))
    elif message[0].upper() == 'JOIN' and len(message) > 2:
        room = find_room_by_num_room(int(message[1]))
        if room in QUICK_GAMES:
            join_game(sock, room)
        elif room in AVAILABLE_GAMES:
            join_private_game(sock, room)


if __name__ == '__main__':
    main()
