"""
╔══════════════════════════════════════════════════════════════════╗
║  ███████╗██╗  ██╗██╗   ██╗██████╗ ██╗   ██╗██████╗ ███╗   ██╗  ║
║  ██╔════╝██║ ██╔╝╚██╗ ██╔╝██╔══██╗██║   ██║██╔══██╗████╗  ██║  ║
║  ███████╗█████╔╝  ╚████╔╝ ██████╔╝██║   ██║██████╔╝██╔██╗ ██║  ║
║  ╚════██║██╔═██╗   ╚██╔╝  ██╔══██╗██║   ██║██╔══██╗██║╚██╗██║  ║
║  ███████║██║  ██╗   ██║   ██████╔╝╚██████╔╝██║  ██║██║ ╚████║  ║
║  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝  ║
║                          ULTIMATE                                ║
║                PCVR STUDIOS  ×  Atlas Nexus Engine               ║
╚══════════════════════════════════════════════════════════════════╝

The most intense arcade shooter for Pythonista 3 & iOS Devices.

HOW TO PLAY
  • Drag the LEFT half of the screen  →  move your ship
  • Tap  the RIGHT half of the screen  →  detonate a BOMB
  • Your ship fires automatically

TIPS
  • Destroy enemies quickly to build combos and raise your multiplier
  • Every 5th wave is a BOSS wave — be ready!
  • Collect coloured capsules for weapon upgrades, shields, health,
    extra bombs, and speed boosts

RUN
  Open skyburner.py in Pythonista 3 and tap the Run button.
"""

import math
import random

from scene import (
    Scene, ShapeNode, LabelNode, Node,
    Action, Color, run, PORTRAIT,
)
import ui

from atlas_nexus import (
    AtlasNexusEngine,
    TransformComponent,
    HealthComponent,
    WeaponComponent,
    ShieldComponent,
)
from entities import (
    PlayerEntity,
    EnemyFighterEntity,
    EnemyCruiserEntity,
    BossEntity,
    BulletEntity,
    MissileEntity,
    EnemyBulletEntity,
    PowerUpEntity,
    make_player_ship_node,
    make_enemy_fighter_node,
    make_enemy_cruiser_node,
    make_boss_node,
    make_bullet_node,
    make_missile_node,
    make_powerup_node,
    make_explosion_node,
    make_shield_node,
)


# ─────────────────────────────────────────────────────────
# SCROLLING STAR FIELD
# ─────────────────────────────────────────────────────────

class StarField(Node):
    """Parallax star-field background."""

    def __init__(self, w, h, num_stars=110):
        super().__init__()
        self._w = w
        self._h = h
        self._stars = []
        for _ in range(num_stars):
            self._add_star(initial=True)

    def _add_star(self, initial=False):
        size       = random.uniform(0.8, 2.8)
        speed      = random.uniform(38, 210)
        brightness = random.uniform(0.25, 1.0)

        x = random.uniform(0, self._w)
        y = random.uniform(0, self._h) if initial else self._h + 8

        star = ShapeNode(
            ui.Path.oval(-size, -size, size * 2, size * 2),
            fill_color=Color(brightness, brightness,
                             min(1.0, brightness + 0.15),
                             brightness),
            stroke_color=None,
        )
        star.position = (x, y)
        star._speed   = speed
        self.add_child(star)
        self._stars.append(star)

    def update(self, dt):
        for star in self._stars:
            x, y = star.position
            y -= star._speed * dt
            if y < -8:
                y = self._h + 8
                x = random.uniform(0, self._w)
            star.position = (x, y)


# ─────────────────────────────────────────────────────────
# HUD
# ─────────────────────────────────────────────────────────

class HUD(Node):
    """Heads-Up Display — score, health, shield, wave, lives, bombs."""

    def __init__(self, w, h):
        super().__init__()
        self._w = w
        self._h = h
        self._max_bar  = 120.0
        self._lives    = 3

        # ── score ──────────────────────────────────────
        self._score_lbl = LabelNode(
            '0', font=('Courier-Bold', 22), color=Color('white'))
        self._score_lbl.position      = (w * 0.5, h - 28)
        self._score_lbl.anchor_point  = (0.5, 0.5)
        self.add_child(self._score_lbl)

        score_title = LabelNode(
            'SCORE', font=('Courier', 9), color=Color(0.5, 0.5, 0.55))
        score_title.position     = (w * 0.5, h - 14)
        score_title.anchor_point = (0.5, 0.5)
        self.add_child(score_title)

        self._hi_lbl = LabelNode(
            'HI: 0', font=('Courier', 13), color=Color(1.0, 0.8, 0.0))
        self._hi_lbl.position     = (w * 0.5, h - 50)
        self._hi_lbl.anchor_point = (0.5, 0.5)
        self.add_child(self._hi_lbl)

        # ── multiplier / wave (top-right) ──────────────
        self._wave_lbl = LabelNode(
            'WAVE 1', font=('Courier', 13), color=Color(0.0, 1.0, 1.0))
        self._wave_lbl.position     = (w - 8, h - 28)
        self._wave_lbl.anchor_point = (1.0, 0.5)
        self.add_child(self._wave_lbl)

        self._mult_lbl = LabelNode(
            'x1', font=('Courier-Bold', 15), color=Color(0.6, 0.6, 0.6))
        self._mult_lbl.position     = (w - 8, h - 50)
        self._mult_lbl.anchor_point = (1.0, 0.5)
        self.add_child(self._mult_lbl)

        # ── lives (top-left) ───────────────────────────
        self._lives_node = Node()
        self._lives_node.position = (10, h - 28)
        self.add_child(self._lives_node)
        self._life_icons = []
        self._rebuild_lives(3)

        # ── health bar ─────────────────────────────────
        self._hp_bg = ShapeNode(
            ui.Path.rect(0, 0, self._max_bar, 9),
            fill_color=Color(0.28, 0.0, 0.0),
            stroke_color=Color(0.7, 0.15, 0.15))
        self._hp_bg.anchor_point = (0, 0)
        self._hp_bg.position     = (10, h - 68)
        self.add_child(self._hp_bg)

        self._hp_bar = ShapeNode(
            ui.Path.rect(0, 0, self._max_bar, 9),
            fill_color=Color(0.0, 0.78, 0.0),
            stroke_color=None)
        self._hp_bar.anchor_point = (0, 0)
        self._hp_bar.position     = (10, h - 68)
        self.add_child(self._hp_bar)

        hp_label = LabelNode('HP', font=('Courier', 8), color=Color(0.6, 0.6, 0.6))
        hp_label.position     = (10 + self._max_bar + 6, h - 63)
        hp_label.anchor_point = (0, 0.5)
        self.add_child(hp_label)

        # ── shield bar ─────────────────────────────────
        self._sh_bar = ShapeNode(
            ui.Path.rect(0, 0, 0, 5),
            fill_color=Color(0.0, 0.55, 1.0),
            stroke_color=None)
        self._sh_bar.anchor_point = (0, 0)
        self._sh_bar.position     = (10, h - 77)
        self.add_child(self._sh_bar)

        # ── bombs ──────────────────────────────────────
        self._bombs_lbl = LabelNode(
            'BOMB x3', font=('Courier', 12), color=Color(1.0, 0.55, 0.0))
        self._bombs_lbl.position     = (10, h - 92)
        self._bombs_lbl.anchor_point = (0, 0.5)
        self.add_child(self._bombs_lbl)

        # ── combo ──────────────────────────────────────
        self._combo_lbl = LabelNode(
            '', font=('Courier-Bold', 20), color=Color(1, 1, 0))
        self._combo_lbl.position     = (w * 0.5, h * 0.62)
        self._combo_lbl.anchor_point = (0.5, 0.5)
        self._combo_lbl.alpha        = 0
        self.add_child(self._combo_lbl)

        # ── boss health bar (hidden) ───────────────────
        self._boss_max_w = w * 0.78
        self._boss_container = Node()
        self._boss_container.position = (w * 0.11, 32)
        self._boss_container.alpha    = 0
        self.add_child(self._boss_container)

        lbl = LabelNode('BOSS', font=('Courier-Bold', 11), color=Color(1, 0, 0))
        lbl.position     = (-28, 5)
        lbl.anchor_point = (0.5, 0.5)
        self._boss_container.add_child(lbl)

        self._boss_bg = ShapeNode(
            ui.Path.rect(0, 0, self._boss_max_w, 11),
            fill_color=Color(0.28, 0.0, 0.0),
            stroke_color=Color(1, 0, 0))
        self._boss_bg.anchor_point = (0, 0)
        self._boss_container.add_child(self._boss_bg)

        self._boss_bar = ShapeNode(
            ui.Path.rect(0, 0, self._boss_max_w, 11),
            fill_color=Color(1, 0, 0),
            stroke_color=None)
        self._boss_bar.anchor_point = (0, 0)
        self._boss_container.add_child(self._boss_bar)

    # ── internal helpers ───────────────────────────────

    def _rebuild_lives(self, count):
        for icon in self._life_icons:
            icon.remove_from_parent()
        self._life_icons = []
        for i in range(count):
            p = ui.Path()
            p.move_to(0, 9)
            p.line_to(-6, -4)
            p.line_to(6, -4)
            p.close()
            icon = ShapeNode(p,
                             fill_color=Color(0.0, 0.55, 1.0),
                             stroke_color=Color(0.3, 0.85, 1.0))
            icon.position = (i * 18, 0)
            self._lives_node.add_child(icon)
            self._life_icons.append(icon)

    # ── public update methods ──────────────────────────

    def update_score(self, score, hi_score, multiplier):
        self._score_lbl.text = '{:,}'.format(score)
        self._hi_lbl.text    = 'HI: {:,}'.format(hi_score)
        self._mult_lbl.text  = 'x{}'.format(multiplier)
        if multiplier > 1:
            self._mult_lbl.color = Color(1.0, 0.3, 0.0)
        else:
            self._mult_lbl.color = Color(0.5, 0.5, 0.5)

    def update_wave(self, wave, is_boss=False):
        if is_boss:
            self._wave_lbl.text  = 'BOSS!'
            self._wave_lbl.color = Color(1, 0.1, 0.1)
        else:
            self._wave_lbl.text  = 'WAVE {}'.format(wave)
            self._wave_lbl.color = Color(0, 1, 1)

    def update_health(self, hp_ratio, sh_ratio):
        bw = max(0.0, self._max_bar * hp_ratio)
        if hp_ratio > 0.5:
            col = Color(0.0, 0.78, 0.0)
        elif hp_ratio > 0.25:
            col = Color(1.0, 0.65, 0.0)
        else:
            col = Color(1.0, 0.05, 0.05)
        self._hp_bar.path       = ui.Path.rect(0, 0, bw, 9)
        self._hp_bar.fill_color = col
        sw = max(0.0, self._max_bar * sh_ratio)
        self._sh_bar.path = ui.Path.rect(0, 0, sw, 5)

    def update_lives(self, lives):
        self._rebuild_lives(max(0, lives))

    def update_bombs(self, bombs):
        self._bombs_lbl.text = 'BOMB x{}'.format(bombs)

    def show_combo(self, combo):
        if combo >= 3:
            self._combo_lbl.text  = '{} COMBO!'.format(combo)
            self._combo_lbl.alpha = 1
            self._combo_lbl.run_action(Action.sequence(
                Action.wait(1.4),
                Action.fade_to(0, 0.45),
            ))

    def show_boss_bar(self, visible):
        self._boss_container.alpha = 1 if visible else 0

    def update_boss_health(self, ratio):
        bw = max(0.0, self._boss_max_w * ratio)
        self._boss_bar.path = ui.Path.rect(0, 0, bw, 11)


# ─────────────────────────────────────────────────────────
# FLOATING SCORE POPUP
# ─────────────────────────────────────────────────────────

def _float_score(parent, amount, x, y, color='#ffff00'):
    lbl = LabelNode('+{:,}'.format(amount),
                    font=('Courier', 13),
                    color=Color(color))
    lbl.position   = (x, y)
    lbl.z_position = 12
    parent.add_child(lbl)
    lbl.run_action(Action.sequence(
        Action.move_by(0, 48, 0.75),
        Action.fade_to(0, 0.35),
        Action.remove(),
    ))


# ─────────────────────────────────────────────────────────
# MAIN GAME SCENE
# ─────────────────────────────────────────────────────────

class GameScene(Scene):
    """
    Top-level Pythonista Scene.

    States
    ------
    MENU             – title / high-score screen
    PLAYING          – active gameplay
    WAVE_TRANSITION  – brief pause between waves
    PAUSED           – waiting for player respawn
    GAME_OVER        – score summary + retry prompt
    """

    # state constants
    ST_MENU       = 'menu'
    ST_PLAYING    = 'playing'
    ST_WAVE_TRANS = 'wave_trans'
    ST_PAUSED     = 'paused'
    ST_GAME_OVER  = 'game_over'

    # ── lifecycle ─────────────────────────────────────

    def setup(self):
        self.background_color = Color(0.02, 0.02, 0.08)

        sw = self.size.w
        sh = self.size.h
        self._sw = sw
        self._sh = sh

        # scene-graph layers (z ordered)
        self._bg_layer  = self._make_layer(z=0)
        self._gm_layer  = self._make_layer(z=1)
        self._fx_layer  = self._make_layer(z=2)
        self._hud_layer = self._make_layer(z=3)
        self._ui_layer  = self._make_layer(z=4)

        # star field
        self._stars = StarField(sw, sh, num_stars=115)
        self._bg_layer.add_child(self._stars)

        # entity-node registry  { entity_id: scene_node }
        self._enodes = {}

        # Atlas Nexus Engine
        self._engine = AtlasNexusEngine()
        self._setup_collisions()

        # game state
        self._state          = self.ST_MENU
        self._lives          = 3
        self._boss_entity    = None
        self._player         = None          # PlayerEntity reference

        # wave-transition timer
        self._wt_timer = 0.0
        self._wt_dur   = 3.0

        # respawn
        self._respawn_timer   = 0.0
        self._pending_respawn = False

        # touch tracking
        self._move_touch  = None
        self._bomb_touch  = None

        # persistent UI references
        self._hud           = None
        self._menu_node     = None
        self._gameover_node = None

        self._show_menu()

    def _make_layer(self, z):
        node = Node()
        node.z_position = z
        self.add_child(node)
        return node

    # ── collision setup ───────────────────────────────

    def _setup_collisions(self):
        cm = self._engine.collision_manager
        cm.register_handler('player_bullet', 'enemy',
                             self._col_bullet_enemy)
        cm.register_handler('player',        'enemy',
                             self._col_player_enemy)
        cm.register_handler('player',        'enemy_bullet',
                             self._col_player_ebullet)
        cm.register_handler('player',        'powerup',
                             self._col_player_powerup)

        wm = self._engine.wave_manager
        wm.on_enemy_spawn   = self._spawn_enemy
        wm.on_wave_complete = self._on_wave_complete

    # ══════════════════════════════════════════════════
    # MENU
    # ══════════════════════════════════════════════════

    def _show_menu(self):
        self._state = self.ST_MENU
        sw, sh = self._sw, self._sh

        node = Node()
        self._menu_node = node
        self._ui_layer.add_child(node)

        # title
        t1 = LabelNode('SKY BURNER',
                       font=('Courier-Bold', 42),
                       color=Color(0.0, 0.78, 1.0))
        t1.position     = (sw * 0.5, sh * 0.76)
        t1.anchor_point = (0.5, 0.5)
        node.add_child(t1)

        t2 = LabelNode('ULTIMATE',
                       font=('Courier-Bold', 26),
                       color=Color(1.0, 0.38, 0.0))
        t2.position     = (sw * 0.5, sh * 0.68)
        t2.anchor_point = (0.5, 0.5)
        node.add_child(t2)

        tag = LabelNode('ATLAS NEXUS ENGINE  •  PCVR STUDIOS',
                        font=('Courier', 9),
                        color=Color(0.42, 0.42, 0.62))
        tag.position     = (sw * 0.5, sh * 0.622)
        tag.anchor_point = (0.5, 0.5)
        node.add_child(tag)

        sm = self._engine.score_manager
        hs = LabelNode('HIGH SCORE: {:,}'.format(sm.high_score),
                       font=('Courier', 14),
                       color=Color(1.0, 0.78, 0.0))
        hs.position     = (sw * 0.5, sh * 0.555)
        hs.anchor_point = (0.5, 0.5)
        node.add_child(hs)

        # start button
        btn_bg = ShapeNode(
            ui.Path.rounded_rect(-105, -27, 210, 54, 11),
            fill_color=Color(0.0, 0.35, 0.75),
            stroke_color=Color(0.0, 0.78, 1.0))
        btn_bg.line_width = 2
        btn_bg.position   = (sw * 0.5, sh * 0.435)
        btn_bg.run_action(Action.repeat(
            Action.sequence(
                Action.scale_to(1.06, 0.65),
                Action.scale_to(0.94, 0.65),
            )
        ))
        node.add_child(btn_bg)

        btn_lbl = LabelNode('TAP TO START',
                            font=('Courier-Bold', 20),
                            color=Color('white'))
        btn_lbl.anchor_point = (0.5, 0.5)
        btn_bg.add_child(btn_lbl)

        ctrl = LabelNode('DRAG LEFT → MOVE   TAP RIGHT → BOMB',
                         font=('Courier', 10),
                         color=Color(0.35, 0.55, 0.78))
        ctrl.position     = (sw * 0.5, sh * 0.32)
        ctrl.anchor_point = (0.5, 0.5)
        node.add_child(ctrl)

        # decorative ships
        for xf in (0.15, 0.85):
            ship = make_player_ship_node()
            ship.position = (sw * xf, sh * 0.44)
            ship.run_action(Action.repeat(
                Action.sequence(
                    Action.move_by(0,  14, 0.9),
                    Action.move_by(0, -14, 0.9),
                )
            ))
            node.add_child(ship)

    # ══════════════════════════════════════════════════
    # GAME START / RESTART
    # ══════════════════════════════════════════════════

    def _start_game(self):
        # clean up overlay nodes
        if self._menu_node:
            self._menu_node.remove_from_parent()
            self._menu_node = None
        if self._gameover_node:
            self._gameover_node.remove_from_parent()
            self._gameover_node = None

        # remove leftover game nodes
        for node in list(self._enodes.values()):
            node.remove_from_parent()
        self._enodes.clear()

        # reset engine
        self._engine.reset()
        self._lives       = 3
        self._boss_entity = None

        # HUD
        if self._hud:
            self._hud.remove_from_parent()
        self._hud = HUD(self._sw, self._sh)
        self._hud_layer.add_child(self._hud)

        # create player
        self._create_player()

        # start wave 1
        self._state = self.ST_PLAYING
        self._engine.start()
        self._engine.wave_manager.start_wave(1)
        self._show_wave_banner(1, is_boss=False)

    def _create_player(self):
        p = PlayerEntity(self._sw, self._sh)
        p.get_component(WeaponComponent).on_fire_callback = self._player_fire
        p.get_component(HealthComponent).on_death_callbacks.append(
            self._on_player_death)

        tc = p.get_component(TransformComponent)
        node = make_player_ship_node()
        node.position = tc.position.to_tuple()

        shield_node = make_shield_node()
        shield_node.alpha = 0
        node.add_child(shield_node)

        self._gm_layer.add_child(node)
        self._enodes[p.id] = node
        self._engine.entity_manager.add(p)
        self._player = p

    # ══════════════════════════════════════════════════
    # ENEMY SPAWNING
    # ══════════════════════════════════════════════════

    def _spawn_enemy(self, entry):
        etype = entry.get('type', 'fighter')
        sw, sh = self._sw, self._sh
        lvl = self._engine.score_manager.level
        x   = random.uniform(55, sw - 55)
        y   = sh + 65

        if etype == 'fighter':
            enemy = EnemyFighterEntity(x, y, lvl)
            node  = make_enemy_fighter_node()
        elif etype == 'cruiser':
            enemy = EnemyCruiserEntity(x, y, lvl)
            node  = make_enemy_cruiser_node()
        elif etype == 'boss':
            enemy = BossEntity(x, y + 80, sw, sh, lvl)
            node  = make_boss_node()
            self._boss_entity = enemy
            self._hud.show_boss_bar(True)
            self._hud.update_wave(
                self._engine.wave_manager.wave_number, is_boss=True)
        else:
            return

        enemy.get_component(WeaponComponent).on_fire_callback = (
            lambda wt, dmg, e=enemy: self._enemy_fire(e, wt, dmg)
        )

        tc = enemy.get_component(TransformComponent)
        node.position = tc.position.to_tuple()
        self._gm_layer.add_child(node)
        self._enodes[enemy.id] = node
        self._engine.entity_manager.add(enemy)

    # ══════════════════════════════════════════════════
    # FIRING
    # ══════════════════════════════════════════════════

    def _player_fire(self, weapon_type, damage):
        if not self._player or not self._player.active:
            return
        tc = self._player.get_component(TransformComponent)
        if not tc:
            return
        px, py = tc.position.x, tc.position.y

        if weapon_type == WeaponComponent.WEAPON_SINGLE:
            self._spawn_bullet(px, py + 20, 90, damage, player=True)

        elif weapon_type == WeaponComponent.WEAPON_DOUBLE:
            self._spawn_bullet(px - 11, py + 16, 90, damage, player=True)
            self._spawn_bullet(px + 11, py + 16, 90, damage, player=True)

        elif weapon_type == WeaponComponent.WEAPON_SPREAD:
            for ang in (74, 90, 106):
                self._spawn_bullet(px, py + 16, ang, damage * 0.82, player=True)

        elif weapon_type == WeaponComponent.WEAPON_MISSILE:
            enemies = self._engine.entity_manager.get_by_tag('enemy')
            target  = None
            if enemies:
                def _dist(e):
                    ttc = e.get_component(TransformComponent)
                    if not ttc:
                        return float('inf')
                    return ((ttc.position.x - px) ** 2 +
                            (ttc.position.y - py) ** 2)
                target = min(enemies, key=_dist)
            self._spawn_missile(px - 8, py + 20, target, damage * 2.2)
            self._spawn_missile(px + 8, py + 20, target, damage * 2.2)

    def _spawn_bullet(self, x, y, angle, damage, player=True):
        if player:
            ent  = BulletEntity(x, y, angle, 630, damage)
            node = make_bullet_node('#ffff00', 3)
        else:
            ent  = EnemyBulletEntity(x, y, angle, 235, damage)
            node = make_bullet_node('#ff3300', 3)
        tc = ent.get_component(TransformComponent)
        node.position = tc.position.to_tuple()
        self._gm_layer.add_child(node)
        self._enodes[ent.id] = node
        self._engine.entity_manager.add(ent)

    def _spawn_missile(self, x, y, target, damage):
        ent  = MissileEntity(x, y, target, damage)
        node = make_missile_node()
        tc   = ent.get_component(TransformComponent)
        node.position = tc.position.to_tuple()
        self._gm_layer.add_child(node)
        self._enodes[ent.id] = node
        self._engine.entity_manager.add(ent)

    def _enemy_fire(self, enemy, weapon_type, damage):
        if not enemy.active:
            return
        tc = enemy.get_component(TransformComponent)
        if not tc:
            return
        ex, ey = tc.position.x, tc.position.y

        angle = -90.0   # straight down by default
        if self._player and self._player.active:
            ptc = self._player.get_component(TransformComponent)
            if ptc:
                dx = ptc.position.x - ex
                dy = ptc.position.y - ey
                angle = math.degrees(math.atan2(dy, dx))

        if enemy.has_tag('boss'):
            for spread in (-22, 0, 22):
                self._spawn_bullet(ex, ey - 22, angle + spread,
                                   damage, player=False)
        else:
            self._spawn_bullet(ex, ey - 14, angle, damage, player=False)

    # ══════════════════════════════════════════════════
    # COLLISION HANDLERS
    # ══════════════════════════════════════════════════

    def _col_bullet_enemy(self, bullet, enemy):
        if not bullet.active or not enemy.active:
            return
        health = enemy.get_component(HealthComponent)
        if not health or health.is_dead:
            return

        health.take_damage(bullet.damage)
        self._hit_flash(enemy)

        if enemy.has_tag('boss'):
            self._hud.update_boss_health(health.health_ratio)

        bullet.active = False
        node = self._enodes.pop(bullet.id, None)
        if node:
            node.remove_from_parent()

        if health.is_dead:
            self._destroy_enemy(enemy)

    def _col_player_enemy(self, player, enemy):
        if not player.active or not enemy.active:
            return
        if self._player and self._player.invincible:
            return
        if self._player:
            self._player.take_hit(22)
            self._update_player_hud()
        health = enemy.get_component(HealthComponent)
        if health:
            health.take_damage(60)
            if health.is_dead:
                self._destroy_enemy(enemy)
        self._screen_flash(Color(1, 0, 0, 0.38), 0.28)

    def _col_player_ebullet(self, player, ebullet):
        if not player.active or not ebullet.active:
            return
        if self._player and self._player.invincible:
            ebullet.active = False
            node = self._enodes.pop(ebullet.id, None)
            if node:
                node.remove_from_parent()
            return
        if self._player:
            self._player.take_hit(ebullet.damage)
            self._update_player_hud()
        ebullet.active = False
        node = self._enodes.pop(ebullet.id, None)
        if node:
            node.remove_from_parent()

    def _col_player_powerup(self, player, powerup):
        if not player.active or not powerup.active:
            return
        self._apply_powerup(powerup.ptype)
        tc = powerup.get_component(TransformComponent)
        if tc:
            self._pickup_label(powerup.ptype.upper() + ' UP!',
                               tc.position.x, tc.position.y)
        powerup.active = False
        node = self._enodes.pop(powerup.id, None)
        if node:
            node.remove_from_parent()

    # ── power-up application ──────────────────────────

    def _apply_powerup(self, ptype):
        p = self._player
        if not p:
            return
        if ptype == 'weapon':
            w = p.get_component(WeaponComponent)
            if w:
                w.upgrade()
        elif ptype == 'shield':
            s = p.get_component(ShieldComponent)
            if s:
                s.add_shield(55)
        elif ptype == 'health':
            h = p.get_component(HealthComponent)
            if h:
                h.heal(35)
        elif ptype == 'bomb':
            p.bombs = min(5, p.bombs + 1)
        elif ptype == 'speed':
            p.apply_speed_boost()
        self._update_player_hud()

    # ── enemy death ───────────────────────────────────

    def _destroy_enemy(self, enemy):
        if not enemy.active:
            return
        tc = enemy.get_component(TransformComponent)
        if tc:
            ex, ey = tc.position.x, tc.position.y
            big  = enemy.has_tag('boss')
            size = 85 if big else (52 if enemy.name == 'enemy_cruiser' else 36)
            exp  = make_explosion_node(size, '#ff6600')
            exp.position = (ex, ey)
            self._fx_layer.add_child(exp)

            if big:
                for _ in range(7):
                    rx = ex + random.uniform(-45, 45)
                    ry = ey + random.uniform(-45, 45)
                    xe = make_explosion_node(
                        random.randint(18, 48),
                        random.choice(['#ff6600', '#ff0000', '#ffff00']))
                    xe.position = (rx, ry)
                    self._fx_layer.add_child(xe)

            sm      = self._engine.score_manager
            earned  = sm.register_kill(enemy.score_value)
            _float_score(self._fx_layer, earned, ex, ey + 20)
            self._hud.update_score(sm.score, sm.high_score, sm.multiplier)
            self._hud.show_combo(sm.combo)

            # drop power-up
            drop_chance = (1.0 if big else
                           0.6 if enemy.name == 'enemy_cruiser' else 0.28)
            if random.random() < drop_chance:
                self._spawn_powerup(ex, ey)

            if big:
                self._boss_entity = None
                self._hud.show_boss_bar(False)

        enemy.active = False
        node = self._enodes.pop(enemy.id, None)
        if node:
            node.remove_from_parent()
        self._engine.wave_manager.enemy_destroyed()

    def _spawn_powerup(self, x, y):
        pu   = PowerUpEntity(x, y)
        node = make_powerup_node(pu.ptype)
        node.position = (x, y)
        self._gm_layer.add_child(node)
        self._enodes[pu.id] = node
        self._engine.entity_manager.add(pu)

    # ── bomb ──────────────────────────────────────────

    def _use_bomb(self):
        if not self._player or not self._player.active:
            return
        if not self._player.use_bomb():
            return
        self._hud.update_bombs(self._player.bombs)

        em = self._engine.entity_manager

        for eb in em.get_by_tag('enemy_bullet'):
            eb.active = False
            n = self._enodes.pop(eb.id, None)
            if n:
                n.remove_from_parent()

        for en in em.get_by_tag('enemy'):
            health = en.get_component(HealthComponent)
            if not health:
                continue
            if en.has_tag('boss'):
                health.take_damage(110)
                if health.is_dead:
                    self._destroy_enemy(en)
                elif self._boss_entity:
                    self._hud.update_boss_health(health.health_ratio)
            else:
                health.take_damage(9999)
                if health.is_dead:
                    self._destroy_enemy(en)

        self._screen_flash(Color(1.0, 0.85, 0.0, 0.55), 0.42)

    # ── player death ──────────────────────────────────

    def _on_player_death(self):
        self._lives -= 1
        self._hud.update_lives(self._lives)

        if self._player:
            tc = self._player.get_component(TransformComponent)
            if tc:
                exp = make_explosion_node(62, '#00aaff')
                exp.position = tc.position.to_tuple()
                self._fx_layer.add_child(exp)
            node = self._enodes.pop(self._player.id, None)
            if node:
                node.remove_from_parent()
            self._engine.entity_manager.remove(self._player)
        self._player = None

        if self._lives > 0:
            self._state         = self.ST_PAUSED
            self._respawn_timer = 2.2
            self._pending_respawn = True

            lbl = LabelNode('RESPAWNING…',
                            font=('Courier-Bold', 18),
                            color=Color(0, 0.78, 1))
            lbl.position     = (self._sw * 0.5, self._sh * 0.5)
            lbl.anchor_point = (0.5, 0.5)
            lbl.z_position   = 12
            self._ui_layer.add_child(lbl)
            lbl.run_action(Action.sequence(
                Action.wait(2.0),
                Action.remove(),
            ))
        else:
            self._game_over()

    # ── game over ─────────────────────────────────────

    def _game_over(self):
        self._state = self.ST_GAME_OVER
        self._engine.stop()
        # clean up remaining enemy nodes
        for en in self._engine.entity_manager.get_by_tag('enemy'):
            en.active = False
            n = self._enodes.pop(en.id, None)
            if n:
                n.remove_from_parent()
        self._show_game_over()

    def _show_game_over(self):
        sw, sh = self._sw, self._sh
        sm     = self._engine.score_manager

        node = Node()
        self._gameover_node = node

        dim = ShapeNode(
            ui.Path.rect(0, 0, sw, sh),
            fill_color=Color(0, 0, 0, 0.72),
            stroke_color=None)
        dim.anchor_point = (0, 0)
        node.add_child(dim)

        go = LabelNode('GAME OVER',
                       font=('Courier-Bold', 40),
                       color=Color(1, 0.05, 0.05))
        go.position     = (sw * 0.5, sh * 0.71)
        go.anchor_point = (0.5, 0.5)
        node.add_child(go)

        sc = LabelNode('SCORE:  {:,}'.format(sm.score),
                       font=('Courier-Bold', 22),
                       color=Color('white'))
        sc.position     = (sw * 0.5, sh * 0.60)
        sc.anchor_point = (0.5, 0.5)
        node.add_child(sc)

        is_new_hi = sm.score > 0 and sm.score >= sm.high_score
        hs_text   = 'NEW HIGH SCORE!' if is_new_hi else 'HIGH SCORE: {:,}'.format(sm.high_score)
        hs_color  = Color(1, 0.82, 0) if is_new_hi else Color(0.6, 0.6, 0.0)
        hs = LabelNode(hs_text,
                       font=('Courier', 18 if is_new_hi else 15),
                       color=hs_color)
        hs.position     = (sw * 0.5, sh * 0.52)
        hs.anchor_point = (0.5, 0.5)
        node.add_child(hs)

        for y_frac, text in (
            (0.44, 'WAVES:   {}'.format(sm.wave)),
            (0.38, 'KILLS:   {}'.format(sm.kills)),
        ):
            lbl = LabelNode(text, font=('Courier', 14),
                            color=Color(0.65, 0.65, 0.88))
            lbl.position     = (sw * 0.5, sh * y_frac)
            lbl.anchor_point = (0.5, 0.5)
            node.add_child(lbl)

        retry = ShapeNode(
            ui.Path.rounded_rect(-115, -29, 230, 58, 12),
            fill_color=Color(0.55, 0.0, 0.0),
            stroke_color=Color(1, 0.28, 0.0))
        retry.line_width = 2
        retry.position   = (sw * 0.5, sh * 0.26)
        retry.run_action(Action.repeat(
            Action.sequence(
                Action.scale_to(1.06, 0.6),
                Action.scale_to(0.94, 0.6),
            )
        ))
        node.add_child(retry)

        rl = LabelNode('PLAY AGAIN',
                       font=('Courier-Bold', 22),
                       color=Color('white'))
        rl.anchor_point = (0.5, 0.5)
        retry.add_child(rl)

        node.alpha = 0
        node.run_action(Action.fade_to(1, 0.5))
        self._ui_layer.add_child(node)

    # ── wave management ───────────────────────────────

    def _show_wave_banner(self, wave_num, is_boss=False):
        sw, sh = self._sw, self._sh
        text  = '⚠ BOSS INCOMING ⚠' if is_boss else 'WAVE {}'.format(wave_num)
        color = Color(1, 0.1, 0.1) if is_boss else Color(0.0, 1.0, 1.0)

        lbl = LabelNode(text, font=('Courier-Bold', 30), color=color)
        lbl.position     = (sw * 0.5, sh * 0.5)
        lbl.anchor_point = (0.5, 0.5)
        lbl.z_position   = 10
        lbl.alpha        = 0
        self._ui_layer.add_child(lbl)
        lbl.run_action(Action.sequence(
            Action.fade_to(1,   0.28),
            Action.scale_to(1.2, 0.28),
            Action.wait(1.5),
            Action.fade_to(0,   0.45),
            Action.remove(),
        ))

    def _on_wave_complete(self, wave_num):
        sm = self._engine.score_manager
        sm.next_wave()

        bonus  = wave_num * 500
        earned = sm.add_score(bonus)
        _float_score(self._fx_layer, earned,
                     self._sw * 0.5, self._sh * 0.5, '#00ff88')
        self._hud.update_score(sm.score, sm.high_score, sm.multiplier)

        sw, sh = self._sw, self._sh
        banner = LabelNode(
            'WAVE {}  CLEAR!  +{:,}'.format(wave_num, earned),
            font=('Courier-Bold', 20),
            color=Color(0.0, 1.0, 0.55))
        banner.position     = (sw * 0.5, sh * 0.56)
        banner.anchor_point = (0.5, 0.5)
        banner.z_position   = 10
        self._ui_layer.add_child(banner)
        banner.run_action(Action.sequence(
            Action.fade_to(1, 0.2),
            Action.wait(1.9),
            Action.fade_to(0, 0.45),
            Action.remove(),
        ))

        self._state    = self.ST_WAVE_TRANS
        self._wt_timer = self._wt_dur

    # ── visual helpers ────────────────────────────────

    def _hit_flash(self, enemy):
        tc = enemy.get_component(TransformComponent)
        if not tc:
            return
        flash = ShapeNode(
            ui.Path.oval(-14, -14, 28, 28),
            fill_color=Color(1, 1, 0.3, 0.72),
            stroke_color=None)
        flash.position   = tc.position.to_tuple()
        flash.z_position = 5
        self._fx_layer.add_child(flash)
        flash.run_action(Action.sequence(
            Action.scale_to(1.5, 0.08),
            Action.fade_to(0,   0.14),
            Action.remove(),
        ))

    def _screen_flash(self, color, duration):
        sw, sh = self._sw, self._sh
        f = ShapeNode(
            ui.Path.rect(0, 0, sw, sh),
            fill_color=color,
            stroke_color=None)
        f.anchor_point = (0, 0)
        f.z_position   = 6
        self.add_child(f)
        f.run_action(Action.sequence(
            Action.fade_to(0, duration),
            Action.remove(),
        ))

    def _pickup_label(self, text, x, y):
        lbl = LabelNode(text,
                        font=('Courier-Bold', 13),
                        color=Color(0.0, 1.0, 0.4))
        lbl.position   = (x, y)
        lbl.z_position = 12
        self._fx_layer.add_child(lbl)
        lbl.run_action(Action.sequence(
            Action.move_by(0, 55, 0.9),
            Action.fade_to(0, 0.38),
            Action.remove(),
        ))

    # ══════════════════════════════════════════════════
    # UPDATE LOOP
    # ══════════════════════════════════════════════════

    def update(self):
        dt = self.dt
        self._stars.update(dt)

        if self._state == self.ST_PLAYING:
            self._update_playing(dt)
        elif self._state == self.ST_WAVE_TRANS:
            self._update_wave_trans(dt)
        elif self._state == self.ST_PAUSED:
            self._update_paused(dt)

    def _update_playing(self, dt):
        # auto-fire
        if self._player and self._player.active:
            w = self._player.get_component(WeaponComponent)
            if w:
                w.fire()

        self._engine.update(dt)
        self._sync_nodes()
        self._cull_offscreen()
        self._refresh_hud()

    def _update_wave_trans(self, dt):
        self._wt_timer -= dt
        if self._wt_timer <= 0:
            next_w  = self._engine.wave_manager.wave_number + 1
            is_boss = (next_w % 5 == 0)
            self._state = self.ST_PLAYING
            self._engine.wave_manager.start_wave(next_w)
            self._show_wave_banner(next_w, is_boss)
            self._hud.update_wave(next_w, is_boss)

    def _update_paused(self, dt):
        if self._pending_respawn:
            self._respawn_timer -= dt
            if self._respawn_timer <= 0:
                self._pending_respawn = False
                self._state = self.ST_PLAYING
                self._create_player()

    # ── node sync ─────────────────────────────────────

    def _sync_nodes(self):
        """Move every scene node to its entity's current position."""
        em = self._engine.entity_manager
        for eid, node in list(self._enodes.items()):
            entity = em.entities.get(eid)
            if entity is None or not entity.active:
                node.remove_from_parent()
                del self._enodes[eid]
                continue
            tc = entity.get_component(TransformComponent)
            if not tc:
                continue
            node.position = tc.position.to_tuple()

            if entity.has_tag('player'):
                # shield visibility
                sc = entity.get_component(ShieldComponent)
                sn = node.child_named('shield')
                if sc and sn:
                    sn.alpha = 0.82 if sc.active else 0
                # invincibility flicker
                if entity.invincible:
                    node.alpha = 0.5 + 0.5 * abs(
                        math.sin(entity.invincible_timer * 18))
                else:
                    node.alpha = 1.0

            if entity.has_tag('boss'):
                inner = node.child_named('inner_core')
                if inner:
                    s = 0.78 + 0.44 * abs(
                        math.sin(entity._phase_t * 3.2))
                    inner.x_scale = s
                    inner.y_scale = s

    # ── off-screen culling ────────────────────────────

    def _cull_offscreen(self):
        sw, sh = self._sw, self._sh
        margin = 120
        em     = self._engine.entity_manager

        for entity in list(em.entities.values()):
            if not entity.active:
                continue

            if entity.has_tag('player'):
                # clamp player inside screen
                tc = entity.get_component(TransformComponent)
                if tc:
                    tc.position.x = max(28, min(sw - 28, tc.position.x))
                    tc.position.y = max(28, min(sh - 58, tc.position.y))
                continue

            tc = entity.get_component(TransformComponent)
            if not tc:
                continue
            x, y = tc.position.x, tc.position.y
            if x < -margin or x > sw + margin or \
               y < -margin or y > sh + margin:
                if entity.has_tag('enemy') and not entity.has_tag('boss'):
                    self._engine.wave_manager.enemy_destroyed()
                entity.active = False
                n = self._enodes.pop(entity.id, None)
                if n:
                    n.remove_from_parent()
                em.remove(entity)

    # ── HUD refresh ───────────────────────────────────

    def _refresh_hud(self):
        sm = self._engine.score_manager
        self._hud.update_score(sm.score, sm.high_score, sm.multiplier)
        if self._player and self._player.active:
            hc = self._player.get_component(HealthComponent)
            sc = self._player.get_component(ShieldComponent)
            self._hud.update_health(
                hc.health_ratio if hc else 0,
                sc.shield_ratio if sc else 0)
            self._hud.update_bombs(self._player.bombs)

    def _update_player_hud(self):
        if self._player and self._player.active:
            hc = self._player.get_component(HealthComponent)
            sc = self._player.get_component(ShieldComponent)
            self._hud.update_health(
                hc.health_ratio if hc else 0,
                sc.shield_ratio if sc else 0)

    # ══════════════════════════════════════════════════
    # TOUCH INPUT
    # ══════════════════════════════════════════════════

    def touch_began(self, touch):
        x, _ = touch.location

        if self._state in (self.ST_MENU, self.ST_GAME_OVER):
            self._start_game()
            return

        if self._state != self.ST_PLAYING:
            return

        if x < self._sw * 0.6:
            if self._move_touch is None:
                self._move_touch = touch
                self._move_player(touch.location)
        else:
            if self._bomb_touch is None:
                self._bomb_touch = touch
                self._use_bomb()

    def touch_moved(self, touch):
        if self._state != self.ST_PLAYING:
            return
        if touch is self._move_touch:
            self._move_player(touch.location)

    def touch_ended(self, touch):
        if touch is self._move_touch:
            self._move_touch = None
        elif touch is self._bomb_touch:
            self._bomb_touch = None

    def _move_player(self, loc):
        x, y = loc
        if self._player and self._player.active:
            self._player.set_target(x, y)


# ─────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    run(GameScene(), PORTRAIT, show_fps=True)
