import streamlit as st
import random


class Fighter:
    def __init__(self, fighter_id, strength, dexterity, constitution,
                 damage_dice, max_hp, damage_type, speed, ac):
        self.id = fighter_id
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.damage_dice = damage_dice
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.damage_type = damage_type
        self.speed = speed
        self.position = 0 if damage_type == 'melee' else 50
        self.ac = ac
        self.retreat_count = 0

    def attack_modifier(self):
        if self.damage_type == 'melee':
            return (self.strength - 10) // 2
        else:
            return (self.dexterity - 10) // 2

    def damage_modifier(self):
        if self.damage_type == 'melee':
            return (self.strength - 10) // 2
        else:
            return (self.dexterity - 10) // 2

    def roll_attack(self):
        roll = random.randint(1, 20)
        return roll, roll + self.attack_modifier()

    def roll_damage(self, critical=False):
        num_dice, dice_type = map(int, self.damage_dice.split('d'))
        total = 0

        for _ in range(num_dice):
            total += random.randint(1, dice_type)

        if critical:
            for _ in range(num_dice):
                total += random.randint(1, dice_type)

        return max(0, total + self.damage_modifier())

    def take_damage(self, damage):
        self.current_hp -= damage

    def is_alive(self):
        return self.current_hp > 0

    def move_towards(self, target_position, forced_engage=False):
        if forced_engage:
            if self.damage_type == 'melee':
                self.position = min(self.position + self.speed, target_position)
            else:
                self.position = max(self.position - self.speed, target_position)
        else:
            if self.position < target_position:
                self.position = min(self.position + self.speed, target_position)
            elif self.position > target_position:
                if self.retreat_count < 3:
                    self.position = max(self.position - self.speed, target_position)
                    self.retreat_count += 1

    def can_attack(self, target):
        distance = abs(self.position - target.position)

        if self.damage_type == 'melee':
            return distance <= 5
        else:
            return distance <= 30


class Squad:
    def __init__(self, name):
        self.name = name
        self.fighters = []

    def add_fighter(self, fighter):
        self.fighters.append(fighter)

    def remove_dead(self):
        self.fighters = [f for f in self.fighters if f.is_alive()]

    def size(self):
        return len(self.fighters)

    def shuffle(self):
        random.shuffle(self.fighters)

    def average_position(self):
        if not self.fighters:
            return 0
        return sum(f.position for f in self.fighters) / len(self.fighters)

    def max_retreat_reached(self):
        return any(f.retreat_count >= 3 for f in self.fighters)


def simulate_battle(squad1, squad2):
    battle_log = []
    round_num = 1
    max_rounds = 50

    battle_log.append(f"\n{'=' * 50}")
    battle_log.append(f"НАЧАЛО СИМУЛЯЦИИ БИТВЫ")
    battle_log.append(f"{'=' * 50}\n")

    while squad1.size() > 0 and squad2.size() > 0 and round_num <= max_rounds:
        squad1.remove_dead()
        squad2.remove_dead()

        if squad1.size() == 0 or squad2.size() == 0:
            break

        squad1.shuffle()
        squad2.shuffle()

        status = f"Раунд {round_num}: {squad1.name}[{squad1.size()}] vs {squad2.name}[{squad2.size()}]"
        battle_log.append(status)
        battle_log.append("-" * len(status))

        forced_engage = squad1.max_retreat_reached() or squad2.max_retreat_reached()

        avg_pos1 = squad1.average_position()
        avg_pos2 = squad2.average_position()

        for fighter in squad1.fighters:
            fighter.move_towards(avg_pos2, forced_engage)

        for fighter in squad2.fighters:
            fighter.move_towards(avg_pos1, forced_engage)

        # Фаза атаки: отряд 1 атакует отряд 2
        for attacker in squad1.fighters:
            if squad2.size() == 0:
                break

            defender = min(squad2.fighters,
                           key=lambda x: abs(attacker.position - x.position))

            if not attacker.can_attack(defender):
                distance = abs(attacker.position - defender.position)
                battle_log.append(
                    f"  {attacker.id} не может атаковать {defender.id} (расстояние: {distance:.1f} футов)")
                continue

            attack_roll, total_attack = attacker.roll_attack()
            critical = (attack_roll == 20)
            hit = False

            if attack_roll == 1:
                result = "Критический промах!"
            elif total_attack >= defender.ac or critical:
                hit = True
                damage = attacker.roll_damage(critical)
                defender.take_damage(damage)
                result = f"Попадание! Урон: {damage} | {'Крит!' if critical else ''}"
            else:
                result = "Промах!"

            battle_log.append(f"  {attacker.id} -> {defender.id}: {result}")

            if hit and not defender.is_alive():
                battle_log.append(f"  {defender.id} УБИТ!")

        # Фаза атаки: отряд 2 атакует отряд 1
        for attacker in squad2.fighters:
            if squad1.size() == 0:
                break

            defender = min(squad1.fighters,
                           key=lambda x: abs(attacker.position - x.position))

            if not attacker.can_attack(defender):
                distance = abs(attacker.position - defender.position)
                battle_log.append(
                    f"  {attacker.id} не может атаковать {defender.id} (расстояние: {distance:.1f} футов)")
                continue

            attack_roll, total_attack = attacker.roll_attack()
            critical = (attack_roll == 20)
            hit = False

            if attack_roll == 1:
                result = "Критический промах!"
            elif total_attack >= defender.ac or critical:
                hit = True
                damage = attacker.roll_damage(critical)
                defender.take_damage(damage)
                result = f"Попадание! Урон: {damage} | {'Крит!' if critical else ''}"
            else:
                result = "Промах!"

            battle_log.append(f"  {attacker.id} -> {defender.id}: {result}")

            if hit and not defender.is_alive():
                battle_log.append(f"  {defender.id} УБИТ!")

        battle_log.append(
            f"Позиции: {squad1.name} на {squad1.average_position():.1f}, {squad2.name} на {squad2.average_position():.1f}")
        battle_log.append(
            f"Отступление: {squad1.name}[{squad1.max_retreat_reached()}] {squad2.name}[{squad2.max_retreat_reached()}]")
        battle_log.append("")
        round_num += 1

    squad1.remove_dead()
    squad2.remove_dead()

    battle_log.append(f"{'=' * 50}")
    battle_log.append("РЕЗУЛЬТАТ БИТВЫ:")
    battle_log.append(f"{'=' * 50}")
    battle_log.append(f"Отряд {squad1.name}: {squad1.size()} выживших")
    battle_log.append(f"Отряд {squad2.name}: {squad2.size()} выживших")

    if squad1.size() > squad2.size():
        battle_log.append(f"ПОБЕДИТЕЛЬ: ОТРЯД {squad1.name}")
    elif squad2.size() > squad1.size():
        battle_log.append(f"ПОБЕДИТЕЛЬ: ОТРЯД {squad2.name}")
    else:
        battle_log.append("НИЧЬЯ!")
    battle_log.append(f"{'=' * 50}")

    return battle_log, squad1.size(), squad2.size()


def create_squad(name, params):
    squad = Squad(name)
    for i in range(params['squad_size']):
        fighter_id = f"{name}-{i + 1}"
        fighter = Fighter(
            fighter_id=fighter_id,
            strength=params['strength'],
            dexterity=params['dexterity'],
            constitution=params['constitution'],
            damage_dice=params['damage_dice'],
            max_hp=params['max_hp'],
            damage_type=params['damage_type'],
            speed=params['speed'],
            ac=params['ac']
        )
        squad.add_fighter(fighter)
    return squad


def main():
    st.title("🎮 Симулятор массовых битв D&D")
    st.markdown("""
    ### Правила симуляции:
    - Каждый отряд состоит из одинаковых бойцов
    - Ближние бойцы (melee) начинают на позиции 0
    - Дальние бойцы (ranged) начинают на позиции 50
    - Максимум 3 раунда отступления
    - После 3 раундов бойцы обязаны вступить в бой
    """)

    st.sidebar.header("Настройки симуляции")
    max_rounds = st.sidebar.slider("Максимальное число раундов", 10, 100, 50)

    col1, col2 = st.columns(2)

    with col1:
        st.header("Отряд A")
        squad_a_params = {
            'strength': st.number_input("Сила", min_value=1, max_value=30, value=10, key="a_str"),
            'dexterity': st.number_input("Ловкость", min_value=1, max_value=30, value=10, key="a_dex"),
            'constitution': st.number_input("Телосложение", min_value=1, max_value=30, value=10, key="a_con"),
            'ac': st.number_input("Класс доспеха (AC)", min_value=1, max_value=30, value=10, key="a_ac"),
            'damage_dice': st.text_input("Кость урона (NdN)", value="1d8", key="a_dmg"),
            'max_hp': st.number_input("ХП бойца", min_value=1, max_value=200, value=10, key="a_hp"),
            'damage_type': st.radio("Тип урона", ["melee", "ranged"], key="a_type"),
            'speed': st.slider("Скорость (футы)", 5, 60, 30, key="a_speed"),
            'squad_size': st.slider("Численность отряда", 1, 1500, 10, key="a_size")
        }

    with col2:
        st.header("Отряд B")
        squad_b_params = {
            'strength': st.number_input("Сила", min_value=1, max_value=30, value=10, key="b_str"),
            'dexterity': st.number_input("Ловкость", min_value=1, max_value=30, value=10, key="b_dex"),
            'constitution': st.number_input("Телосложение", min_value=1, max_value=30, value=10, key="b_con"),
            'ac': st.number_input("Класс доспеха (AC)", min_value=1, max_value=30, value=10, key="b_ac"),
            'damage_dice': st.text_input("Кость урона (NdN)", value="1d8", key="b_dmg"),
            'max_hp': st.number_input("ХП бойца", min_value=1, max_value=200, value=10, key="b_hp"),
            'damage_type': st.radio("Тип урона", ["melee", "ranged"], key="b_type"),
            'speed': st.slider("Скорость (футы)", 5, 60, 30, key="b_speed"),
            'squad_size': st.slider("Численность отряда", 1, 1500, 10, key="b_size")
        }

    if st.button("🚀 Начать симуляцию битвы"):
        with st.spinner("Идет симуляция боя..."):
            squad_a = create_squad("A", squad_a_params)
            squad_b = create_squad("B", squad_b_params)
            battle_log, survivors_a, survivors_b = simulate_battle(squad_a, squad_b)

        st.success("Симуляция завершена!")

        # Отображение результатов
        col1, col2 = st.columns(2)
        col1.metric(f"Выжившие в отряде A", survivors_a)
        col2.metric(f"Выжившие в отряде B", survivors_b)

        if survivors_a > survivors_b:
            st.success(f"🏆 ПОБЕДИТЕЛЬ: ОТРЯД A ({survivors_a} vs {survivors_b})")
        elif survivors_b > survivors_a:
            st.success(f"🏆 ПОБЕДИТЕЛЬ: ОТРЯД B ({survivors_b} vs {survivors_a})")
        else:
            st.info("⚔️ НИЧЬЯ!")

        # Детализированный журнал боя
        with st.expander("📜 Показать детали боя"):
            for line in battle_log:
                st.text(line)


if __name__ == "__main__":
    main()