from display.lcd_printout import Printout
from display.lcd_display import LcdDisplay

class DisplayController:
    displays = [] # this list will contain all display instances
    def __init__(self, configuration):
        for c in configuration:
            self.displays.append(LcdDisplay(c))

    def print_immediately(self, display_id, printout: Printout):
        pass

    def add_printout(self, display_id, printout: Printout):
        self.update_printout_data(display_id, printout)

    def update_printout_data(self, display_id, printout: Printout):
        found = False
        for d in self.displays:
            if d.display_id == display_id:
                d.update_printout_data(printout)
                found = True
        if not found:
            print("display with id:")

    def get_displays_id(self):
        return [i.id for i in self.printouts]

    def update(self):
        for d in self.displays:
            d.update()

    
