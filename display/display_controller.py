from display.lcd_printout import Printout
from display.lcd_display import LcdDisplay

class DisplayController:
    displays = [] # this list will contain all display instances

    def __init__(self):
        pass
    def configure(self,configuration):
        for c in configuration:
            print("add dispal with id "+c['id'])
            self.displays.append(LcdDisplay(c))

    def print_immediately(self, display_id, printout: Printout):
         for d in self.displays:
             d.print_immediately(printout)

    def add_printout(self, display_id, printout: Printout):
        self.update_printout_data(display_id, printout)

    def update_printout_data(self, display_id, printout: Printout):
        if len(self.displays) == 0:
            print("go away")
            return

        found = False
        print("update_printout_data: length of displays: ",len(self.displays))
        for d in range(len(self.displays)):
            print("check if: ",self.displays[d].display_id," is equal to: ",display_id)
            if self.displays[d].display_id == display_id:
                self.displays[d].update_printout_data(printout)
                found = True
                print("display found and updated")
        if not found:
            print("display with id:")

    def get_displays_id(self):
        return [i.display_id for i in self.displays]

    def update(self):
        for d in self.displays:
            d.update()

    
