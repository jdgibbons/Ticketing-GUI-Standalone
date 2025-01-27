import tkinter as tk
import ttkbootstrap as ttk


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
