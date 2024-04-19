    def popup_options_2d(self, options, title=None, shadow=True, extended_border=False, scrollable=False):
        """
        Display a popup message with given options arranged in 2D grid.
        Blocks until option selected, returns selection.
        USAGE: arrows for selecting options, W and A for switching pages.
        """
        
        tft = self.display
        num_cols = 5  # Number of columns in the grid
        per_colomn = 6
        col_width = 240 // num_cols  # Width of each column
        row_height = 16  # Height of each row
        
        if scrollable:
            old_options = options
            options = old_options[:num_cols*per_colomn]

        if self.compatibility_mode:
            # draw box
            box_height = (len(options) // num_cols + 1) * row_height + 8
            box_y = 67 - (box_height // 2)
            if extended_border:
                tft.fill_rect(0, max(box_y - 10, 0), 240, min(box_height + 20, 135), self.config.palette[1])
            if title:
                self.draw_textbox(title, 120, box_y - 16, shadow=shadow, extended_border=extended_border)
        else:
            # draw box
            box_height = (len(options) // num_cols + 1) * row_height + 8
            box_y = 67 - (box_height // 2)
            if extended_border:
                tft.fill_rect(0, max(box_y - 10, 0), 240, min(box_height + 20, 135), self.config.palette[1])
            if title:
                self.draw_textbox(title, 120, box_y - 14, shadow=shadow, extended_border=extended_border)

        cursor_index = 0
        keys = self.kb.get_new_keys()
        while True:
            if self.compatibility_mode:
                # draw options
                for idx, option in enumerate(options):
                    col = idx % num_cols
                    row = idx // num_cols
                    x = col * col_width + (col_width - len(option) * 4) // 2
                    y = box_y + row * row_height + 4
                    if idx == cursor_index:
                        tft.fill_rect(x - 2, y - 2, len(option) * 4 + 4, 20, self.config.palette[0])
                        tft.text(self.font, option, x, y, self.config.palette[5], self.config.palette[0])
                    else:
                        tft.text(self.font, option, x, y, self.config.palette[4], self.config.palette[2])
            else:
                # draw options
                for idx, option in enumerate(options):
                    col = idx % num_cols
                    row = idx // num_cols
                    x = col * col_width + (col_width - len(option) * 4) // 2
                    y = box_y + row * row_height + 4
                    if idx == cursor_index:
                        tft.fill_rect(x - 2, y - 2, len(option) * 4 + 4, 20, self.config.palette[0])
                        tft.text(option, x, y, self.config.palette[5])
                    else:
                        tft.text(option, x, y, self.config.palette[4])
                tft.show()

            keys = self.kb.get_new_keys()
            for key in keys:
                if key == ";":  # Move cursor up
                    cursor_index = (cursor_index - num_cols) % len(options)
                elif key == ".":  # Move cursor down
                    cursor_index = (cursor_index + num_cols) % len(options)
                elif key == ",":  # Move cursor left
                    cursor_index = (cursor_index - 1) % len(options)
                elif key == "/":  # Move cursor right
                    cursor_index = (cursor_index + 1) % len(options)
                elif key == "w" and scrollable:
                    next_page_result = self.popup_options_2d(options=old_options[num_cols*per_colomn:], title=title, shadow=shadow,
                                                          extended_border=extended_border, scrollable=True)
                    if next_page_result != None:
                        return next_page_result
                    else:
                        cursor_index = 0
                elif key == "`" or key == "ESC" or key == "BSPC" or key == "a":
                    return None
                elif key == "ENT" or key == "GO":
                    return options[cursor_index]

            time.sleep_ms(10)