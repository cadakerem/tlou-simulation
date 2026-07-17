import random
import matplotlib.pyplot as plt

class Player:
    def __init__(self, name, scavenge_rate, skill_modifier, hp_threshold, medkit_prob_high, medkit_prob_low):
        self.name = name
        self.scavenge_rate = scavenge_rate
        self.skill_modifier = skill_modifier
        self.hp_threshold = hp_threshold
        self.medkit_prob_high = medkit_prob_high
        self.medkit_prob_low = medkit_prob_low
        
        self.hp = 100
        self.deaths = 0
        self.alcohol = 0
        self.rags = 0
        self.medkits = 0
        self.molotovs = 0
        
        # Hard limits as per PDF ("strictly capacity-capped inventories")
        self.max_cap = 3 
        
        self.hp_history = []
        
    def step(self, step_num):
        # 1. Scavenge
        if random.random() < self.scavenge_rate:
            if self.alcohol < self.max_cap:
                self.alcohol += 1
        if random.random() < self.scavenge_rate:
            if self.rags < self.max_cap:
                self.rags += 1
                
        # 2. Craft
        # Note: only the raw materials (Alcohol, Rag) are capped at max_cap.
        # Medkit and Molotov inventories are uncapped in the Machinations model.
        if self.alcohol > 0 and self.rags > 0:
            prob = self.medkit_prob_high if self.hp > self.hp_threshold else self.medkit_prob_low
            if random.random() < prob:
                self.medkits += 1
                self.alcohol -= 1
                self.rags -= 1
            else:
                self.molotovs += 1
                self.alcohol -= 1
                self.rags -= 1

        # 3. Enemy Damage
        # Machinations formulas (M = current Molotov stock, acts as a damage buffer;
        # S = Skill Modifier -- multiplied INSIDE the max(1, ...) floor, per the
        # formulas read directly from the Machinations nodes):
        #   Zombie:  max(1, (2 + floor(STEP/10) - M*2) * S)          -- every step
        #   Clicker: random() < 0.3 ? max(1, (3 - M*2) * S) : 0      -- every step
        #   Bloater: STEP in {60,70,80,90,100} ? max(1, (30 - M*5) * S) : 0
        M = self.molotovs

        zombie_dmg = max(1, (2 + (step_num // 10) - M * 2) * self.skill_modifier)

        clicker_dmg = 0
        if random.random() < 0.3:
            clicker_dmg = max(1, (3 - M * 2) * self.skill_modifier)

        actual_dmg = zombie_dmg + clicker_dmg

        if step_num in (60, 70, 80, 90, 100):
            bloater_dmg = max(1, (30 - M * 5) * self.skill_modifier)
            actual_dmg += bloater_dmg

        self.hp -= actual_dmg

        # "Use Molotov" is an automatic pull: any Molotov in inventory is spent
        # immediately after it's used to buffer this step's damage. Crafting only
        # ever produces one item per step, so molotov stock is always 0 or 1 here.
        if self.molotovs > 0:
            self.molotovs -= 1

        # 4. Death Check
        if self.hp <= 0:
            self.deaths += 1
            self.hp = 100
            
        # 5. Heal Action
        # Medkit is also an automatic pull: it's used the instant it's crafted if
        # HP < 100, but it never carries over to a later step -- if HP was already
        # full this step, the medkit is discarded rather than stockpiled.
        if self.hp < 100 and self.medkits > 0:
            self.hp += 35
            if self.hp > 100:
                self.hp = 100
        self.medkits = 0
            
        # 6. Record
        self.hp_history.append(self.hp)

def main():
    # No fixed seed: each run reflects the system's natural randomness.
    # Across repeated runs the pattern holds -- Pro survives best, Noob struggles
    # most -- but exact death counts will vary run to run.
    
    # Pro: Scavenge 60%, Skill 0.7, Threshold 70, Medkit Prob High 0.3, Low 0.6
    pro = Player("Pro Player", 0.60, 0.7, 70, 0.30, 0.60)
    
    # Normal: Scavenge 40%, Skill 1.0, Threshold 50, Medkit Prob High 0.45, Low 0.85
    normal = Player("Normal Player", 0.40, 1.0, 50, 0.45, 0.85)
    
    # Noob: Scavenge 30%, Skill 1.4, Threshold 40, Medkit Prob High 0.55, Low 0.85
    noob = Player("Noob Player", 0.30, 1.4, 40, 0.55, 0.85)
    
    players = [pro, normal, noob]
    
    for step in range(1, 101):
        for p in players:
            p.step(step)
            
    # Plotting
    plt.figure(figsize=(14, 7))
    
    plt.plot(range(1, 101), pro.hp_history, label=f"Pro Player HP (Deaths: {pro.deaths})", color='#2ca02c')
    plt.plot(range(1, 101), normal.hp_history, label=f"Normal Player HP (Deaths: {normal.deaths})", color='#1f77b4')
    plt.plot(range(1, 101), noob.hp_history, label=f"Noob Player HP (Deaths: {noob.deaths})", color='#d62728')
    
    plt.title("The Last of Us - 100-Step Survival Resource & Combat Simulation", fontsize=14, fontweight='bold')
    plt.xlabel("Simulation Steps", fontsize=12)
    plt.ylabel("Player HP", fontsize=12)
    
    plt.ylim(0, 110)
    plt.axhline(y=0, color='black', linewidth=1)
    
    # Highlight bloater spikes (steps 60, 70, 80, 90, 100)
    for step in (60, 70, 80, 90, 100):
        plt.axvline(x=step, color='purple', linestyle='--', alpha=0.3)
    
    plt.legend(loc='lower left')
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig("simulation_results.png", dpi=300)
    print(f"Simulation completed.\nDeaths -> Pro: {pro.deaths}, Normal: {normal.deaths}, Noob: {noob.deaths}")
    print("Graph saved as simulation_results.png")

if __name__ == "__main__":
    main()
