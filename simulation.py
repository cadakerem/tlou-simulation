import random
import matplotlib.pyplot as plt
import config

class Player:
    def __init__(self, name, scavenge_rate, skill_modifier, hp_threshold, medkit_prob_high, medkit_prob_low):
        self.name = name
        self.scavenge_rate = scavenge_rate
        self.skill_modifier = skill_modifier
        self.hp_threshold = hp_threshold
        self.medkit_prob_high = medkit_prob_high
        self.medkit_prob_low = medkit_prob_low
        
        self.hp = config.MAX_HP
        self.deaths = 0
        self.alcohol = 0
        self.rags = 0
        self.medkits = 0
        self.molotovs = 0
        
        self.max_cap = config.MAX_INVENTORY_CAP 
        
        self.hp_history = []
        
    def step(self, step_num):
        # 1. Scavenge (Optimized logic)
        if random.random() < self.scavenge_rate and self.alcohol < self.max_cap:
            self.alcohol += 1
        if random.random() < self.scavenge_rate and self.rags < self.max_cap:
            self.rags += 1
                
        # 2. Craft (Optimized logic)
        if self.alcohol > 0 and self.rags > 0:
            prob = self.medkit_prob_high if self.hp > self.hp_threshold else self.medkit_prob_low
            if random.random() < prob:
                self.medkits += 1
            else:
                self.molotovs += 1
            self.alcohol -= 1
            self.rags -= 1

        # 3. Enemy Damage
        M = self.molotovs

        zombie_dmg = max(1, (config.ZOMBIE_BASE_DMG + (step_num // 10) - M * config.ZOMBIE_MOLOTOV_DEFENSE) * self.skill_modifier)

        clicker_dmg = 0
        if random.random() < config.CLICKER_PROBABILITY:
            clicker_dmg = max(1, (config.CLICKER_BASE_DMG - M * config.CLICKER_MOLOTOV_DEFENSE) * self.skill_modifier)

        actual_dmg = zombie_dmg + clicker_dmg

        if step_num in config.BLOATER_SPAWN_STEPS:
            bloater_dmg = max(1, (config.BLOATER_BASE_DMG - M * config.BLOATER_MOLOTOV_DEFENSE) * self.skill_modifier)
            actual_dmg += bloater_dmg

        self.hp -= actual_dmg

        if self.molotovs > 0:
            self.molotovs -= 1

        # 4. Death Check
        if self.hp <= 0:
            self.deaths += 1
            self.hp = config.MAX_HP
            
        # 5. Heal Action (Optimized logic)
        if self.hp < config.MAX_HP and self.medkits > 0:
            self.hp = min(self.hp + config.MEDKIT_HEAL_AMOUNT, config.MAX_HP)
        self.medkits = 0
            
        # 6. Record
        self.hp_history.append(self.hp)

def main():
    pro = Player("Pro Player", 0.60, 0.7, 70, 0.30, 0.60)
    normal = Player("Normal Player", 0.40, 1.0, 50, 0.45, 0.85)
    noob = Player("Noob Player", 0.30, 1.4, 40, 0.55, 0.85)
    
    players = [pro, normal, noob]
    
    for step in range(1, config.TOTAL_STEPS + 1):
        for p in players:
            p.step(step)
            
    # Plotting
    plt.figure(figsize=(14, 7))
    
    plt.plot(range(1, config.TOTAL_STEPS + 1), pro.hp_history, label=f"Pro Player HP (Deaths: {pro.deaths})", color='#2ca02c')
    plt.plot(range(1, config.TOTAL_STEPS + 1), normal.hp_history, label=f"Normal Player HP (Deaths: {normal.deaths})", color='#1f77b4')
    plt.plot(range(1, config.TOTAL_STEPS + 1), noob.hp_history, label=f"Noob Player HP (Deaths: {noob.deaths})", color='#d62728')
    
    plt.title(f"The Last of Us - {config.TOTAL_STEPS}-Step Survival Resource & Combat Simulation", fontsize=14, fontweight='bold')
    plt.xlabel("Simulation Steps", fontsize=12)
    plt.ylabel("Player HP", fontsize=12)
    
    plt.ylim(0, config.MAX_HP + 10)
    plt.axhline(y=0, color='black', linewidth=1)
    
    for step in config.BLOATER_SPAWN_STEPS:
        plt.axvline(x=step, color='purple', linestyle='--', alpha=0.3)
    
    plt.legend(loc='lower left')
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig("simulation_results.png", dpi=300)
    print(f"Simulation completed.\nDeaths -> Pro: {pro.deaths}, Normal: {normal.deaths}, Noob: {noob.deaths}")
    print("Graph saved as simulation_results.png")

if __name__ == "__main__":
    main()
