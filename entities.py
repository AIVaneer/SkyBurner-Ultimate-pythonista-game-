"""
╔══════════════════════════════════════════════════════════╗
║      SKYBURNER ULTIMATE — Game Entities & Visuals        ║
║      PCVR STUDIOS  ×  Atlas Nexus Engine                 ║
╚══════════════════════════════════════════════════════════╝

Contains:
  - Pure-logic entity classes  (PlayerEntity, EnemyFighterEntity, …)
  - Visual node builder helpers (make_player_ship_node, …)

The visual helpers create scene.Node trees from ui.Path shapes so
that no external image assets are needed.  This keeps the game fully
self-contained inside Pythonista 3.
"""

import math
import random

# Pythonista 3 scene / ui imports
from scene import ShapeNode, LabelNode, Node, Action, Color
import ui

# Engine imports
from atlas_nexus import (
    Entity, TransformComponent, HealthComponent,
    WeaponComponent, ShieldComponent,
    Vector2 as V2,
)


# ─────────────────────────────────────────────────────────
# VISUAL NODE BUILDERS
# ─────────────────────────────────────────────────────────

def make_player_ship_node():
    """Return a Node tree that looks like the player's fighter jet."""
    root = Node()

    # Main hull — a sleek arrowhead
    hull = ui.Path()
    hull.move_to(0,   28)
    hull.line_to(-18, -10)
    hull.line_to(-7,  -4)
    hull.line_to(0,  -18)
    hull.line_to(7,   -4)
    hull.line_to(18, -10)
    hull.close()
    body = ShapeNode(hull,
                     fill_color=Color(0.05, 0.55, 1.0),
                     stroke_color=Color(0.4, 0.85, 1.0))
    body.line_width = 1.5
    root.add_child(body)

    # Engine glow
    glow_path = ui.Path.oval(-7, -26, 14, 10)
    glow = ShapeNode(glow_path,
                     fill_color=Color(1.0, 0.45, 0.0),
                     stroke_color=Color(1.0, 0.75, 0.0))
    glow.z_position = -1
    root.add_child(glow)

    # Cockpit canopy
    canopy_path = ui.Path.oval(-5, 4, 10, 11)
    canopy = ShapeNode(canopy_path,
                       fill_color=Color(0.0, 0.95, 0.95),
                       stroke_color=Color(0.6, 1.0, 1.0))
    root.add_child(canopy)

    return root


def make_enemy_fighter_node():
    """Enemy fighter — downward-pointing crimson dart."""
    root = Node()

    hull = ui.Path()
    hull.move_to(0,  -24)
    hull.line_to(17,  10)
    hull.line_to(7,    4)
    hull.line_to(0,   14)
    hull.line_to(-7,   4)
    hull.line_to(-17, 10)
    hull.close()
    body = ShapeNode(hull,
                     fill_color=Color(0.75, 0.08, 0.08),
                     stroke_color=Color(1.0, 0.35, 0.2))
    body.line_width = 1.5
    root.add_child(body)

    eye = ShapeNode(ui.Path.oval(-4, -9, 8, 8),
                    fill_color=Color(1.0, 0.9, 0.0),
                    stroke_color=Color(1.0, 1.0, 1.0))
    root.add_child(eye)
    return root


def make_enemy_cruiser_node():
    """Enemy cruiser — wide winged battleship."""
    root = Node()

    hull_path = ui.Path.rect(-22, -14, 44, 28)
    hull = ShapeNode(hull_path,
                     fill_color=Color(0.45, 0.04, 0.04),
                     stroke_color=Color(1.0, 0.25, 0.1))
    hull.line_width = 2
    root.add_child(hull)

    for side in (-1, 1):
        wing = ui.Path()
        wing.move_to(side * 22,  6)
        wing.line_to(side * 46, 16)
        wing.line_to(side * 46, -14)
        wing.line_to(side * 22, -6)
        wing.close()
        w_node = ShapeNode(wing,
                           fill_color=Color(0.32, 0.03, 0.03),
                           stroke_color=Color(1.0, 0.25, 0.1))
        root.add_child(w_node)

    dome = ShapeNode(ui.Path.oval(-10, -7, 20, 14),
                     fill_color=Color(0.9, 0.1, 0.1),
                     stroke_color=Color(1.0, 0.5, 0.5))
    root.add_child(dome)
    return root


def make_boss_node():
    """Boss ship — massive eight-pointed death machine."""
    root = Node()

    hull = ui.Path()
    pts = [
        (0, -58), (20, -38), (55,  0), (20, 38),
        (0,  58), (-20, 38), (-55, 0), (-20, -38),
    ]
    hull.move_to(*pts[0])
    for p in pts[1:]:
        hull.line_to(*p)
    hull.close()
    body = ShapeNode(hull,
                     fill_color=Color(0.22, 0.0, 0.0),
                     stroke_color=Color(1.0, 0.0, 0.0))
    body.line_width = 2.5
    root.add_child(body)

    core = ShapeNode(ui.Path.oval(-18, -18, 36, 36),
                     fill_color=Color(1.0, 0.0, 0.0),
                     stroke_color=Color(1.0, 0.5, 0.0))
    root.add_child(core)

    inner = ShapeNode(ui.Path.oval(-9, -9, 18, 18),
                      fill_color=Color(1.0, 1.0, 0.0),
                      stroke_color=Color(1.0, 1.0, 1.0))
    inner.name = 'inner_core'
    root.add_child(inner)
    return root


def make_bullet_node(color='#ffff00', radius=3):
    """Glowing energy bolt for bullets."""
    path = ui.Path.oval(-radius, -radius * 1.8, radius * 2, radius * 3.5)
    return ShapeNode(path,
                     fill_color=Color(color),
                     stroke_color=Color(1, 1, 1, 0.6))


def make_missile_node():
    """Player missile with body, nose tip, and fins."""
    root = Node()

    body = ShapeNode(ui.Path.rect(-3, -11, 6, 18),
                     fill_color=Color(0.7, 0.7, 0.75),
                     stroke_color=Color(1, 1, 1, 0.7))
    root.add_child(body)

    tip = ui.Path()
    tip.move_to(0,  9)
    tip.line_to(-3, 4)
    tip.line_to(3,  4)
    tip.close()
    tip_node = ShapeNode(tip,
                         fill_color=Color(1.0, 0.3, 0.0),
                         stroke_color=Color(1.0, 0.7, 0.0))
    root.add_child(tip_node)

    for side in (-1, 1):
        fin = ui.Path()
        fin.move_to(side * 3,  -6)
        fin.line_to(side * 8,  -11)
        fin.line_to(side * 3,  -11)
        fin.close()
        fin_node = ShapeNode(fin,
                             fill_color=Color(0.5, 0.5, 0.55),
                             stroke_color=Color(0.8, 0.8, 0.9))
        root.add_child(fin_node)
    return root


_POWERUP_COLORS = {
    'weapon': '#00ff44',
    'shield': '#0088ff',
    'health': '#ff1177',
    'bomb':   '#ff8800',
    'speed':  '#ffff00',
}

_POWERUP_ICONS = {
    'weapon': 'W',
    'shield': 'S',
    'health': '+',
    'bomb':   'B',
    'speed':  'V',
}


def make_powerup_node(ptype):
    """Pulsing collectible power-up with coloured ring + letter."""
    color_hex = _POWERUP_COLORS.get(ptype, '#ffffff')
    letter    = _POWERUP_ICONS.get(ptype, '?')
    c = Color(color_hex)

    root = Node()

    ring = ShapeNode(ui.Path.oval(-15, -15, 30, 30),
                     fill_color=Color(c.r, c.g, c.b, 0.15),
                     stroke_color=c)
    ring.line_width = 2
    root.add_child(ring)

    icon = LabelNode(letter,
                     font=('Courier-Bold', 14),
                     color=c)
    icon.anchor_point = (0.5, 0.5)
    root.add_child(icon)

    root.run_action(Action.repeat(
        Action.sequence(
            Action.scale_to(1.18, 0.45),
            Action.scale_to(0.88, 0.45),
        )
    ))
    return root


def make_explosion_node(size=40, color='#ff6600'):
    """Animated explosion that removes itself after playing."""
    root = Node()
    c = Color(color)

    center = ShapeNode(ui.Path.oval(-size * 0.28, -size * 0.28,
                                    size * 0.56,  size * 0.56),
                       fill_color=Color(1, 1, 0.3, 0.9),
                       stroke_color=None)
    root.add_child(center)

    for i in range(8):
        angle = (i / 8.0) * math.pi * 2
        r = size * 0.45
        spark = ShapeNode(ui.Path.oval(-2.5, -2.5, 5, 5),
                          fill_color=c,
                          stroke_color=Color(1, 1, 0, 0.5))
        spark.position = (math.cos(angle) * r, math.sin(angle) * r)
        root.add_child(spark)

    root.run_action(Action.sequence(
        Action.scale_to(1.6, 0.18),
        Action.fade_to(0,   0.28),
        Action.remove(),
    ))
    return root


def make_shield_node(radius=34):
    """Translucent shield bubble attached to the player node."""
    path = ui.Path.oval(-radius, -radius, radius * 2, radius * 2)
    shield = ShapeNode(path,
                       fill_color=Color(0.0, 0.45, 1.0, 0.18),
                       stroke_color=Color(0.0, 0.75, 1.0, 0.85))
    shield.line_width = 2
    shield.name = 'shield'
    return shield


# ─────────────────────────────────────────────────────────
# ENTITY CLASSES
# ─────────────────────────────────────────────────────────

class PlayerEntity(Entity):
    """The player's ship — tracks input target, manages invincibility."""

    def __init__(self, scene_w, scene_h):
        super().__init__('player')
        self.add_tag('player')
        self.collision_width  = 28
        self.collision_height = 38

        self.add_component(TransformComponent(scene_w * 0.5, scene_h * 0.18))
        health = HealthComponent(100)
        self.add_component(health)
        weapon = WeaponComponent(fire_rate=0.24, damage=15)
        self.add_component(weapon)
        self.add_component(ShieldComponent(max_shield=100))

        self.speed         = 320.0
        self.move_smooth   = 9.0
        self.target_x      = scene_w * 0.5
        self.target_y      = scene_h * 0.18

        self.invincible          = False
        self.invincible_timer    = 0.0
        self.invincible_duration = 2.2

        self.bombs         = 3
        self.speed_boost   = 1.0
        self._speed_timer  = 0.0

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def take_hit(self, amount):
        if self.invincible:
            return
        shield = self.get_component(ShieldComponent)
        health = self.get_component(HealthComponent)
        if shield and shield.active:
            amount -= shield.absorb_damage(amount)
        if amount > 0 and health:
            health.take_damage(amount)
            if not health.is_dead:
                self.invincible       = True
                self.invincible_timer = self.invincible_duration

    def use_bomb(self):
        if self.bombs > 0:
            self.bombs -= 1
            return True
        return False

    def update(self, dt):
        super().update(dt)
        tc = self.get_component(TransformComponent)
        if tc:
            dx = self.target_x - tc.position.x
            dy = self.target_y - tc.position.y
            f  = self.move_smooth * dt
            tc.position.x += dx * f
            tc.position.y += dy * f

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if self._speed_timer > 0:
            self._speed_timer -= dt
            if self._speed_timer <= 0:
                self.speed_boost = 1.0

    def apply_speed_boost(self):
        self.speed_boost  = 1.85
        self._speed_timer = 5.0


class EnemyFighterEntity(Entity):
    """Basic enemy fighter with three movement patterns."""

    def __init__(self, x, y, level=1):
        super().__init__('enemy_fighter')
        self.add_tag('enemy')
        self.collision_width  = 28
        self.collision_height = 28
        self.score_value      = 100

        self.add_component(TransformComponent(x, y))
        self.add_component(HealthComponent(20 + level * 10))
        weapon = WeaponComponent(fire_rate=max(0.6, 2.0 - level * 0.08),
                                 damage=10)
        self.add_component(weapon)

        self._pattern      = random.choice(['straight', 'sine', 'dive'])
        self._pattern_t    = 0.0
        self._base_x       = x
        self._speed_y      = -(85 + level * 8)
        self._amp_x        = 55.0

    def update(self, dt):
        super().update(dt)
        tc = self.get_component(TransformComponent)
        if not tc:
            return
        self._pattern_t += dt

        if self._pattern == 'sine':
            tc.position.x   = self._base_x + math.sin(self._pattern_t * 1.8) * self._amp_x
            tc.velocity.y   = self._speed_y
        elif self._pattern == 'dive':
            tc.velocity.y   = self._speed_y * (1.0 + self._pattern_t * 0.25)
        else:
            tc.velocity.y   = self._speed_y


class EnemyCruiserEntity(Entity):
    """Tougher cruiser that enters, then patrols horizontally."""

    def __init__(self, x, y, level=1):
        super().__init__('enemy_cruiser')
        self.add_tag('enemy')
        self.collision_width  = 60
        self.collision_height = 34
        self.score_value      = 300

        self.add_component(TransformComponent(x, y))
        self.add_component(HealthComponent(60 + level * 20))
        weapon = WeaponComponent(fire_rate=max(0.8, 1.6 - level * 0.05),
                                 damage=15)
        self.add_component(weapon)

        self._speed_y  = -(50 + level * 4)
        self._patrol_y = None          # set on first update
        self._patrol_t = 0.0

    def update(self, dt):
        super().update(dt)
        tc = self.get_component(TransformComponent)
        if not tc:
            return

        if self._patrol_y is None:
            self._patrol_y = tc.position.y - 110

        if tc.position.y > self._patrol_y:
            tc.velocity.y = self._speed_y
            tc.velocity.x = 0
        else:
            tc.velocity.y   = 0
            self._patrol_t += dt
            tc.velocity.x   = math.sin(self._patrol_t * 0.9) * 55


class BossEntity(Entity):
    """Multi-phase boss with entry, two attack phases, and rage mode."""

    PHASE_ENTRY   = 'entry'
    PHASE_ATK1    = 'atk1'
    PHASE_ATK2    = 'atk2'
    PHASE_RAGE    = 'rage'

    def __init__(self, x, y, scene_w, scene_h, level=1):
        super().__init__('boss')
        self.add_tag('enemy')
        self.add_tag('boss')
        self.collision_width  = 78
        self.collision_height = 78
        self.score_value      = 2000 + level * 500

        self.add_component(TransformComponent(x, y))
        self.add_component(HealthComponent(500 + level * 100))
        weapon = WeaponComponent(fire_rate=max(0.3, 0.6 - level * 0.02),
                                 damage=20)
        self.add_component(weapon)

        self._phase     = self.PHASE_ENTRY
        self._phase_t   = 0.0
        self._entry_y   = scene_h * 0.76
        self._speed     = 110.0

    def update(self, dt):
        super().update(dt)
        tc     = self.get_component(TransformComponent)
        health = self.get_component(HealthComponent)
        if not tc or not health:
            return

        self._phase_t += dt
        ratio = health.health_ratio

        if self._phase == self.PHASE_ENTRY:
            if tc.position.y > self._entry_y:
                tc.velocity.y = -85
            else:
                tc.velocity.y = 0
                self._phase   = self.PHASE_ATK1

        elif self._phase == self.PHASE_ATK1:
            if ratio < 0.5:
                self._phase = self.PHASE_ATK2
            tc.velocity.x = math.sin(self._phase_t * 0.55) * self._speed
            tc.velocity.y = 0

        elif self._phase == self.PHASE_ATK2:
            if ratio < 0.2:
                self._phase = self.PHASE_RAGE
            tc.velocity.x = math.sin(self._phase_t * 1.1) * self._speed * 1.5
            tc.velocity.y = math.sin(self._phase_t * 2.2) * 28

        elif self._phase == self.PHASE_RAGE:
            tc.velocity.x = math.sin(self._phase_t * 2.2) * self._speed * 2.0
            tc.velocity.y = math.cos(self._phase_t * 1.6) * 55


class BulletEntity(Entity):
    """Player projectile."""

    def __init__(self, x, y, angle_deg=90, speed=620, damage=15):
        super().__init__('bullet')
        self.add_tag('player_bullet')
        self.collision_width  = 6
        self.collision_height = 12
        self.damage = damage

        tc = TransformComponent(x, y)
        rad = math.radians(angle_deg)
        tc.velocity = V2(math.cos(rad) * speed, math.sin(rad) * speed)
        self.add_component(tc)

        self._lifetime = 3.0
        self._timer    = 0.0

    def update(self, dt):
        super().update(dt)
        self._timer += dt
        if self._timer >= self._lifetime:
            self.active = False


class MissileEntity(Entity):
    """Homing missile that steers toward a target entity."""

    def __init__(self, x, y, target=None, damage=45):
        super().__init__('missile')
        self.add_tag('player_bullet')
        self.collision_width  = 8
        self.collision_height = 16
        self.damage  = damage
        self.target  = target
        self._speed  = 420.0
        self._steer  = 2.8

        tc = TransformComponent(x, y)
        tc.velocity = V2(0, self._speed)
        self.add_component(tc)

        self._lifetime = 4.0
        self._timer    = 0.0

    def update(self, dt):
        super().update(dt)
        self._timer += dt
        if self._timer >= self._lifetime:
            self.active = False
            return

        tc = self.get_component(TransformComponent)
        if tc and self.target and self.target.active:
            ttc = self.target.get_component(TransformComponent)
            if ttc:
                dx = ttc.position.x - tc.position.x
                dy = ttc.position.y - tc.position.y
                wanted  = math.atan2(dy, dx)
                current = math.atan2(tc.velocity.y, tc.velocity.x)
                diff = wanted - current
                while diff >  math.pi:
                    diff -= 2 * math.pi
                while diff < -math.pi:
                    diff += 2 * math.pi
                new_ang = current + diff * self._steer * dt
                tc.velocity.x = math.cos(new_ang) * self._speed
                tc.velocity.y = math.sin(new_ang) * self._speed


class EnemyBulletEntity(Entity):
    """Enemy projectile."""

    def __init__(self, x, y, angle_deg=-90, speed=230, damage=10):
        super().__init__('enemy_bullet')
        self.add_tag('enemy_bullet')
        self.collision_width  = 6
        self.collision_height = 12
        self.damage = damage

        tc = TransformComponent(x, y)
        rad = math.radians(angle_deg)
        tc.velocity = V2(math.cos(rad) * speed, math.sin(rad) * speed)
        self.add_component(tc)

        self._lifetime = 4.0
        self._timer    = 0.0

    def update(self, dt):
        super().update(dt)
        self._timer += dt
        if self._timer >= self._lifetime:
            self.active = False


class PowerUpEntity(Entity):
    """Collectible power-up that drifts downward and expires."""

    TYPES = ['weapon', 'shield', 'health', 'bomb', 'speed']

    def __init__(self, x, y, ptype=None):
        super().__init__('powerup')
        self.add_tag('powerup')
        self.collision_width  = 30
        self.collision_height = 30
        self.ptype = ptype or random.choice(self.TYPES)

        tc = TransformComponent(x, y)
        tc.velocity = V2(0, -55)
        self.add_component(tc)

        self._lifetime = 9.0
        self._timer    = 0.0

    def update(self, dt):
        super().update(dt)
        self._timer += dt
        if self._timer >= self._lifetime:
            self.active = False
