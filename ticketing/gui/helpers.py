import ttkbootstrap as ttk

from ticketing.games.game_n_c_i_ca import create_game as ncica_create_game
from ticketing.games.game_n_s_i_sh import create_game as nsish_create_game
from ticketing.games.game_n_i_i_im import create_game as niiim_create_game
from ticketing.games.game_i_i_i_im import create_game as iiiim_create_game
from ticketing.games.game_i_i_i_ba import create_game as iiiba_create_game
from ticketing.games.game_i_i_i_ma import create_game as iiima_create_game
from ticketing.games.game_n_i_i_fl import create_game as niifl_create_game
from ticketing.games.game_i_i_i_bi import create_game as iiibi_create_game
from ticketing.games.game_i_i_i_bb import create_game as iiibb_create_game
from ticketing.games.game_i_i_i_bn import create_game as iiibn_create_game


def create_label_and_field(label_text, input_field, row, column, parent_frame,
                           default_text=None, input_span: int = 1):
    """
    Create a pair of widgets comprised of a label and some sort of data collection field.

    :param label_text: name of the widget
    :type label_text: str
    :param input_field: a data-collection widget
    :type input_field: tkinter.ttk widget
    :param row: grid row to assign the widget
    :type row: int
    :param column: grid column to assign the widget
    :type column: int
    :param parent_frame: frame in which the widget will be placed
    :type parent_frame: tkinter.ttk.Frame or tkinter.ttk.LabelFrame
    :param default_text: text to place in entry field
    :type default_text: str or int
    :param input_span: number of columns the widget will span
    :type input_span: int
    :return: label and input widget
    :rtype [(tkinter.ttk.Label, tkinter.ttk.Widget)]:
    """
    # Create and position the label
    label = ttk.Label(parent_frame, text=label_text)
    label.grid(row=row, column=column, padx=10, pady=5, sticky="w")
    # Position the input widget
    input_field.grid(row=row, column=column + 1, padx=10, pady=5, columnspan=input_span, sticky="e")
    # Add the input field to the field dictionary, set its default value,
    # then add it to the input_fields list.
    if default_text:
        input_field.insert(0, default_text)  # Set default text if provided
    # Return the label and widget
    return label, input_field


def extract_ticket_types(game_spex):
    """
    Remove the first element of the ticket types for nonwinners, instants,
    picks, and holds and return them as a list.

    :param game_spex: a list of specs for a ticketed game, elemets 1 - 4 correspond to
                      ticket types nonwinners, instants, picks, and holds respectively.
    :return:
    """
    return [game_spex[1].pop(0), game_spex[2].pop(0), game_spex[3].pop(0), game_spex[4].pop(0)]


def select_game_method(nw_type: str, inst_type: str, pick_type: str, hold_type: str):
    full_type = nw_type + inst_type + pick_type + hold_type
    # NW - Instant - Pick - Hold
    # Image - Image - Image - Image
    if full_type in ["IIIIM"]:
        return iiiim_create_game
    # Numbers - Cannons - Image - Cannons
    elif full_type in ["NCICA"]:
        return ncica_create_game
    # Numbers - Shaded - Image - Shaded
    elif full_type in ["NSISH", "NIISH"]:
        return nsish_create_game
    # Numbers - Image - Image - Image
    elif full_type in ['NIIIM']:
        return niiim_create_game
    # Numbers - Shaded - Image - Balls
    elif full_type in ['NSIBA', 'IIIBA']:
        return iiiba_create_game
    # Image - Image - Image - Matrix
    elif full_type in ['IIIMA']:
        return iiima_create_game
    elif full_type in ['NIIFL']:
        return niifl_create_game
    elif full_type in ['IIIBI']:
        return iiibi_create_game
    elif full_type in ['IIIBB']:
        return iiibb_create_game
    elif full_type in ['IIIBN']:
        return iiibn_create_game
    else:
        return None
