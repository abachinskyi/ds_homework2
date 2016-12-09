global _game_counter
_game_counter = 0

class Server:
    def __init__(self, name = "Default"):
        self.server_name = name
        self.game_list = []
        self.player_nicknames_list = []

    def getServerName(self):
        return self.server_name

    def getGamesList(self):
        str = ""
        counter = 1
        for game in self.game_list:
            str += "%d. "%counter + game.game_name + "\n"
            counter += 1
        return str

    #Creation of instances of other classes
    def createGame(self, field_size):
        game = Game(field_size)
        self.game_list.append(game)

    def createShip(self, ship_size, list_coord):
        return Ship(ship_size, list_coord)

    def createFleet(self, field_size):
        return Fleet(field_size)

    def createPlayer(self, nickname, fleet, field_size):
        return Player(nickname, fleet, field_size)


class Game:
    def __init__(self, field_size, name = ""):
        #size of field initialization
        self.size = field_size
        #name initialization
        if name:
            self.game_name = name
        else:
            global _game_counter
            self.game_name = "game#%d" % _game_counter
            _game_counter += 1
        #list of players initialization
        self.player_list = []

    def addPlayer(self, player):
        self.player_list.append(player)

    def getPlayerNicknames(self):
        list_nicknames = []
        for player in self.player_list:
            list_nicknames.append(player.getNickname())
        return list_nicknames

class Player:
    def __init__(self, nickname, fleet, game_field_size):
        self.nickname = nickname
        self.createBattlefield(game_field_size)
        self.createPlayersFleet(fleet)

    def getNickname(self):
        return self.nickname

    def _printBattlefield(self):
        for row in self.battlefield:
            print row

    def createBattlefield(self, game_field_size):
        self.battlefield = []
        for i in range(game_field_size):
            self.battlefield.append([])
            for j in range(game_field_size):
                self.battlefield[i].append(0)

    def createPlayersFleet(self, fleet):
        self.fleet = fleet
        for ship_list_by_type in [fleet.patrol_boat_list, fleet.destroyer_list, fleet.submarine_list, fleet.carrier_list]:
            for ship in ship_list_by_type:
                for coordinates in ship.list_coordinates:
                    self.battlefield[coordinates[1]][coordinates[0]] = 1


class Fleet:
    def __init__(self, game_field_size):
        #!!!!!!!!!!! wrong, change with formula!!!
        self.size = game_field_size
        self.patrol_boat_list = []
        self.destroyer_list = []
        self.submarine_list = []
        self.carrier_list = []
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def addShip(self, ship):
        if ship.size == 1:
            self.patrol_boat_list.append(ship)
        elif ship.size == 2:
            self.destroyer_list.append(ship)
        elif ship.size == 3:
            self.submarine_list.append(ship)
        elif ship.size == 4:
            self.carrier_list.append(ship)


    def getNumberOfShips(self, type = "All"):
        if type == "All":
            return len(self.patrol_boat_list) + len(self.destroyer_list) + len(self.submarine_list) + len(self.carrier_list)
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



if __name__ == "__main__":
    server = Server()
    #print server.getServerName()
    game1 = Game(5)
    game2 = Game(10)
    server.addGame(game1)
    server.addGame(game2)
    patrol_boat = Ship(1, [(0,0)])
    submarine = Ship(3, [(2, 3),(3,3),(4,3)])
    fleet = Fleet(game1.size)
    fleet.addShip(patrol_boat)
    fleet.addShip(submarine)
    print fleet.getNumberOfShips()
    player = Player('Dimas', fleet, game1.size)
    player._printBattlefield()
    game1.addPlayer(player)
    print game1.getPlayerNicknames()
    print server.getGamesList()