#
# MIT License
#
# Copyright (c) 2023 Thought Stream, LLC dba Bluescape.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from typing import List, Tuple
import math

class BluescapeLayout:

    # Padding used for title positioning within the canvas
    top_title_padding_left = 100
    top_title_padding_top = 90

    # Padding used for infotext padding from the bottom of the canvas.
    # If verbose mode enabled the infotext_top_from_bottom is adjusted
    infotext_padding_left = 100
    infotext_top_from_bottom = 250

    # Padding used for infobar padding at the bottom of the canvas.
    bottom_infobar_padding_left = 100
    bottom_infobar_top_from_bottom = 200

    # Used to make space for seed info panel below each image.
    vertical_seed_margin = 50
    margin = 50 # otherwise

    canvas_padding = (400, 500, 50, 50)

    def __init__(self, num_images: int, image_size: Tuple[int, int], verbose_mode: bool):
        min_num_columns = 3 if image_size[0] >= 768 else 4
        num_suggested_columns = math.floor(math.sqrt(num_images))
        num_columns = num_suggested_columns if num_suggested_columns > min_num_columns else min_num_columns

        if (verbose_mode):
            self.infotext_top_from_bottom = 500
            self.canvas_padding = (400, 750, 50, 50)

        self.canvas_padding_top = self.canvas_padding[0]
        self.canvas_padding_left = self.canvas_padding[2]

        self.image_grid_layout, self.image_grid_bounding_box = self._calculate_image_grid_layout(num_images, num_columns, image_size, self.margin)
        self.canvas_bounding_box = self._create_canvas_bounding_box_at_origin(self.canvas_padding)

        # Translate the image grid to origin + padding
        self.image_grid_layout = self._translate_image_grid_layout(self.canvas_padding_left, self.canvas_padding_top)

        self.image_height = image_size[1]

    # Public interface

    def get_image_grid_layout(self) -> Tuple[List[Tuple[int, int]]]:
        return self.image_grid_layout

    def get_canvas_bounding_box(self) -> Tuple[int, int, int, int]:
        return self.canvas_bounding_box

    def get_label_grid_layout(self) -> Tuple[List[Tuple[int, int]]]:
        return self._get_seed_grid_layout()

    def translate(self, target_bounding_box: Tuple[int, int, int, int]):
        new_x, new_y, _, _ = target_bounding_box
        self.canvas_bounding_box = (new_x, new_y, self.canvas_bounding_box[2], self.canvas_bounding_box[3])
        self.image_grid_layout = self._translate_image_grid_layout(self.canvas_padding_left + new_x, self.canvas_padding_top + new_y)

    # Text related public functions

    def get_canvas_title(self, text):
        return self._truncate_string(text, 100)

    def get_top_title_location(self) -> Tuple[int, int, int]:
        return (self.canvas_bounding_box[0] + self.top_title_padding_left, self.canvas_bounding_box[1] + self.top_title_padding_top, self.canvas_bounding_box[2] - self.top_title_padding_left * 2)

    def get_top_title(self, text):
        return self._truncate_string(text, 145)

    def get_bottom_infobar_location(self) -> Tuple[int, int, int]:
        return (self.canvas_bounding_box[0] + self.top_title_padding_left, self.canvas_bounding_box[1] + self.canvas_bounding_box[3] - self.bottom_infobar_top_from_bottom, self.canvas_bounding_box[2] - self.top_title_padding_left * 2)

    def get_infotext_location(self) -> Tuple[int, int, int]:
        return (self.canvas_bounding_box[0] + self.top_title_padding_left, self.canvas_bounding_box[1] + self.canvas_bounding_box[3] - self.infotext_top_from_bottom, self.canvas_bounding_box[2] - self.top_title_padding_left * 2)

    def get_infotext_label_location(self) -> Tuple[int, int, int]:
        return (self.canvas_bounding_box[0] + self.top_title_padding_left, self.canvas_bounding_box[1] + self.canvas_bounding_box[3] - self.infotext_top_from_bottom - 74, self.canvas_bounding_box[2] - self.top_title_padding_left * 2)

    def get_extended_generation_data_label_location(self) -> Tuple[int, int, int]:
        return (self.canvas_bounding_box[0] + self.top_title_padding_left, self.canvas_bounding_box[1] + self.canvas_bounding_box[3] - self.bottom_infobar_top_from_bottom - 74, self.canvas_bounding_box[2] - self.top_title_padding_left * 2)


    # Private functions

    def _calculate_image_grid_layout(self, num_images: int, num_columns: int, image_size: Tuple[int, int], margin: int) -> Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]:
        """
        Calculates a grid layout for the given number of images, based on the desired number of columns,
        image size, and margin.

        :param num_images: The number of images.
        :param num_columns: The desired number of columns in the grid.
        :param image_size: A tuple representing the size (width, height) of each image.
        :param margin: The margin in pixels between each image.
        :return: A list of tuples representing the position (x, y) of each image in the grid layout.
        """

        image_width, image_height = image_size

        # Calculate the number of rows based on the desired number of columns
        num_rows = (num_images + num_columns - 1) // num_columns

        # Calculate the canvas width and height based on the number of columns/rows, image size, and margin
        canvas_width = num_columns * image_width + (num_columns - 1) * margin
        canvas_height = num_rows * image_height + (num_rows - 1) * margin + self.vertical_seed_margin * num_rows

        # Calculate the width and height of each cell in the grid
        cell_width = image_width
        cell_height = image_height

        # Calculate the x and y position of each image in the grid
        layout = []
        for i in range(num_images):
            col = i % num_columns
            row = i // num_columns
            x = col * (cell_width + margin)
            y = row * (cell_height + margin + self.vertical_seed_margin)
            layout.append((x, y))

        bounding_box = (0, 0, canvas_width, canvas_height)

        return layout, bounding_box

    def _create_canvas_bounding_box_at_origin(self, canvas_padding: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Adds padding to each side of the bounding box.

        :param bounding_box: A tuple representing the bounding box coordinates (left, top, width, height).
        :param padding_top: The padding value for the top side.
        :param padding_bottom: The padding value for the bottom side.
        :param padding_left: The padding value for the left side.
        :param padding_right: The padding value for the right side.
        :return: A tuple representing the new bounding box coordinates with padding applied (left, top, width, height).
        """

        x, y, width, height = self.image_grid_bounding_box
        padding_top, padding_bottom, padding_left, padding_right = canvas_padding

        x = 0
        y = 0
        width += padding_left + padding_right
        height += padding_top + padding_bottom

        return 0, 0, width, height

    def _translate_image_grid_layout(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Translates the existing layout to new coordinates based on the target (x, y).

        :param x: The target x-coordinate for translation.
        :param y: The target y-coordinate for translation.
        :param layout: A list of tuples representing the position (x, y) of each image in the layout.
        :return: A list of tuples representing the new layout with translated coordinates.
        """

        # Calculate the translation delta
        delta_x = x - self.image_grid_layout[0][0]
        delta_y = y - self.image_grid_layout[0][1]

        # Translate the layout coordinates
        new_layout = [(lx + delta_x, ly + delta_y) for lx, ly in self.image_grid_layout]

        return new_layout

    def _get_seed_grid_layout(self) -> List[Tuple[int, int]]:

        # TODO: this is silly - the magic 13
        # Translation delta is the height of the image
        delta_x = 13
        delta_y = self.image_height + 13

        # Translate the layout coordinates
        seed_grid_layout = [(lx + delta_x, ly + delta_y) for lx, ly in self.image_grid_layout]

        return seed_grid_layout

    def _truncate_string(self, text, max_length):
        if len(text) > max_length:
            truncated_text = text[:max_length-3] + "..."
        else:
            truncated_text = text
        return truncated_text