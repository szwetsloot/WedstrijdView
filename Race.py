

class Race:
    
    race_status = 0;
    Con = "";
    
    def __init__(self, Con):
        self.Con = Con;
        
    def get_race_status(self):
        return self.race_status;
    
    def get_next_race(self):
        time = Con.get_next_heat();