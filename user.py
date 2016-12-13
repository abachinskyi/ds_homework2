import pika
import uuid
from random import randint
import math


#########################____RPC____START_____#################################

class Fleet:
    def __init__(self, game_field_size):
        # !!!!!!!!!!! wrong, change with formula!!!
        self.size = game_field_size
        self.patrol_boat_list = []
        self.destroyer_list = []
        self.submarine_list = []
        self.carrier_list = []
        for i in range(int(math.floor(0.4 * self.size))):
            self.patrol_boat_list.append(None)
        for i in range(int(math.floor(0.3 * self.size))):
            self.destroyer_list.append(None)
        for i in range(int(math.floor(0.2 * self.size))):
            self.submarine_list.append(None)
        for i in range(int(math.floor(0.1 * self.size))):
            self.carrier_list.append(None)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def addShip(self, ship):
        pb, d, s, c = self.checkFullfil()
        if ship.size == 1:
            self.patrol_boat_list[pb - 1] = ship
        elif ship.size == 2:
            self.destroyer_list[d - 1] = ship
        elif ship.size == 3:
            self.submarine_list[s - 1] = ship
        elif ship.size == 4:
            self.carrier_list[c - 1] = ship

    def checkFullfil(self):
        pb = 0
        d = 0
        s = 0
        c = 0
        for elem in self.patrol_boat_list:
            if not elem:
                pb += 1
        for elem in self.destroyer_list:
            if not elem:
                d += 1
        for elem in self.submarine_list:
            if not elem:
                s += 1
        for elem in self.carrier_list:
            if not elem:
                c += 1
        return pb, d, s, c

    def getNumberOfShips(self, type="All"):
        if type == "All":
            return len(self.patrol_boat_list) + len(self.destroyer_list) + len(self.submarine_list) + len(
                self.carrier_list)
        elif type == "PatrolBoat":
            return len(self.patrol_boat_list)
        elif type == "Destroyer":
            return len(self.destroyer_list)
        elif type == "Submarine":
            return len(self.submarine_list)
        elif type == "Carrier":
            return len(self.carrier_list)
        else:
            raise NameError("There is no such type")


class Ship:
    def __init__(self, ship_size, list_coord):
        self.size = ship_size
        if self.size == 1:
            self.name = "PatrolBoat"
        elif self.size == 2:
            self.name = "Destroyer"
        elif self.size == 3:
            self.name = "Submarine"
        elif self.size == 4:
            self.name = "Carrier"
        else:
            raise NameError("Ship size is out of bounds")

        if len(list_coord) == ship_size:
            self.list_coordinates = list_coord
        else:
            raise NameError("The number of coordinates does not correspond to size of a ship")


class User(object):
    def __init__(self):
        self.name = ''
        self.fieldSize = 0
        self.battlefield = None
        self.rpc_queue = 'rpc_queue'
        self.state = ''
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='user_state')

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue


        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

        self.channel.basic_consume(self.getState,
                                   queue='user_state',
                                   no_ack=True)

    def getState(self, ch, method, properties, body):
        self.state = body

    def BattlefieldToString(self):
        string = ''
        for i in self.battlefield:
            for j in i:
                string += str(j)
        return string

    def returnBattlefield(self):
        main_str = "    "
        for num in range(len(self.battlefield)):
            if num < 10:
                main_str += (" %s  ") % (num + 1)
            else:
                main_str += ("%s  ") % (num + 1)

        main_str += "\n"
        counter = 1
        for row in self.battlefield:
            if counter < 10:
                str = "%s. |" % counter
            else:
                str = "%s.|" % counter
            for elem in row:
                if elem == 0:
                    str_el = " "
                elif elem == 1:
                    str_el = "#"
                elif elem == 2:
                    str_el = "$"
                elif elem == 3:
                    str_el = "*"
                str += " %s |" % str_el
            counter += 1
            main_str += str
            main_str += "\n"
            main_str += "____" * (len(self.battlefield) + 1)
            main_str += "\n"
        return main_str

    def createBattlefield(self, game_field_size):
        battlefield = []
        for i in range(game_field_size):
            battlefield.append([])
            for j in range(game_field_size):
                battlefield[i].append(0)
        return battlefield

    def addPlayersFleetOnBoard(self, fleet):
        self.fleet = fleet
        for ship_list_by_type in [fleet.patrol_boat_list, fleet.destroyer_list, fleet.submarine_list,
                                  fleet.carrier_list]:
            for ship in ship_list_by_type:
                if ship:
                    for coordinates in ship.list_coordinates:
                        self.battlefield[coordinates[0]][coordinates[1]] = 1

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def callGameList(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '01_'
        self.channel.basic_publish(exchange='',
                                   routing_key=self.rpc_queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(request))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def callNewGame(self, fieldSize, numPlayers):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '02_' + fieldSize + ',' + numPlayers + '.' + self.name
        self.channel.basic_publish(exchange='',
                                   routing_key=self.rpc_queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(request))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def callName(self, name):
        self.channel.queue_declare(queue=name)
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '00_' + name
        self.channel.basic_publish(exchange='',
                                   routing_key=self.rpc_queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(request))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def callEnterGame(self, Pname, Gnumber):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '03_' + Pname + ',' + Gnumber
        self.channel.basic_publish(exchange='',
                                   routing_key=self.rpc_queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(request))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


#########################____RPC____END_____####################################

min_field_size = 10
max_field_size = 40
list_of_servers = ["server#1"]


def checkNear(x, y, battlefield):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if 0 <= x + i < len(battlefield) and 0 <= y + j < len(battlefield):
                if battlefield[x + i][y + j] == 1:
                    return False
    return True


def checkAddedShip(x, y, ship_size, battlefield, direction=''):
    if ship_size == 1:
        if not checkNear(x, y, battlefield):
            return False
    elif ((direction == 'v') and ((x + ship_size) > len(battlefield))) or (
        (direction == 'h') and ((y + ship_size) > len(battlefield))):
        return False
    elif (direction == 'v') and ((x + ship_size - 1) <= len(battlefield)):
        for i in range(ship_size):
            if not checkNear(x + i, y, battlefield):
                return False
    elif (direction == 'h') and ((y + ship_size - 1) <= len(battlefield)):
        for i in range(ship_size):
            if not checkNear(x, y + i, battlefield):
                return False
    return True


if __name__ == "__main__":

#########################____RPC____START_____#################################

    user = User()
    print "Hello! Welcome to the Battleship Game."
    print "What server would you like to join?"

#####################################################################################################

    while True:
        nickname = raw_input("Enter your nickname: ")
        user.name = nickname
        print " [x] Requesting NAME"
        response = user.callName(nickname)
        print user.state
        if response == 'Wrong NAME':
            print 'This name already exists!'
            continue
        if response == 'OK':
            print 'Congratulations!'
            break

#####################################################################################################

    while True:
        gameList = user.callGameList()
        if gameList:
            while True:
                print "What would you like to do?"
                print "1. Create new game."
                print "2. Enter existing game."
                choice = int(raw_input('Your choice:'))
                if choice == 1 or choice == 2:
                    break
                else:
                    print 'Wrong decision!'
                    continue
        else:
            choice = 1

#####################################################################################################

        if choice == 1:
            print "To create a new game, You need to enter the field size you want to play on and number of players."
            while True:
                print "Notice that field size should be between %d and %d and number of players should be at least two." % (
                min_field_size, max_field_size)
                size_of_field = raw_input("Field size: ")
                user.fieldSize = int(size_of_field)
                number_of_players = raw_input('Number of players:')
                if min_field_size <= int(size_of_field) <= max_field_size and int(number_of_players) >= 2:
                    pass
                else:
                    print "You have entered field size that is out of bounds or wrong number of players. Please try again."
                    continue
                    # Creation of new game
                response = user.callNewGame(size_of_field, number_of_players)
                if response == 'OK!':
                    print 'The Game has been created!'
                    break
                else:
                    print 'Connection problem. Try again!'
                    continue
            break

#####################################################################################################

        elif choice == 2:
            print "What game would you like to join?"
            while True:
                print gameList
                game_number = raw_input("Your choice: ")
                response = user.callEnterGame(user.name, game_number)
                if response:
                    user.fieldSize = int(response)
                    print 'You have joined The GAME!'
                    break
                else:
                    print "There is no such option. Please try again."
                    continue
            break
        else:
            print "There is no such option. Please enter again."
            continue

#####################################################################################################

    user.battlefield = user.createBattlefield(user.fieldSize)
    fleet = Fleet(user.fieldSize)
    while True:
        print "What would you like to do:"
        print "1. Generate random fleet."
        print "2. Create your own fleet."
        fleet_choice = raw_input("Your choice: ")
        if fleet_choice == "1":
            boats = fleet.checkFullfil()
            for num_ships_by_type in ((boats[3], 4), (boats[2], 3), (boats[1], 2), (boats[0], 1)):
                for ship in range(num_ships_by_type[0]):
                    while True:
                        x = randint(0, len(user.battlefield) - 1)
                        y = randint(0, len(user.battlefield) - 1)
                        direction = randint(0, 1)
                        #print "I generate %d, %d of dir %d" % (x, y, direction)
                        if num_ships_by_type[1] == 1:
                            if checkAddedShip(x, y, num_ships_by_type[1], user.battlefield):
                                fleet.addShip(Ship(num_ships_by_type[1], [(x, y)]))
                                #print "I added ship of size %d with coord %s" % (num_ships_by_type[1], str([(x, y)]))
                                user.addPlayersFleetOnBoard(fleet)
                                break
                            else:
                                #print "No"
                                continue
                        else:
                            if direction == 0:
                                if checkAddedShip(x, y, num_ships_by_type[1], user.battlefield, 'h'):
                                    list = []
                                    list.append((x, y))
                                    for i in range(1, num_ships_by_type[1]):
                                        list.append((x, y + i))
                                    fleet.addShip(Ship(num_ships_by_type[1], list))
                                    #print "I added ship of size %d with coord %s" % (num_ships_by_type[1], str(list))
                                    user.addPlayersFleetOnBoard(fleet)
                                    break
                                else:
                                    #print "No"
                                    continue
                            else:
                                if checkAddedShip(x, y, num_ships_by_type[1], user.battlefield, 'v'):
                                    list = []
                                    list.append((x, y))
                                    for i in range(1, num_ships_by_type[1]):
                                        list.append((x + i, y))
                                    fleet.addShip(Ship(num_ships_by_type[1], list))
                                    #print "I added ship of size %d with coord %s" % (num_ships_by_type[1], str(list))
                                    user.addPlayersFleetOnBoard(fleet)
                                    break
                                else:
                                    #print "No"
                                    continue
            user.addPlayersFleetOnBoard(fleet)
            print user.returnBattlefield()
            break

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
                        print 'Wrong option.'
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
                            print "Wrong option."
                            continue
                        if not checkAddedShip(x, y, size, user.battlefield, direction):
                            print "You can`t put ship in the place you want. Please take a look on battlefield."
                            continue
                    else:
                        if not checkAddedShip(x, y, size, user.battlefield):
                            print "You can`t put ship in the place you want. Please take a look on battlefield."
                            continue
                    fleet.addShip(Ship(size, list))
                    user.addPlayersFleetOnBoard(fleet)
                    print user.returnBattlefield()
        else:
            "Dyrak chtoli?"
            continue

    #########################____RPC____END_____####################################
