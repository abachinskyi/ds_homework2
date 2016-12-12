from server import *
from random import randint
#import pika
import uuid




#########################____RPC____START_____#################################
"""
class User(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)
"""
#########################____RPC____END_____####################################

min_field_size = 10
max_field_size = 40
list_of_servers = ["server#1"]


def checkNear(y,x,battlefield):
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if 0<=x+i<len(battlefield) and 0<=y+j<len(battlefield):
                if battlefield[x+i][y+j]==1:
                    return False
    return True

def checkAddedShip(y,x,ship_size,battlefield, direction = ''):
    if ship_size == 1:
        if not checkNear(x,y,battlefield):
            return False
    elif ((direction == 'v') and ((y+ship_size)>len(battlefield))) or ((direction == 'h') and ((x+ship_size)>len(battlefield))):
        return False
    elif (direction == 'v') and ((y+ship_size)<len(battlefield)):
        for i in range(ship_size):
            if not checkNear(x,y+i,battlefield):
                return False
    elif (direction == 'h') and ((x+ship_size)<len(battlefield)):
        for i in range(ship_size):
            if not checkNear(x+i,y,battlefield):
                return False
    return True

if __name__ == "__main__":

#########################____RPC____START_____#################################
#
#    user = User()
#    print " [x] Requesting fib(30)"
#    response = user.call(30)
#    print " [.] Got %r" % (response,)
#
#########################____RPC____END_____####################################

    print "Hello! Welcome to the Battleship Game."
    print "What server would you like to join?"
    numb = 1
    number_of_game = None
    for server in list_of_servers:
        print "%d. "%numb + server
        numb += 1
    server_number = raw_input()
    #!!! Connection !!!#
    server = Server()
    ####################
    while True:
        nickname = raw_input("Enter your nickname: ")
        if nickname in server.player_nicknames_list:
            print "User with such nickname already exists. Please enter another nickname."
        else:
            server.player_nicknames_list.append(nickname)
            break

    while True:
        if server.getGamesList():
            print "What would you like to do?"
            print "1. Create new game."
            print "2. Enter existing game."
            choice = int(raw_input())
        else:
            choice = 1
        if choice == 1:
            print "To create a new game, You need to enter the field size you want to play on."
            size = 0
            while True:
                print "Notice that field size should be between %d and %d." % (min_field_size, max_field_size)
                size = raw_input("Field size: ")
                if min_field_size <= int(size) <= max_field_size:
                    break
                else:
                    print "You have entered field size that is out of bounds. Please try again."
            #Creation of new game
            server.createGame(int(size))
            number_of_game = 0
            break

        elif choice == 2:
            print "What game would you like to join?"
            while True:
                print server.getGamesList()
                game_number = raw_input("Your choice: ")
                if 0 <= int(game_number) < len(server.getGamesList()):
                    number_of_game = int(game_number) - 1
                    break
                else:
                    print "There is no such option. Please try again."
            print game_number
        else:
            print "There is no such option. Please enter again."

    print "Game %s starts" % server.game_list[number_of_game].game_name
    player = Player(nickname,  server.game_list[number_of_game].size)
    print player.returnBattlefield()
    fleet = Fleet(server.game_list[number_of_game].size)
    while True:
        print "What would you like to do:"
        print "1. Generate random fleet."
        print "2. Create your own fleet."
        fleet_choice = raw_input("Your choice: ")
        if fleet_choice == "1":
            boats = fleet.checkFullfil()
            for num_ships_by_type in (boats[3], boats[2], boats[1]):
                for ship in range(num_ships_by_type):
                    while True:
                        x = randint(0,len(player.battlefield) - 1)
                        y = randint(0, len(player.battlefield) - 1)
                        direction = randint(0,1)
                        #if checkAddedShip(x,y,



        elif fleet_choice == "2":
            while True:
                boats = fleet.checkFullfil()
                if boats == (0, 0, 0, 0):
                    break
                else:
                    print "You need to enter more ships:"
                    if boats[0]:
                        print "1. Patrol boat: %d" % boats[0]
                    if boats[1]:
                        print "2. Destroyer: %d" % boats[1]
                    if boats[2]:
                        print "3. Submarine: %d" % boats[2]
                    if boats[3]:
                        print "4. Carrier: %d" % boats[3]
                    choice = raw_input("Choose option:")
                    if choice == '1' or choice == '2' or choice == '3' or choice == '4':
                        size = int(choice)
                        print size
                    else:
                        print 'TY DOLBOEB.'
                        continue
                    coords = raw_input('Enter top cootdinate of the ship: x,y: ')
                    x, y = coords.split(',')
                    x, y = int(x) - 1, int(y) - 1
                    list = []
                    list.append((x, y))
                    if size > 1:
                        direction = raw_input('Do you want to place ship horizontally (h) or vertically (v)')
                        if direction == 'h':
                            for i in range(1, size):
                                list.append((x, y + i))
                        elif direction == 'v':
                            for i in range(1, size):
                                list.append((x + i, y))
                        else:
                            print "Ty dolboyeb."
                            continue
                        if not checkAddedShip(x, y, size, player.battlefield, direction):
                            print "You can`t put ship in the place you want. Please take a look on battlefield."
                            continue
                    else:
                        if not checkAddedShip(x, y, size, player.battlefield):
                            print "You can`t put ship in the place you want. Please take a look on battlefield."
                            continue
                    fleet.addShip(Ship(size, list))
                    player.addPlayersFleetOnBoard(fleet)
                    print player.returnBattlefield()
        else:
            "Dyrak chtoli?"
            continue
    ##### Game starts #####
    while True:
        pass

