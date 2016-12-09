from server import *

min_field_size = 10
max_field_size = 40
list_of_servers = ["server#1"]



if __name__ == "__main__":
    print "Hello! Welcome to the Battleship Game."
    print "What server would you like to join?"
    numb = 1
    for server in list_of_servers:
        print "%d. "%numb + server
        numb += 1
    server_number = raw_input()
    #!!! Connection !!!#
    server = Server()
    ####################
    while True:
        nickname = raw_input("Enter your nickname: ")
        if nickname not in server.player_nicknames_list:
            print "User with such nickname already exists. Please enter another nickname."
        else:
            server.player_nicknames_list.append(nickname)
            break

    while True:
        if server.getGamesList():
            print "What would you like to do?"
            print "1. Create new game."
            print "2. Enter existing game."
            choice = raw_input()
        else:
            choice = 1
        if choice == 1:
            print "To create a new game, You need to enter the field size you want to play on."
            size = 0
            while True:
                print "Notice that field size should be between %d and %d."%(min_field_size,max_field_size)
                size = raw_input("Field size: ")
                if  min_field_size <= size <= max_field_size:
                    break
                else:
                    print "You have entered field size that is out of bounds. Please try again."
            #Creation of new game
            server.createGame(size)

        elif choice == 2:
            print "What game would you like to join?"
            while True:
                print server.getGamesList()
                game_number = raw_input("Your choice: ")
                if  0 <= game_number < len(server.getGamesList()):
                    break
                else:
                    print "There is no such option. Please try again."
        else:
            print "There is no such option. Please enter again."