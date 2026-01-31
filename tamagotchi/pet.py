import json
import os
from datetime import datetime
from pathlib import Path

def dict_construct(pet, save_date):
    """
    Format pet's attribute into JSON-serializable format
    
    :param pet: pet's instance
    :param save_date: date of current session instance
    """
    return {pet.name: {'properties': {'health': pet.health, 'fatigue': pet.fatigue, 'sleep': pet.sleepy, 'experience': pet.experience,'save_date': save_date}}}


class Pet:
    def __init__(self, name: str):
        self.name = name
        self.health = 10
        self.fatigue = 5
        self.sleepy = 5
        self.experience = 0
        self.resting = False
        self.alive = True
        self.rest_start_time = None
        self.death_condition = self.fatigue > 50 or self.sleepy > 50 or self.health == 0

        
        BASE_DIR = Path(__file__).resolve().parent.parent
        SAVE_DIR = BASE_DIR / "saves"
        SAVE_DIR.mkdir(exist_ok=True)

        self.save_path = SAVE_DIR / f"save_{self.name}.json"

        if self.save_path.exists():
            self._load_state()
        else:
            self._save_state()


    def rest(self):
        if not self.resting:
            self.resting = True
            self.rest_start_time = datetime.now()

    def awake(self):
        self.resting = False
        self.rest_start_time = None

    # Deletion handled in death command
    #def delete_save(self): 
    #    self.save_path.unlink(missing_ok=True)

    def _save_state(self):
        """
        Create or update a save state for the pet
        """
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        state_dict = dict_construct(self, now)

        with self.save_path.open("w") as f:
            json.dump(state_dict, f, indent=4)


    def _load_state(self):
        """
        Load Save state from disk and applies time degradation
        """

        if os.path.exists(self.save_path):
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                if self.name in data:
                    props = data[self.name]['properties']

                    # Simple time degradation mechanism - to refine
                    last_save = datetime.strptime(props.get('save_date', 0), "%m/%d/%Y, %H:%M:%S")
                    hours_elapsed = (datetime.now() - last_save).total_seconds() / 36000
                    self.apply_time_degradation(hours_elapsed)

                    self.health = props.get('health', 1) 
                    self.fatigue = props.get('fatigue', 0)
                    self.sleepy = props.get('sleep', 0) 
                    self.experience = props.get('experience', 0)

            print(f"Loaded state for {self.name}: health={self.health}, fatigue={self.fatigue}, sleep={self.sleepy}")
        else:
            print("No save file found, starting fresh.")

    def apply_time_degradation(self, hours_elapsed):
        """
        Apply time-based changes to pet properties
        - Fatigue increases over time
        - Experience decays slightly
        - Sleepiness increases
        """
        # Fatigue increases with time (0.1 per hour, max 1.0)
        fatigue_increase = min(hours_elapsed * 0.1, 1.0 - self.fatigue)
        self.fatigue += fatigue_increase
        
        # Experience decays slightly (5% per day = ~0.2% per hour)
        exp_decay = self.experience * (hours_elapsed * 0.002)  # 0.2% per hour
        self.experience = max(0, self.experience - exp_decay)
        
        # Sleepiness increases (0.15 per hour, max 1.0)
        sleep_increase = min(hours_elapsed * 0.15, 1.0 - self.sleepy)
        self.sleepy += sleep_increase
        
        # Health slowly decreases if very fatigued or sleepy
        if self.fatigue > 0.8 or self.sleepy > 0.8:
            health_decay = hours_elapsed * 0.01  # 1% per hour when over-tired
            self.health = max(0.1, self.health - health_decay)
        
        print(f"  Time effects: +{fatigue_increase:.2f} fatigue, -{exp_decay:.2f} XP, +{sleep_increase:.2f} sleep")


    def update(self):
        if self.resting:
            now = datetime.now()
            elapsed = (now - self.rest_start_time).total_seconds()
            
            self.sleepy -= 0.2 * elapsed
            self.sleepy = max(0, round(self.sleepy, 3))
            
            # Optional: reduce fatigue as well
            self.fatigue = max(0, round(self.fatigue - 0.1 * elapsed, 3))
            
            # Update start time
            self.rest_start_time = now
            
            # Stop resting when fully rested
            if self.sleepy == 0 and self.fatigue == 0:
                self.resting = False

    # Not implemented
    def feed(self):
        self.health += 0.2  

    def __str__(self):
        return f"""Monster's Name: {self.name} \n
(`')  
 \/   Health: {self.health} \n
 Fatige: {self.fatigue} \n
 Sleepy: {self.sleepy}         
            ^	
         __/_\__
        /__ 0 __\\ EXP: {self.experience}
           |||
           ||| 
            V"""


    
    
   
