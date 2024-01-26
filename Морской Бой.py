#Не знаю, можно ли было сделать короче, но сделал так.
#А еще вопрос, можно ли было сделать это без библиотеку. Все, что касаемо их, нашел в интернете, потому что тут
#не понимал, как куда и что, если без них.



import os
from random import randrange
from random import choice


class boardPart(object):
    main = 'map'
    radar = 'radar'
    weight = 'weight'


def text_in_dot(text):
    return text

class Dot(object):
    empty_dot = text_in_dot(' ')
    ship_dot = text_in_dot('■')
    destroyed_ship_dot = text_in_dot('X')
    damaged_ship_dot = text_in_dot('□')
    miss_dot = text_in_dot('•')

class Board(object):

    def __init__(self, size):
        self.size = size
        self.map = [[Dot.empty_dot for _ in range(size)] for _ in range(size)]
        self.radar = [[Dot.empty_dot for _ in range(size)] for _ in range(size)]
        self.weight = [[1 for _ in range(size)] for _ in range(size)]

    def get_board_part(self, element):
        if element == boardPart.main:
            return self.map
        if element == boardPart.radar:
            return self.radar
        if element == boardPart.weight:
            return self.weight

    def draw_board(self, element):

        board = self.get_board_part(element)
        weights = self.get_max_weight_cells()

        if element == boardPart.weight:
            for x in range(self.size):
                for y in range(self.size):
                    if (x, y) in weights:
                        print('\033[1;32m', end='')
                    if board[x][y] < self.size:
                        print(" ", end='')
                    if board[x][y] == 0:
                        print(str("" + ". " + ""), end='')
                    else:
                        print(str("" + str(board[x][y]) + " "), end='')
                    print('\033[0;0m', end='')
                print()

        else:
            for x in range(-1, self.size):
                for y in range(-1, self.size):
                    if x == -1 and y == -1:
                        print("  ", end="")
                        continue
                    if x == -1 and y >= 0:
                        print(y + 1, end=" ")
                        continue
                    if x >= 0 and y == -1:
                        print(Game.letters[x], end='')
                        continue
                    print(" " + str(board[x][y]), end='')
                print("")
        print("")


    def check_ship_fits(self, ship, element):

        board = self.get_board_part(element)

        if ship.x + ship.height - 1 >= self.size or ship.x < 0 or \
                ship.y + ship.width - 1 >= self.size or ship.y < 0:
            return False

        x = ship.x
        y = ship.y
        width = ship.width
        height = ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                if str(board[p_x][p_y]) == Dot.miss_dot:
                    return False

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(board) or p_y < 0 or p_y >= len(board):
                    continue
                if str(board[p_x][p_y]) in (Dot.ship_dot, Dot.destroyed_ship_dot):
                    return False

        return True

    def mark_destroyed_ship(self, ship, element):

        board = self.get_board_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(board) or p_y < 0 or p_y >= len(board):
                    continue
                board[p_x][p_y] = Dot.miss_dot

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                board[p_x][p_y] = Dot.destroyed_ship_dot

    def add_ship_to_board(self, ship, element):

        board = self.get_board_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                board[p_x][p_y] = ship

    def get_max_weight_cells(self):
        weights = {}
        max_weight = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.weight[x][y] > max_weight:
                    max_weight = self.weight[x][y]
                weights.setdefault(self.weight[x][y], []).append((x, y))

        return weights[max_weight]

    def recalculate_weight_map(self, available_ships):
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]
        for x in range(self.size):
            for y in range(self.size):
                if self.radar[x][y] == Dot.damaged_ship_dot:

                    self.weight[x][y] = 0

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.weight[x - 1][y - 1] = 0
                        self.weight[x - 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x - 1][y + 1] = 0

                    if y - 1 >= 0:
                        self.weight[x][y - 1] *= 50
                    if y + 1 < self.size:
                        self.weight[x][y + 1] *= 50

                    if x + 1 < self.size:
                        if y - 1 >= 0:
                            self.weight[x + 1][y - 1] = 0
                        self.weight[x + 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x + 1][y + 1] = 0
        for ship_size in available_ships:

            ship = Ship(ship_size, 1, 1, 0)
            for x in range(self.size):
                for y in range(self.size):
                    if self.radar[x][y] in (Dot.destroyed_ship_dot, Dot.damaged_ship_dot, Dot.miss_dot) \
                            or self.weight[x][y] == 0:
                        self.weight[x][y] = 0
                        continue
                    for rotation in range(0, 4):
                        ship.set_position(x, y, rotation)
                        if self.check_ship_fits(ship, boardPart.radar):
                            self.weight[x][y] += 1

class Game(object):
    letters = ("1", "2", "3", "4", "5", "6")
    ships_rules = [1, 1, 1, 2, 2, 3]
    board_size = len(letters)

    def __init__(self):

        self.players = []
        self.current_player = None
        self.next_player = None

        self.status = 'prepare'

    def start_game(self):

        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def status_check(self):
        if self.status == 'prepare' and len(self.players) >= 2:
            self.status = 'in game'
            self.start_game()
            return True
        if self.status == 'in game' and len(self.next_player.ships) == 0:
            self.status = 'game over'
            return True

    def add_player(self, player):
        player.board = Board(Game.board_size)
        player.enemy_ships = list(Game.ships_rules)
        self.ships_setup(player)
        player.board.recalculate_weight_map(player.enemy_ships)
        self.players.append(player)

    def ships_setup(self, player):
        for ship_size in Game.ships_rules:
            retry_count = 30

            ship = Ship(ship_size, 0, 0, 0)

            while True:

                Game.clear_screen()
                if player.auto_ship_setup is not True:
                    player.board.draw_board(boardPart.main)
                    player.message.append('Куда поставить {} корабль: '.format(ship_size))
                    for _ in player.message:
                        print(_)
                else:
                    print('{}. Расставляем корабли'.format(player.name))

                player.message.clear()

                x, y, r = player.get_input('ship_setup')
                if x + y + r == 0:
                    continue

                ship.set_position(x, y, r)
                if player.board.check_ship_fits(ship, boardPart.main):
                    player.board.add_ship_to_board(ship, boardPart.main)
                    player.ships.append(ship)
                    break
                player.message.append('Неправильная позиция!')
                retry_count -= 1
                if retry_count < 0:

                    player.board.map = [[Dot.empty_dot for _ in range(Game.board_size)] for _ in
                                        range(Game.board_size)]
                    player.ships = []
                    self.ships_setup(player)
                    return True

    def draw(self):
        if not self.current_player.is_ai:
            self.current_player.board.draw_board(boardPart.main)
            self.current_player.board.draw_board(boardPart.radar)
        for line in self.current_player.message:
            print(line)

    def switch_players(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')


class Player(object):

    def __init__(self, name, is_ai, skill, auto_ship):
        self.name = name
        self.is_ai = is_ai
        self.auto_ship_setup = auto_ship
        self.skill = skill
        self.message = []
        self.ships = []
        self.enemy_ships = []
        self.board = None

    def get_input(self, input_type):

        if input_type == "ship_setup":

            if self.is_ai or self.auto_ship_setup:
                user_input = str(choice(Game.letters)) + str(randrange(0, self.board.size)) + choice(["H", "V"])
            else:
                user_input = input().upper().replace(" ", "")

            if len(user_input) < 3:
                return 0, 0, 0

            x, y, r = user_input[0], user_input[1:-1], user_input[-1]

            if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.board_size + 1) or \
                    r not in ("H", "V"):
                self.message.append('Неправильнно введены координаты')
                return 0, 0, 0

            return Game.letters.index(x), int(y) - 1, 0 if r == 'H' else 1

        if input_type == "shot":

            if self.is_ai:
                if self.skill == 1:
                    x, y = choice(self.board.get_max_weight_cells())
                if self.skill == 0:
                    x, y = randrange(0, self.board.size), randrange(0, self.board.size)
            else:
                user_input = input().upper().replace(" ", "")
                x, y = user_input[0].upper(), user_input[1:]
                if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.board_size + 1):
                    self.message.append('Неправильно введены координаты')
                    return 500, 0
                x = Game.letters.index(x)
                y = int(y) - 1
            return x, y

    def make_shot(self, target_player):

        sx, sy = self.get_input('shot')

        if sx + sy == 500 or self.board.radar[sx][sy] != Dot.empty_dot:
            return 'retry'
        shot_res = target_player.receive_shot((sx, sy))

        if shot_res == 'miss':
            self.board.radar[sx][sy] = Dot.miss_dot

        if shot_res == 'get':
            self.board.radar[sx][sy] = Dot.damaged_ship_dot

        if type(shot_res) == Ship:
            destroyed_ship = shot_res
            self.board.mark_destroyed_ship(destroyed_ship, boardPart.radar)
            self.enemy_ships.remove(destroyed_ship.size)
            shot_res = 'kill'

        self.board.recalculate_weight_map(self.enemy_ships)

        return shot_res

    def receive_shot(self, shot):

        sx, sy = shot

        if type(self.board.map[sx][sy]) == Ship:
            ship = self.board.map[sx][sy]
            ship.hp -= 1

            if ship.hp <= 0:
                self.board.mark_destroyed_ship(ship, boardPart.main)
                self.ships.remove(ship)
                return ship

            self.board.map[sx][sy] = Dot.damaged_ship_dot
            return 'get'

        else:
            self.board.map[sx][sy] = Dot.miss_dot
            return 'miss'


class Ship:

    def __init__(self, size, x, y, rotation):

        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def __str__(self):
        return Dot.ship_dot

    def set_position(self, x, y, r):
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):

        self.rotation = r

        if self.rotation == 0:
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:
            self.width = 1
            self.height = self.size
        elif self.rotation == 2:
            self.y = self.y - self.size + 1
            self.width = self.size
            self.height = 1
        elif self.rotation == 3:
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size


if __name__ == '__main__':

    players = []
    players.append(Player(name=input("Введите имя: "), is_ai=False, auto_ship=True, skill=1))
    players.append(Player(name='Компьютер', is_ai=True, auto_ship=True, skill=1))

    game = Game()

    while True:
        game.status_check()

        if game.status == 'prepare':
            game.add_player(players.pop(0))

        if game.status == 'in game':
            Game.clear_screen()
            game.current_player.message.append("Выстрел: ")
            game.draw()
            game.current_player.message.clear()
            shot_result = game.current_player.make_shot(game.next_player)
            if shot_result == 'miss':
                game.next_player.message.append('{} промахнулся '.format(game.current_player.name))
                game.next_player.message.append('{}'.format(game.next_player.name))
                game.switch_players()
                continue
            elif shot_result == 'retry':
                game.current_player.message.append('Координаты уже были')
                continue
            elif shot_result == 'get':
                game.current_player.message.append('Попадание. Еще один ход')
                continue
            elif shot_result == 'kill':
                game.current_player.message.append('Корабль противника уничтожен')
                game.next_player.message.append('Ваш корабль уничтожен :(')
                continue

        if game.status == 'game over':
            Game.clear_screen()
            game.next_player.board.draw_board(boardPart.main)
            game.current_player.board.draw_board(boardPart.main)
            print('{} победил'.format(game.current_player.name))
            break

