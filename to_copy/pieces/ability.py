from pieces.useful_funcs import *


class Ability:
    def __init__(self, info: dict):
        self.info = {k: v for k, v in info.items()}

    def text_info(self):  # для отображения информации о способности
        return [self.info["NAME"], ABILITY_DESCRIPTION[self.info["NAME"]]]

    def use(self, centre_row, centre_col, ability_range, field, test=False):  # использование способности
        if self.info["USE_COUNT"]:
            if ABILITY_ACTIONS[self.info["ACTION"]](centre_row, centre_col, ability_range, field):
                if not test:
                    self.info["USE_COUNT"] -= 1
                return True
            else:
                return False
        else:
            return False

    def update_counter(self):
        self.info["USE_COUNT"] -= 1

    def get_ability_range(self):  # возвращает радиус действия способности
        return self.info["RANGE"]

    def get_use_count(self):
        return self.info["USE_COUNT"]

    def get_image(self):
        return self.info["IMAGE"]

    def is_all_cells(self):
        return self.info["ALL_CELLS"]


def piece_check(piece):
    return piece is not None and not piece.char() == 'K'


def not_king_check(piece):
    return piece is None or piece.char() != 'K'


def carry(centre_row, centre_col, ability_range, field):
    used_coords = []
    ability_success = 0
    for row_delta, col_delta in ability_range:
        row_sub, col_sub = centre_row - row_delta, centre_col - col_delta
        row_add, col_add = centre_row + row_delta, centre_col + col_delta
        if (row_add, col_add) in used_coords or (row_sub, col_sub) in used_coords:
            continue
        used_coords.append((row_sub, col_sub))
        used_coords.append((row_add, col_add))
        if correct_coords(row_add, col_add) and correct_coords(row_sub, col_sub):
            if not_king_check(field[row_add][col_add]) and not_king_check(field[row_sub][col_sub]):
                field[row_add][col_add], field[row_sub][col_sub] = field[row_sub][col_sub], field[row_add][col_add]
                if field[row_add][col_add] is not None:
                    field[row_add][col_add].set_position(row_add, col_add)
                if field[row_sub][col_sub] is not None:
                    field[row_sub][col_sub].set_position(row_sub, col_sub)
                ability_success = 1
    return ability_success


def stop(centre_row, centre_col, ability_range, field, **kwargs):
    ability_successs = 0
    for row_delta, col_delta in ability_range:
        row_add, col_add = centre_row + row_delta, centre_col + col_delta
        if correct_coords(row_add, col_add):
            if piece_check(field[row_add][col_add]):
                ability_successs = 1
                field[row_add][col_add].stopped = True
    return ability_successs


def absorb(centre_row, centre_col, ability_range, field, **kwargs):
    for row_delta, col_delta in ability_range:
        row_add, col_add = centre_row + row_delta, centre_col + col_delta
        if correct_coords(row_add, col_add):
            if piece_check(field[row_add][col_add]):
                field[row_add][col_add] = None
    field[centre_row][centre_col] = None
    return True


def replace(centre_row, centre_col, target_coords, field, **kwargs):
    target_row, target_col = target_coords[0]
    ability_successs = 0
    if piece_check(field[target_row][target_col]):
        ability_successs = 1
        field[centre_row][centre_col], field[target_row][target_col] = field[target_row][target_col], field[centre_row][
            centre_col]
        field[centre_row][centre_col].set_position(centre_row, centre_col)
        field[target_row][target_col].set_position(target_row, target_col)
    return ability_successs


def pierce(centre_row, centre_col, target_coords, field, **kwargs):
    ability_successs = 0
    target_row, target_col = target_coords[0]
    enemy_piece = field[target_row][target_col]
    if piece_check(enemy_piece) and enemy_piece.color != field[centre_row][centre_col].color:
        ability_successs = 1
        field[target_row][target_col] = None
    return ability_successs


def shield(centre_row, centre_col, ability_range, field, **kwargs):
    piece = field[centre_row][centre_col]
    for row_delta, col_delta in ability_range:
        row_add, col_add = centre_row + row_delta, centre_col + col_delta
        if correct_coords(row_add, col_add):
            if piece_check(field[row_add][col_add]) and field[row_add][col_add].color == piece.color:
                new_piece = field[row_add][col_add]
                new_piece.shielded = True
    piece.shielded = True
    return True


ABILITY_ACTIONS = {"ABSORB": absorb, "REPLACE": replace, "PIERCE": pierce, "CARRY": carry, "STOP": stop,
                   "SHIELD": shield}
