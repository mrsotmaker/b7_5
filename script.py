from random import choice
from random import shuffle

class Ship:

    def __init__(self, num_of_decks, board):
        self.cells = []

        free_cells = [(cell.row, cell.column) for cell in board.cells_by_status(Cell.States.empty)]
        non_free_cells = [(cell.row, cell.column) for cell in board.cells_by_status(Cell.States.deck_whole)]
        tmp_cells = []

        for cell in non_free_cells:
            tmp_cells.append((cell[0] + 1, cell[1]))
            tmp_cells.append((cell[0] - 1, cell[1]))
            tmp_cells.append((cell[0], cell[1] + 1))
            tmp_cells.append((cell[0], cell[1] - 1))
            tmp_cells.append((cell[0] + 1, cell[1] + 1))
            tmp_cells.append((cell[0] - 1, cell[1] - 1))
            tmp_cells.append((cell[0] + 1, cell[1] - 1))
            tmp_cells.append((cell[0] - 1, cell[1] + 1))

        non_free_cells += tmp_cells
        free_cells = list(set(free_cells).difference(set(non_free_cells)))

        tmp_cells = []

        direction = choice(('horizontal', 'vertical'))

        while len(tmp_cells) < num_of_decks:
            if len(tmp_cells):
                tmp_cell = (tmp_cells[len(tmp_cells) - 1][0] + 1,
                            tmp_cells[len(tmp_cells) - 1][1]) if direction == 'horizontal' \
                    else (tmp_cells[len(tmp_cells) - 1][0],
                          tmp_cells[len(tmp_cells) - 1][1] + 1)

                if tmp_cell not in free_cells:
                    tmp_cell = (tmp_cells[0][0] - 1, tmp_cells[0][1]) if direction == 'horizontal' \
                        else (tmp_cells[0][0], tmp_cells[0][1] - 1)

                if tmp_cell not in free_cells:
                    free_cells += tmp_cells
                    tmp_cells.clear()
                    tmp_cell = choice(free_cells)
            elif not len(free_cells):
                # действительно заканчиваются в некоторых случаях
                # print('DEBUG: Закончились свободные ячейки!')
                # board.print()
                raise Warning('Неудачно расположены корабли. Не хватило ячеек')
            else:
                tmp_cell = choice(free_cells)

            free_cells.remove(tmp_cell)
            tmp_cells.append(tmp_cell)

        for tmp_cell in tmp_cells:
            board_cell = board.cell_by_coords(*tmp_cell)
            board_cell.state = Cell.States.deck_whole
            self.cells.append(board_cell)

    @staticmethod
    def init_new_list(board):
        # 1 корабль на 3 клетки, 2 корабля на 2 клетки, 4 корабля на одну клетку
        while True:
            # если поле размером 6 на 6, бываеют ситуации, когда не хватает ячеек
            # в этом случае будем перераспределять корабли
            try:
                result = [Ship(3, board)] + [Ship(2, board) for _ in range(2)] + [Ship(1, board) for _ in range(4)]
            except Warning as ex:
                # print('Перераспределение ячеек...')
                board = Board(board.header)
            else:
                return result


class Cell:
    class States:
        empty = ' '
        deck_whole = '='
        deck_burning = 'x'
        hole = 'o'

    def __init__(self, row, column):
        if not (0 < row <= Game.num_rows) or \
                not (0 < column <= Game.num_columns):
            raise ValueError('Ошибка создания ячейки игрового поля')

        self._state = Cell.States.empty
        self._row = row
        self._column = column

    @property
    def row(self):
        return self._row

    @property
    def column(self):
        return self._column

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if type(state) != str or state not in self.States.__dict__.values():
            raise ValueError('Ошибка создания ячейки игрового поля')
        self._state = state


class Board:
    def __init__(self, header):
        self._cells = [Cell(row, column) for row in range(1, Game.num_rows + 1)
                       for column in range(1, Game.num_columns + 1)]
        self.header = header

    def print(self, show_ships = True):
        print(self.header)
        str_to_print = '   '
        for col_num in range(Game.num_columns):
            str_to_print += f'{col_num + 1} '

        print(str_to_print)

        str_to_print = '1 '

        for cell in self._cells:
            if show_ships:
                str_to_print += f'|{cell.state}'
            else:
                str_to_print += f'|{Cell.States.empty if cell.state == Cell.States.deck_whole else cell.state}'

            if self._cells.index(cell) != len(self._cells) - 1:
                str_to_print += f'|\n{int((self._cells.index(cell) + 1) / Game.num_columns + 1)} ' \
                    if not (self._cells.index(cell) + 1) % Game.num_columns else ''
        print(str_to_print + '|')

        print('')

    def set_cell(self, row, col, state):
        self._cells[row][col].state = state

    def cells_by_status(self, state):
        return list(filter(lambda cell: cell.state == state, self._cells))

    def cell_by_coords(self, row, column):
        return list(filter(lambda cell: cell.row == row and cell.column == column, self._cells))[0]

    def has_whole_ships(self):
        return len(self.cells_by_status(Cell.States.deck_whole)) != 0


class Game:
    num_rows = 6
    num_columns = 6

    def __init__(self):
        self._player_board = Board('--==Ваше поле==--')
        ships = Ship.init_new_list(self._player_board)
        self._pc_board = Board('--==Поле ИИ==--')
        ships = Ship.init_new_list(self._pc_board)

    @property
    def player_board(self):
        return self._player_board

    @property
    def pc_board(self):
        return self._pc_board

    # def print_boards(self):
    #     self._player_board.print()
    #     self._pc_board.print()

    @staticmethod
    def get_bool_answer(question_text):
        while True:
            answer = input(question_text).lower().strip()
            if answer == 'y':
                return True
            elif answer == 'n':
                return False

    def player_shot(self):
        while True:
            answer = input('Ваш ход. Введите номера строки и колонки цифрами (m - показать ваше поле):')
            if answer == 'm':
                self._player_board.print()
                continue

            answer = list(map(lambda char: char if char.isdigit() else '', answer))
            if len(answer) != 2:
                print('Ошибка в координатах. Попробуйте ещё раз')
                continue

            row, column = int(answer[0]), int(answer[1])
            if not (1 <= row <= self.num_rows and 1 <= column <= self.num_columns):
                print('Ошибка в координатах. Попробуйте ещё раз')
                continue

            free_cells = self._pc_board.cells_by_status(Cell.States.empty) + \
                         self._pc_board.cells_by_status(Cell.States.deck_whole)
            cell = self._pc_board.cell_by_coords(row, column)

            if cell not in free_cells:
                print('Ошибка в координатах. Попробуйте ещё раз')
                continue

            if cell.state == Cell.States.empty:
                print('Вы промахнулись')
                cell.state = Cell.States.hole
            elif cell.state == Cell.States.deck_whole:
                print('Удачный выстрел!')
                cell.state = Cell.States.deck_burning

            break

    def pc_shot(self):
        free_cells = self._player_board.cells_by_status(Cell.States.empty) + \
                     self._player_board.cells_by_status(Cell.States.deck_whole)

        # если не перемешать список, choise первую половину игры промахивается, вторую попадает. Шаг?
        shuffle(free_cells)

        cell = choice(free_cells)
        print(f'Ход компьютера: строка - {cell.row}, колонка - {cell.column}')

        if cell.state == Cell.States.empty:
            cell.state = Cell.States.hole
            print('ИИ промахивается')
        elif cell.state == Cell.States.deck_whole:
            print('ИИ попадает!')
            cell.state = Cell.States.deck_burning

while True:

    game = Game()
    game.player_board.print()
    game.pc_board.print(False)

    while True:
        if not game.pc_board.has_whole_ships():
            print('Вы выиграли!')
            break
        elif not game.player_board.has_whole_ships():
            print('Вы проиграли.')
            break

        game.player_shot()
        game.pc_board.print(False)
        game.pc_shot()
        game.player_board.print()

    if not Game.get_bool_answer('Сыграть еще раз? (y - начать заново, n - выйти): '):
        break
