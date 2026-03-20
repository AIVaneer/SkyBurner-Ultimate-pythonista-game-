"""
╔══════════════════════════════════════════════════════════╗
║              ATLAS NEXUS ENGINE  v1.0                    ║
║              PCVR STUDIOS                                ║
║   Core game engine powering SkyBurner Ultimate           ║
╚══════════════════════════════════════════════════════════╝

Provides:
  - Entity / Component system
  - Axis-Aligned Bounding-Box collision detection
  - Score & multiplier management
  - Wave / progression management
  - Central engine coordinator
"""

import math
import random
from collections import defaultdict


# ─────────────────────────────────────────────────────────
# MATH UTILITIES
# ─────────────────────────────────────────────────────────

class Vector2:
    """Lightweight 2-D vector used throughout the engine."""

    __slots__ = ('x', 'y')

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return 'Vector2({:.2f}, {:.2f})'.format(self.x, self.y)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        l = self.length()
        if l == 0:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)

    def distance_to(self, other):
        return (self - other).length()

    def to_tuple(self):
        return (self.x, self.y)


class AABB:
    """Axis-Aligned Bounding Box for fast collision detection."""

    __slots__ = ('cx', 'cy', 'hw', 'hh')

    def __init__(self, cx, cy, width, height):
        self.cx = cx
        self.cy = cy
        self.hw = width * 0.5
        self.hh = height * 0.5

    def intersects(self, other):
        return (
            abs(self.cx - other.cx) < (self.hw + other.hw) and
            abs(self.cy - other.cy) < (self.hh + other.hh)
        )


# ─────────────────────────────────────────────────────────
# ENTITY / COMPONENT SYSTEM
# ─────────────────────────────────────────────────────────

class Component:
    """Base class for all components."""

    def __init__(self):
        self.entity = None
        self.enabled = True

    def update(self, dt):
        pass


class TransformComponent(Component):
    """Owns position and velocity; integrates each frame."""

    def __init__(self, x=0.0, y=0.0):
        super().__init__()
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)

    def update(self, dt):
        if self.enabled:
            self.position = self.position + self.velocity * dt


class HealthComponent(Component):
    """Hit-points, death detection, and optional callbacks."""

    def __init__(self, max_health):
        super().__init__()
        self.max_health = max_health
        self.current_health = float(max_health)
        self.is_dead = False
        self.on_death_callbacks = []
        self.on_damage_callbacks = []

    def take_damage(self, amount):
        if self.is_dead:
            return
        self.current_health = max(0.0, self.current_health - amount)
        for cb in self.on_damage_callbacks:
            cb(amount)
        if self.current_health <= 0:
            self.is_dead = True
            for cb in self.on_death_callbacks:
                cb()

    def heal(self, amount):
        self.current_health = min(float(self.max_health),
                                  self.current_health + amount)

    @property
    def health_ratio(self):
        return self.current_health / self.max_health


class WeaponComponent(Component):
    """Fire-rate gated weapon with upgradeable fire modes."""

    WEAPON_SINGLE  = 'single'
    WEAPON_DOUBLE  = 'double'
    WEAPON_SPREAD  = 'spread'
    WEAPON_MISSILE = 'missile'

    def __init__(self, fire_rate=0.3, damage=10):
        super().__init__()
        self.fire_rate = fire_rate
        self.damage = damage
        self.weapon_type = self.WEAPON_SINGLE
        self.fire_timer = 0.0
        self.on_fire_callback = None
        self.level = 1

    def can_fire(self):
        return self.fire_timer <= 0

    def fire(self):
        if self.can_fire() and self.on_fire_callback:
            self.on_fire_callback(self.weapon_type, self.damage)
            self.fire_timer = self.fire_rate

    def upgrade(self):
        self.level += 1
        if self.level == 2:
            self.weapon_type = self.WEAPON_DOUBLE
            self.fire_rate = 0.22
        elif self.level == 3:
            self.weapon_type = self.WEAPON_SPREAD
            self.fire_rate = 0.30
        elif self.level >= 4:
            self.weapon_type = self.WEAPON_MISSILE
            self.damage = 25

    def update(self, dt):
        if self.fire_timer > 0:
            self.fire_timer -= dt


class ShieldComponent(Component):
    """Absorb-damage shield with recharge delay."""

    def __init__(self, max_shield=100):
        super().__init__()
        self.max_shield = float(max_shield)
        self.current_shield = 0.0
        self.active = False
        self.recharge_delay = 3.0
        self.recharge_timer = 0.0

    def absorb_damage(self, amount):
        if self.active and self.current_shield > 0:
            absorbed = min(amount, self.current_shield)
            self.current_shield -= absorbed
            if self.current_shield <= 0:
                self.active = False
                self.recharge_timer = self.recharge_delay
            return absorbed
        return 0

    def add_shield(self, amount):
        self.current_shield = min(self.max_shield,
                                  self.current_shield + amount)
        self.active = True

    def update(self, dt):
        if not self.active and self.recharge_timer > 0:
            self.recharge_timer -= dt

    @property
    def shield_ratio(self):
        return self.current_shield / self.max_shield


# ─────────────────────────────────────────────────────────
# ENTITY
# ─────────────────────────────────────────────────────────

class Entity:
    """Base game object.  Holds components and scene-node reference."""

    _id_counter = 0

    def __init__(self, name='entity'):
        Entity._id_counter += 1
        self.id = Entity._id_counter
        self.name = name
        self.components = {}
        self.active = True
        self.tags = set()
        self.node = None               # set by the scene layer

    def add_component(self, component):
        component.entity = self
        self.components[type(component).__name__] = component
        return component

    def get_component(self, component_type):
        return self.components.get(component_type.__name__)

    def has_component(self, component_type):
        return component_type.__name__ in self.components

    def add_tag(self, tag):
        self.tags.add(tag)

    def has_tag(self, tag):
        return tag in self.tags

    def update(self, dt):
        if self.active:
            for comp in self.components.values():
                if comp.enabled:
                    comp.update(dt)

    def destroy(self):
        self.active = False


# ─────────────────────────────────────────────────────────
# ENTITY MANAGER
# ─────────────────────────────────────────────────────────

class EntityManager:
    """Stores entities, supports tag-based querying, deferred removal."""

    def __init__(self):
        self.entities = {}
        self._by_tag = defaultdict(set)
        self._to_remove = []

    def add(self, entity):
        self.entities[entity.id] = entity
        for tag in entity.tags:
            self._by_tag[tag].add(entity.id)
        return entity

    def remove(self, entity):
        self._to_remove.append(entity.id)

    def get_by_tag(self, tag):
        ids = list(self._by_tag.get(tag, set()))
        return [self.entities[eid] for eid in ids if eid in self.entities]

    def update(self, dt):
        for eid in self._to_remove:
            entity = self.entities.pop(eid, None)
            if entity:
                for tag in entity.tags:
                    self._by_tag[tag].discard(eid)
        self._to_remove.clear()

        for entity in list(self.entities.values()):
            entity.update(dt)

    def clear(self):
        self.entities.clear()
        self._by_tag.clear()
        self._to_remove.clear()


# ─────────────────────────────────────────────────────────
# COLLISION MANAGER
# ─────────────────────────────────────────────────────────

class CollisionManager:
    """AABB collision detection between tagged entity groups."""

    def __init__(self):
        self._handlers = {}

    def register_handler(self, tag_a, tag_b, handler):
        key = tuple(sorted([tag_a, tag_b]))
        self._handlers[key] = (handler, tag_a, tag_b)

    def check_collisions(self, entity_manager):
        for key, (handler, tag_a, tag_b) in self._handlers.items():
            group_a = entity_manager.get_by_tag(tag_a)
            group_b = entity_manager.get_by_tag(tag_b)

            for ea in group_a:
                if not ea.active:
                    continue
                tc_a = ea.get_component(TransformComponent)
                if not tc_a:
                    continue
                cw_a = getattr(ea, 'collision_width', 30)
                ch_a = getattr(ea, 'collision_height', 30)
                box_a = AABB(tc_a.position.x, tc_a.position.y, cw_a, ch_a)

                for eb in group_b:
                    if not eb.active or ea is eb:
                        continue
                    tc_b = eb.get_component(TransformComponent)
                    if not tc_b:
                        continue
                    cw_b = getattr(eb, 'collision_width', 30)
                    ch_b = getattr(eb, 'collision_height', 30)
                    box_b = AABB(tc_b.position.x, tc_b.position.y, cw_b, ch_b)

                    if box_a.intersects(box_b):
                        handler(ea, eb)


# ─────────────────────────────────────────────────────────
# SCORE MANAGER
# ─────────────────────────────────────────────────────────

class ScoreManager:
    """Tracks score, multipliers, combos, waves and levels."""

    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.multiplier = 1
        self._mult_timer = 0.0
        self._mult_duration = 5.0
        self.kills = 0
        self.wave = 1
        self.level = 1
        self.combo = 0
        self._combo_timer = 0.0
        self._combo_duration = 2.5

    def add_score(self, points):
        earned = int(points * self.multiplier)
        self.score += earned
        if self.score > self.high_score:
            self.high_score = self.score
        return earned

    def register_kill(self, base_points):
        self.kills += 1
        self.combo += 1
        self._combo_timer = self._combo_duration
        if self.combo >= 5:
            self.multiplier = min(8, self.multiplier + 1)
            self._mult_timer = self._mult_duration
            self.combo = 0
        return self.add_score(base_points)

    def update(self, dt):
        if self._mult_timer > 0:
            self._mult_timer -= dt
            if self._mult_timer <= 0:
                self.multiplier = max(1, self.multiplier - 1)
        if self._combo_timer > 0:
            self._combo_timer -= dt
            if self._combo_timer <= 0:
                self.combo = 0

    def next_wave(self):
        self.wave += 1
        if self.wave % 5 == 0:
            self.level += 1

    def reset(self):
        self.score = 0
        self.multiplier = 1
        self._mult_timer = 0.0
        self.kills = 0
        self.wave = 1
        self.level = 1
        self.combo = 0
        self._combo_timer = 0.0


# ─────────────────────────────────────────────────────────
# WAVE MANAGER
# ─────────────────────────────────────────────────────────

class WaveManager:
    """Drives enemy spawning in timed waves."""

    def __init__(self):
        self.wave_number = 1
        self.enemies_remaining = 0
        self.enemies_spawned = 0
        self.wave_complete = False
        self._spawn_timer = 0.0
        self._wave_data = []
        self.is_boss_wave = False
        self.on_enemy_spawn = None
        self.on_wave_complete = None

    def start_wave(self, wave_number):
        self.wave_number = wave_number
        self.wave_complete = False
        self.enemies_spawned = 0
        self._spawn_timer = 0.0
        self.is_boss_wave = (wave_number % 5 == 0)
        self._wave_data = self._build_wave(wave_number)
        self.enemies_remaining = len(self._wave_data)

    def _build_wave(self, wave):
        entries = []
        if wave % 5 == 0:
            entries.append({'type': 'boss',    'delay': 1.0})
            for i in range(4):
                entries.append({'type': 'fighter', 'delay': 2.0 + i * 0.6})
        else:
            num_fighters = 3 + wave * 2
            num_cruisers = max(0, wave - 2)
            for i in range(num_fighters):
                entries.append({'type': 'fighter', 'delay': i * 0.7})
            for i in range(num_cruisers):
                entries.append({
                    'type': 'cruiser',
                    'delay': num_fighters * 0.7 + i * 1.4
                })
        return entries

    def update(self, dt):
        if self.wave_complete:
            return
        self._spawn_timer += dt
        while self.enemies_spawned < len(self._wave_data):
            entry = self._wave_data[self.enemies_spawned]
            if self._spawn_timer >= entry.get('delay', 0):
                if self.on_enemy_spawn:
                    self.on_enemy_spawn(entry)
                self.enemies_spawned += 1
            else:
                break

    def enemy_destroyed(self):
        self.enemies_remaining = max(0, self.enemies_remaining - 1)
        if (self.enemies_remaining == 0 and
                self.enemies_spawned >= len(self._wave_data)):
            self.wave_complete = True
            if self.on_wave_complete:
                self.on_wave_complete(self.wave_number)

    def reset(self):
        self.wave_number = 1
        self.enemies_remaining = 0
        self.enemies_spawned = 0
        self.wave_complete = False
        self._spawn_timer = 0.0
        self._wave_data = []


# ─────────────────────────────────────────────────────────
# ATLAS NEXUS ENGINE  — top-level coordinator
# ─────────────────────────────────────────────────────────

class AtlasNexusEngine:
    """
    Top-level coordinator for all Atlas Nexus subsystems.

    Usage::

        engine = AtlasNexusEngine()
        engine.start()
        # in scene update():
        engine.update(dt)
    """

    VERSION = '1.0.0'
    STUDIO  = 'PCVR STUDIOS'

    def __init__(self):
        self.entity_manager   = EntityManager()
        self.collision_manager = CollisionManager()
        self.score_manager    = ScoreManager()
        self.wave_manager     = WaveManager()
        self.running = False
        self.paused  = False

    def start(self):
        self.running = True

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False

    def update(self, dt):
        if not self.running or self.paused:
            return
        self.entity_manager.update(dt)
        self.collision_manager.check_collisions(self.entity_manager)
        self.score_manager.update(dt)
        self.wave_manager.update(dt)

    def reset(self):
        self.entity_manager.clear()
        self.score_manager.reset()
        self.wave_manager.reset()
        self.running = True
        self.paused  = False

    def __repr__(self):
        return 'AtlasNexusEngine v{} by {}'.format(self.VERSION, self.STUDIO)
