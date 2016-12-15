import pika
import uuid
from random import randint
import math
import time
import signal
import threading

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

def nonBlockingRawInput(prompt='', timeout=30):
    signal.signal(signal.SIGALRM, alarmHandler)
    signal.alarm(timeout)
    try:
        text = raw_input(prompt)
        signal.alarm(0)
        return text
    except AlarmException:
        print '\nYou are out of time'
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return 'No Input!'

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
        self.enemy_battlefield = None
        self.rpc_queue = 'rpc_queue'
        self.state = 'not connected'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue


        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def getState(self, ch, method, properties, body):
        self.state = body

    def stringToList(self,string_to_parse):
        temp_list = string_to_parse.split(';')[:-1]
        coords = []
        for value in temp_list:
            value = value[1:-1]
            x, y = value.split(',')
            coords.append((int(x), int(y)))
        return coords

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

    def returnEnemyBattlefield(self):
        main_str = "    "
        for num in range(len(self.enemy_battlefield)):
            if num < 10:
                main_str += (" %s  ") % (num + 1)
            else:
                main_str += ("%s  ") % (num + 1)

        main_str += "\n"
        counter = 1
        for row in self.enemy_battlefield:
            if counter < 10:
                str = "%s. |" % counter
            else:
                str = "%s.|" % counter
            for elem in row:
                if elem == 0:
                    str_el = " "
                elif elem == 1:
                    str_el = "$"
                elif elem == 2:
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

    def StringToBattelfield(self,stringBattle,field_size):
        self.fieldSize = field_size
        self.enemy_battlefield = self.createBattlefield(self.fieldSize)
        self.battlefield = self.createBattlefield(self.fieldSize)
        battlefield = []
        i = 0
        while i < len(stringBattle):
            x = []
            for j in range(len(self.battlefield)):

                x.append(int(stringBattle[i + j]))
            i += len(self.battlefield)
            battlefield.append(x)
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

    def callSendBattlefield(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        bat = self.BattlefieldToString()
        request = '04_' + self.name + ',' + bat
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

    def callCheckGame(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '05_' + self.name
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

    def callEndGame(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '06_' + self.name
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

    def callShoot(self, x, y):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '07_' + self.name + '.' + str(x) + ',' + str(y)
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

    def callCheckTurn(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '08_' + self.name
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

    def callInfo(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '09_' + self.name
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

    def callUserState(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '10_' + self.name
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

    def callBattlefield(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '11_' + self.name
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

    def callNextPlayer(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '12_' + self.name
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

    def callWin(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '13_' + self.name
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

    def callSpectator(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        request = '14_' + self.name
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
    while True:
        time.sleep(2)
        #print user.state

        #####################################################################################################

        if user.state == 'not connected':
            while True:
                nickname = raw_input("Enter your nickname: ")
                user.name = nickname
                user.channel.queue_declare(queue=user.name)
                user.channel.basic_consume(user.getState,
                                           queue=user.name,
                                           no_ack=True)
                user.state = user.callUserState()
                print user.state
                if user.state == 'not connected':
                    print " [x] Requesting NAME"
                    response = user.callName(nickname)
                    if response == 'Wrong NAME':
                        print 'This name already exists!'
                        continue
                    if response == 'OK':
                        print 'Congratulations!'
                        break
                else:
                    break

        #####################################################################################################
        if user.state == 'connected':
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

        if user.state == 'joined':
            battlefieldServer = user.callBattlefield()
            battlefieldS, game_size = battlefieldServer.split(',')
            user.fieldSize = int(game_size)
            user.battlefield = user.createBattlefield(user.fieldSize)
            fleet = Fleet(user.fieldSize)
            while True:
                boats = fleet.checkFullfil()
                if boats == (0, 0, 0, 0):
                    break
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
                                # print "I generate %d, %d of dir %d" % (x, y, direction)
                                if num_ships_by_type[1] == 1:
                                    if checkAddedShip(x, y, num_ships_by_type[1], user.battlefield):
                                        fleet.addShip(Ship(num_ships_by_type[1], [(x, y)]))
                                        # print "I added ship of size %d with coord %s" % (num_ships_by_type[1], str([(x, y)]))
                                        user.addPlayersFleetOnBoard(fleet)
                                        break
                                    else:
                                        # print "No"
                                        continue
                                else:
                                    if direction == 0:
                                        if checkAddedShip(x, y, num_ships_by_type[1], user.battlefield, 'h'):
                                            list = []
                                            list.append((x, y))
                                            for i in range(1, num_ships_by_type[1]):
                                                list.append((x, y + i))
                                            fleet.addShip(Ship(num_ships_by_type[1], list))
                                            # print "I added ship of size %d with coord %s" % (num_ships_by_type[1], str(list))
                                            user.addPlayersFleetOnBoard(fleet)
                                            break
                                        else:
                                            # print "No"
                                            continue
                                    else:
                                        if checkAddedShip(x, y, num_ships_by_type[1], user.battlefield, 'v'):
                                            list = []
                                            list.append((x, y))
                                            for i in range(1, num_ships_by_type[1]):
                                                list.append((x + i, y))
                                            fleet.addShip(Ship(num_ships_by_type[1], list))
                                            # print "I added ship of size %d with coord %s" % (num_ships_by_type[1], str(list))
                                            user.addPlayersFleetOnBoard(fleet)
                                            break
                                        else:
                                            # print "No"
                                            continue
                    user.addPlayersFleetOnBoard(fleet)
                    user.enemy_battlefield = user.createBattlefield(user.fieldSize)
                    response = user.callSendBattlefield()
                    if response == 'OK!':
                        print user.returnBattlefield()
                        break
                    else:
                        print 'Connection problem!'
                        continue

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
                            user.enemy_battlefield = user.createBattlefield(user.fieldSize)
                            response = user.callSendBattlefield()
                            if response == 'OK!':
                                print user.returnBattlefield()
                                break
                            else:
                                print 'Connection problem!'
                                continue
                else:
                    "Dyrak chtoli?"
                    continue

        if user.state == 'wait for game start':

            while True:
                response = user.callCheckGame()
                if response == 'OK!':
                    break

        if user.state == 'your turn':
            response = user.callWin()
            if response == 'not':
                if user.fieldSize == 0:
                    battlefieldServer = user.callBattlefield()
                    battlefieldS, game_size = battlefieldServer.split(',')
                    #print user.battlefield
                    user.battlefield = user.StringToBattelfield(battlefieldS,int(game_size))
                response = 'HIT'
                yourbattlefield = user.callInfo()
                your, another = yourbattlefield.split('|')
                if your != 'empty':
                    your_list = user.stringToList(your)
                    for coord in your_list:
                        user.battlefield[coord[0]][coord[1]] = 2
                if another:
                    another_list = user.stringToList(another)
                    for coord in another_list:
                        user.enemy_battlefield[coord[0]][coord[1]] = 1
                end = True
                for row in user.battlefield:
                    for elem in row:
                        if elem == 1:
                            end = False
                print end
                print user.battlefield
                if end == True:
                    response = user.callEndGame()
                elif end == False:
                    while response == 'HIT':
                        print 'Now your battlefield looks like this:'
                        print user.returnBattlefield()
                        print 'Enemies battlefield looks like this:'
                        print user.returnEnemyBattlefield()
                        #choice = raw_input('Enter coordinates (x,y) or "EXIT" to end your game:')
                        choice = nonBlockingRawInput('You have 30 sec to Enter coordinates (x,y) or "EXIT" to end your game:')
                        if choice == 'EXIT':
                            response = user.callEndGame()
                            break
                        if choice != 'No Input!':
                            try:
                                x, y = choice.split(',')
                                x, y = int(x) - 1, int(y) - 1
                                if 0 <= x < user.fieldSize and 0 <= y < user.fieldSize:
                                    response = user.callShoot(x, y)
                                    if response == 'miss':
                                        user.enemy_battlefield[x][y] = 2
                                        print user.returnEnemyBattlefield()
                                        print "You have missed."
                                        break
                                    else:
                                        response, output = response.split('_')
                                        playername_list = output.split(',')[:-1]
                                        for playername in playername_list:
                                            print "You have hit %s" % playername
                                        user.enemy_battlefield[x][y] = 1
                                else:
                                    print 'Wrong input coordinates! Try again!'
                                    continue
                            except ValueError:
                                pass

                        else:
                            print 'KUKU'
                            response = user.callNextPlayer()
                            print response
                            if response == 'miss':
                                user.state = 'not your turn'
                                break
                            else:
                                print 'connection problem'
            elif response == 'win':
                user.state = 'win'

        if user.state == 'not your turn':
            while True:
                response = user.callCheckTurn()
                if response == 'OK!':
                    break

        if user.state == 'game over':
            choice = raw_input("Do you want to spectate or exit? (y/n)")
            if choice == 'y':
                while True:
                    time.sleep(40)
                    allBattlefields = user.callSpectator()
                    list_battlefields = allBattlefields.split(';')
                    for bfield in list_battlefields:
                        user.battlefield = user.StringToBattelfield(bfield, user.fieldSize)
                        print 'Your enemies fields:'
                        print user.returnBattlefield()

            else:
                print "Good bye."

        if user.state == 'win':
            print "You are winner."





            #########################____RPC____END_____####################################
