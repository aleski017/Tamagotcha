import json
from datetime import datetime
from pathlib import Path
import random as rnd


class Pet:
    """A virtual pet with health, fatigue, and sleep mechanics."""

    MAX_STAT = 50
    FATIGUE_PER_HOUR = 0.1
    SLEEP_PER_HOUR = 0.15
    EXP_DECAY_PER_HOUR = 0.002
    HEALTH_DECAY_PER_HOUR = 0.01
    HEALTH_DECAY_THRESHOLD = 0.8
    REST_FATIGUE_RATE = 0.1
    REST_SLEEP_RATE = 0.2
    
    def __init__(self, name: str):
        self.name = name
        # Pet is born with some random IV (Initial Values)
        self.health = rnd.randint(5, 15)
        self.fatigue = rnd.randint(0, 5) 
        self.sleepy = rnd.randint(0, 5)

        self.experience = 0
        self.resting = False
        self.alive = True
        self.rest_start_time = None
        
        # Handle first time load
        base_dir = Path(__file__).resolve().parent.parent
        save_dir = base_dir / "saves"
        save_dir.mkdir(exist_ok=True)
        self.save_path = save_dir / f"save_{self.name}.json"
        
        if self.save_path.exists():
            self._load_state()
        else:
            self._save_state()
        
        self.death_condition = self.fatigue > self.MAX_STAT or self.sleepy > self.MAX_STAT or self.health == 0
    
    def delete_save(self): 
        self.save_path.unlink(missing_ok=True)

    def rest(self):
        """Start resting to recover sleep and fatigue."""
        if not self.resting:
            self.resting = True
            self.rest_start_time = datetime.now()
    
    def awake(self):
        """Stop resting."""
        self.resting = False
        self.rest_start_time = None
    
    def _save_state(self):
        """Create or update a save state for the pet."""
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        state_dict = {
            self.name: {
                'properties': {
                    'health': self.health,
                    'fatigue': self.fatigue,
                    'sleep': self.sleepy,
                    'experience': self.experience,
                    'resting': self.resting,
                    'save_date': now
                }
            }
        }
        
        with self.save_path.open("w") as f:
            json.dump(state_dict, f, indent=4)
    
    def _load_state(self):
        """Load save state from disk and apply time degradation."""
        try:
            with self.save_path.open('r') as f:
                data = json.load(f)
            
            if self.name not in data:
                print("No save file found, starting fresh.")
                return
            
            props = data[self.name]['properties']
            
            self.health = props.get('health', 1)
            self.fatigue = props.get('fatigue', 0)
            self.sleepy = props.get('sleep', 0)
            self.experience = props.get('experience', 0)
            
            #  apply time degradation
            save_date_str = props.get('save_date')
            if save_date_str:
                last_save = datetime.strptime(save_date_str, "%m/%d/%Y, %H:%M:%S")
                                                                    #second per hour
                hours_elapsed = (datetime.now() - last_save).total_seconds() / 3600
                
                # DOES NOT WORK - WIP
                # If saved when resting then pet recovers
                #if props.get('resting', 0):
                #    self.apply_rest_recovery(hours_elapsed)
                #else: self.apply_time_degradation(hours_elapsed)
                self.apply_time_degradation(hours_elapsed)
            
            print(f"Loaded state for {self.name}: health={self.health}, fatigue={self.fatigue}, sleep={self.sleepy}, resting = {self.resting}")
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading save file: {e}. Starting fresh.")

# WIP - Does not work   
#    def apply_rest_recovery(self, hours_elapsed):
#        """
#        Apply recovery while pet is resting (even when game is closed).
#        - Fatigue decreases
#        - Sleepiness decreases
#        - Experience stays the same (no decay while resting)
#        """
#
#        seconds_elapsed = hours_elapsed * 3600
#        
#        fatigue_decrease = self.REST_FATIGUE_RATE * seconds_elapsed
#        self.fatigue = max(0, self.fatigue - fatigue_decrease)
#        
#        sleep_decrease = self.REST_SLEEP_RATE * seconds_elapsed
#        self.sleepy = max(0, self.sleepy - sleep_decrease)
#        
#        print(f"Rest recovery: -{fatigue_decrease:.2f} fatigue, -{sleep_decrease:.2f} sleepiness")


    def apply_time_degradation(self, hours_elapsed):
        """
        Apply time-based changes to pet properties.
        - Fatigue increases over time
        - Experience decays slightly
        - Sleepiness increases
        """

        fatigue_increase = min(hours_elapsed * self.FATIGUE_PER_HOUR, self.MAX_STAT - self.fatigue)
        self.fatigue += fatigue_increase
        
        exp_decay = self.experience * (hours_elapsed * self.EXP_DECAY_PER_HOUR)
        self.experience = max(0, self.experience - exp_decay)
        
        sleep_increase = min(hours_elapsed * self.SLEEP_PER_HOUR, self.MAX_STAT - self.sleepy)
        self.sleepy += sleep_increase
        
        # Health slowly decreases if very fatigued or sleepy
        if self.fatigue > self.HEALTH_DECAY_THRESHOLD or self.sleepy > self.HEALTH_DECAY_THRESHOLD:
            health_decay = hours_elapsed * self.HEALTH_DECAY_PER_HOUR
            self.health = max(0.1, self.health - health_decay)
        
        print(f"Time effects: +{fatigue_increase:.2f} fatigue, -{exp_decay:.2f} XP, +{sleep_increase:.2f} sleep")
    
    def update(self):
        """Update pet state based on elapsed time since last rest check."""
        if self.resting:
            now = datetime.now()
            elapsed = (now - self.rest_start_time).total_seconds()
            
            self.sleepy -= self.REST_SLEEP_RATE * elapsed
            self.sleepy = max(0, round(self.sleepy, 3))
            
            self.fatigue = max(0, round(self.fatigue - self.REST_FATIGUE_RATE * elapsed, 3))
            
            self.rest_start_time = now
            
            if self.sleepy == 0 and self.fatigue == 0:
                self.resting = False
    
    def __str__(self):
        return f"""Monster's Name: {self.name} \n
(`')  
 \/   Health: {round(self.health, 1)} \n
 Fatige: {round(self.fatigue, 1)} \n
 Sleepy: {round(self.sleepy, 1)}         
            ^	
         __/_\__
        /__ 0 __\\ EXP: {round(self.experience, 1)}
           |||
           ||| 
            V"""