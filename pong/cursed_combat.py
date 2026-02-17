"""
cursed_combat.py -- Sword-fighting combat system for Cursed Mode.

Features:
- Dual combat modes: Force (default) and Saber, toggled with one button
- Ball grab: catch a slow ball, carry it, then launch it at insane speed
- Paddle grab: grab the enemy paddle and throw it across the board
- Directional sword (saber mode): controlled by movement keys, swings where you point
- Sword has physics mass — fast swings deal damage and deflect the ball
- 3-hit health system with visual damage states
- Permanent death (paddle stays dead until game restart)
- Rayman-style cartoon hands with 3 states (Force/Igniting/Saber)
- Lightning bolt kill move (hold push+pull for 2s)
- Blood particle system with dripping, splattering, pooling
- Paddle-to-paddle collision (ramming)
"""

import math
import random
import time
import pygame
import numpy as np
from pong.constants import *
from pong import audio


# ---- Blood colors ----
BLOOD_RED = (180, 0, 0)
BLOOD_DARK = (100, 0, 0)
BLOOD_BRIGHT = (220, 20, 20)
BLOOD_DRIP = (140, 0, 0)

# ---- Skin color for hands ----
SKIN_COLOR = (255, 220, 185)
SKIN_SHADOW = (220, 185, 150)
SKIN_HIGHLIGHT = (255, 240, 220)

# ---- Sword constants ----
SWORD_LENGTH = 100  # longer reach for combat
SWORD_WIDTH = 4
SWORD_MASS = 3.0  # mass for momentum calculation
MIN_DAMAGE_ANGULAR_VEL = 3.0  # radians/sec minimum to deal damage
SWORD_LERP_SPEED = 0.25  # how fast sword tracks input direction
BALL_SWORD_IMPULSE = 12.0  # impulse applied to ball on sword hit
MAX_HEALTH = 3

# ---- Combat mode constants ----
MODE_FORCE = 'force'
MODE_SABER = 'saber'
IGNITE_ANIMATION_DURATION = 0.55
SABER_SWING_IMPULSE = 12.0
SABER_BLOCK_ANGLE = math.pi / 2
LIGHTNING_CHARGE_TIME = 2.0
LIGHTNING_KILL_DIST = 130
CHARGE_FORCE_TIME = 1.5


# -----------------------------------------------------------------------
# Module-level helpers
# -----------------------------------------------------------------------

def _draw_cartoon_hand(surface, x, y, facing_right, size=10):
    """Draw a Rayman-style cartoon hand: big round palm with shadow + highlight, 3 stubby fingers."""
    ix, iy = int(x), int(y)
    s = size

    # Drop shadow
    pygame.draw.circle(surface, SKIN_SHADOW, (ix + 1, iy + 2), s)

    # Main palm
    pygame.draw.circle(surface, SKIN_COLOR, (ix, iy), s)

    # Specular highlight (top-left quarter)
    hl_x = ix - s // 3
    hl_y = iy - s // 3
    pygame.draw.circle(surface, SKIN_HIGHLIGHT, (hl_x, hl_y), max(s // 3, 2))

    # 3 stubby fingers
    finger_dir = 1 if facing_right else -1
    finger_angles = [-0.5, 0.0, 0.5]  # spread in radians
    finger_len = s * 0.7
    for fa in finger_angles:
        fx = ix + math.cos(fa) * (s + finger_len) * finger_dir
        fy = iy + math.sin(fa) * (s + finger_len * 0.5)
        # Knuckle arc
        mid_fx = ix + math.cos(fa) * s * finger_dir
        mid_fy = iy + math.sin(fa) * s * 0.5
        pygame.draw.circle(surface, SKIN_COLOR, (int(mid_fx), int(mid_fy)), max(s // 3, 2))
        pygame.draw.circle(surface, SKIN_COLOR, (int(fx), int(fy)), max(s // 4, 2))


def _generate_lightning_path(x1, y1, x2, y2, jitter=30, segments=8):
    """Generate a jagged lightning bolt path between two points."""
    points = [(x1, y1)]
    for i in range(1, segments):
        t = i / segments
        mx = x1 + (x2 - x1) * t + random.uniform(-jitter, jitter)
        my = y1 + (y2 - y1) * t + random.uniform(-jitter, jitter)
        points.append((mx, my))
    points.append((x2, y2))
    return points


def _point_near_path(px, py, path, threshold=15):
    """Check if a point is near any segment of a path."""
    for i in range(len(path) - 1):
        ax, ay = path[i]
        bx, by = path[i + 1]
        # Point-to-segment distance
        dx, dy = bx - ax, by - ay
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq < 1:
            continue
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
        closest_x = ax + t * dx
        closest_y = ay + t * dy
        dist = math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)
        if dist < threshold:
            return True
    return False


# -----------------------------------------------------------------------
# Blood Particle System
# -----------------------------------------------------------------------

class BloodParticle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life',
                 'size', 'splat', 'splat_size')

    def __init__(self, x, y, vx, vy, color, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.splat = False
        self.splat_size = 0


class BloodSystem:
    """Gore particle system. Blood droplets fly, drip, and splat on surfaces."""

    MAX_PARTICLES = 500
    GRAVITY = 200  # heavier than normal particles

    def __init__(self, screen_h=None):
        self._particles = []
        self._splats = []  # permanent blood pools on surfaces
        self._last_time = time.monotonic()
        self._screen_h = screen_h or HEIGHT

    def emit_slash(self, x, y, direction_x, count=40):
        """Emit blood from a sword slash. direction_x: 1 or -1."""
        colors = [BLOOD_RED, BLOOD_DARK, BLOOD_BRIGHT, BLOOD_DRIP,
                  (200, 0, 0), (160, 10, 10)]
        for _ in range(count):
            angle = random.uniform(-1.2, 1.2)
            spd = random.uniform(80, 350)
            vx = math.cos(angle) * spd * direction_x
            vy = math.sin(angle) * spd - random.uniform(50, 200)
            color = random.choice(colors)
            life = random.uniform(0.8, 2.5)
            size = random.randint(2, 6)
            self._particles.append(
                BloodParticle(x, y, vx, vy, color, life, size))

    def emit_drip(self, x, y, count=5):
        """Continuous drip from a bleeding paddle."""
        for _ in range(count):
            vx = random.uniform(-15, 15)
            vy = random.uniform(20, 80)
            color = random.choice([BLOOD_RED, BLOOD_DARK, BLOOD_DRIP])
            life = random.uniform(1.0, 3.0)
            size = random.randint(1, 3)
            self._particles.append(
                BloodParticle(x + random.uniform(-5, 5), y, vx, vy,
                              color, life, size))

    def emit_impact(self, x, y, count=20):
        """Blood burst from a high-speed paddle ram."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(40, 200)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice([BLOOD_RED, BLOOD_BRIGHT, (200, 30, 30)])
            life = random.uniform(0.5, 1.5)
            size = random.randint(2, 5)
            self._particles.append(
                BloodParticle(x, y, vx, vy, color, life, size))

    def emit_hit(self, x, y, count=15):
        """Medium blood burst for a sword hit (not kill)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(30, 150)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - random.uniform(20, 80)
            color = random.choice([BLOOD_RED, BLOOD_DARK, BLOOD_BRIGHT])
            life = random.uniform(0.5, 1.8)
            size = random.randint(1, 4)
            self._particles.append(
                BloodParticle(x, y, vx, vy, color, life, size))

    def update(self):
        now = time.monotonic()
        dt = now - self._last_time
        self._last_time = now
        if dt <= 0:
            return

        H = self._screen_h
        grav = self.GRAVITY * dt
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                # Convert to permanent splat
                if p.y >= H - 20 and not p.splat:
                    self._splats.append(
                        (int(p.x), int(p.y), p.color, random.randint(2, 5)))
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += grav

            # Floor collision — splat and slow
            if p.y >= H - 5:
                p.y = H - 5
                p.vy = -abs(p.vy) * 0.2
                p.vx *= 0.5
                if not p.splat:
                    p.splat = True
                    p.splat_size = random.randint(3, 7)
                    self._splats.append(
                        (int(p.x), int(p.y), p.color, p.splat_size))

            alive.append(p)

        # Budget
        overflow = len(alive) - self.MAX_PARTICLES
        if overflow > 0:
            del alive[:overflow]
        self._particles = alive

        # Limit permanent splats
        if len(self._splats) > 300:
            self._splats = self._splats[-200:]

    def draw(self, surface):
        # Draw permanent blood pools first (underneath)
        for sx, sy, color, size in self._splats:
            pygame.draw.circle(surface, color, (sx, sy), size)

        # Draw active blood particles
        for p in self._particles:
            ratio = max(p.life / p.max_life, 0.0)
            cur_size = max(int(p.size * ratio), 1)
            # Elongate fast-moving particles (blood streaks)
            speed = math.sqrt(p.vx * p.vx + p.vy * p.vy)
            if speed > 100 and cur_size >= 2:
                dx = p.vx / speed * cur_size * 2
                dy = p.vy / speed * cur_size * 2
                pygame.draw.line(surface, p.color,
                                 (int(p.x - dx), int(p.y - dy)),
                                 (int(p.x + dx), int(p.y + dy)),
                                 max(cur_size - 1, 1))
            else:
                pygame.draw.circle(surface, p.color,
                                   (int(p.x), int(p.y)), cur_size)

    def reset(self):
        self._particles.clear()
        self._splats.clear()


# -----------------------------------------------------------------------
# Sword (directional, physics-based) with ignition + blocking
# -----------------------------------------------------------------------

class Sword:
    """A sword attached to a paddle. Controlled by movement keys direction."""

    def __init__(self, is_left, paddle_color=None):
        self.is_left = is_left
        self.angle = 0.0  # current sword angle in radians relative to base
        self.prev_angle = 0.0  # previous frame angle for angular velocity
        self.angular_velocity = 0.0  # rad/s for damage calculation
        self.visible = False  # only visible when player presses movement keys
        self._target_angle = 0.0
        self._hit_cooldown = 0.0  # brief per-hit cooldown to avoid double hits
        self.paddle_color = paddle_color or LIGHT_PURPLE

        # Ignition state
        self.ignited = False
        self.ignite_progress = 0.0  # 0..1 animation progress
        self._ignite_dir = 1  # 1=igniting, -1=sheathing

        # Blocking state
        self.blocking = False
        self._swing_kicked = False

        # Pre-allocate glow surface to avoid per-frame allocation
        glow_size = int(SWORD_LENGTH * 2 + 60)
        self._glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

    def _base_angle(self):
        """Left paddle sword points RIGHT (0), right paddle points LEFT (pi)."""
        return 0.0 if self.is_left else math.pi

    def ignite(self):
        """Start ignition animation."""
        self._ignite_dir = 1
        if not self.ignited:
            self.ignite_progress = 0.0
        self.ignited = True

    def sheathe(self):
        """Start sheathing animation."""
        self._ignite_dir = -1

    def set_direction(self, dx, dy):
        """Set sword direction from input vector. (0,0) = neutral."""
        if abs(dx) < 0.01 and abs(dy) < 0.01:
            self.visible = False
            return
        self.visible = True
        # Target angle relative to base
        input_angle = math.atan2(dy, dx)
        # For right paddle, mirror the input
        if not self.is_left:
            input_angle = math.pi - input_angle
        self._target_angle = input_angle

    def set_blocking(self, is_blocking):
        """Enter or exit block stance."""
        self.blocking = is_blocking

    def apply_swing_impulse(self, dx, dy):
        """Kick the sword in aimed direction for a saber swing."""
        if abs(dx) < 0.01 and abs(dy) < 0.01:
            # Default forward swing
            dx = 1.0 if self.is_left else -1.0
        input_angle = math.atan2(dy, dx)
        if not self.is_left:
            input_angle = math.pi - input_angle
        self._target_angle = input_angle
        self.visible = True
        self._swing_kicked = True
        # Boost angular velocity for hit detection
        self.angular_velocity = SABER_SWING_IMPULSE * (1 if random.random() > 0.5 else -1)

    def update(self, dt=1/60):
        """Update sword angle with smooth lerp toward target."""
        self._hit_cooldown = max(0, self._hit_cooldown - dt)

        # Ignition animation
        if self._ignite_dir > 0 and self.ignite_progress < 1.0:
            self.ignite_progress = min(1.0, self.ignite_progress + dt / IGNITE_ANIMATION_DURATION)
        elif self._ignite_dir < 0:
            self.ignite_progress = max(0.0, self.ignite_progress - dt / (IGNITE_ANIMATION_DURATION * 0.7))
            if self.ignite_progress <= 0:
                self.ignited = False
                self._ignite_dir = 1

        self.prev_angle = self.angle

        # Blocking: snap to perpendicular
        if self.blocking and self.ignited:
            block_target = SABER_BLOCK_ANGLE if self.is_left else -SABER_BLOCK_ANGLE
            self.angle += (block_target - self.angle) * 0.4
            self.angular_velocity = 0
            self.visible = True
            return

        if not self.visible:
            # Lerp back to neutral when hidden
            self.angle += (0 - self.angle) * 0.2
            self.angular_velocity = 0
            return

        # Smooth rotation toward target
        diff = self._target_angle - self.angle
        # Normalize angle difference to [-pi, pi]
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi

        self.angle += diff * SWORD_LERP_SPEED
        self.angular_velocity = (self.angle - self.prev_angle) / dt

        # Decay swing kick
        if self._swing_kicked:
            self._swing_kicked = False

    def get_tip_pos(self, paddle):
        """Get sword tip world position."""
        cx = paddle.pos[0] + paddle.width / 2
        cy = paddle.pos[1] + paddle.height / 2
        final_angle = self._base_angle() + self.angle
        blade_len = SWORD_LENGTH * self.ignite_progress
        tip_x = cx + math.cos(final_angle) * blade_len
        tip_y = cy + math.sin(final_angle) * blade_len
        return tip_x, tip_y

    def get_hitbox(self, paddle):
        """Get sword line segment for collision detection."""
        cx = paddle.pos[0] + paddle.width / 2
        cy = paddle.pos[1] + paddle.height / 2
        final_angle = self._base_angle() + self.angle
        blade_len = SWORD_LENGTH * self.ignite_progress
        tip_x = cx + math.cos(final_angle) * blade_len
        tip_y = cy + math.sin(final_angle) * blade_len
        return (cx, cy), (tip_x, tip_y)

    def can_hit(self):
        """Whether this sword can deal damage right now."""
        return (self.ignited and self.ignite_progress > 0.5 and
                (abs(self.angular_velocity) > MIN_DAMAGE_ANGULAR_VEL or self._swing_kicked) and
                self._hit_cooldown <= 0)

    def register_hit(self):
        """Mark that a hit just happened (brief cooldown)."""
        self._hit_cooldown = 0.25  # 250ms between hits
        self._swing_kicked = False

    def draw(self, surface, paddle):
        if not self.ignited or self.ignite_progress < 0.01:
            return

        cx = int(paddle.pos[0] + paddle.width / 2)
        cy = int(paddle.pos[1] + paddle.height / 2)
        final_angle = self._base_angle() + self.angle

        blade_len = SWORD_LENGTH * self.ignite_progress
        tip_x = cx + math.cos(final_angle) * blade_len
        tip_y = cy + math.sin(final_angle) * blade_len

        # Swing speed intensifies glow
        speed_ratio = min(abs(self.angular_velocity) / 10.0, 1.0)
        base_alpha_mult = 0.7 + 0.3 * speed_ratio

        pr, pg, pb = self.paddle_color[:3]

        # Draw lightsaber glow layers on pre-allocated SRCALPHA surface
        gs = self._glow_surf
        gs.fill((0, 0, 0, 0))
        gw, gh = gs.get_size()
        gcx, gcy = gw // 2, gh // 2
        local_tip_x = gcx + math.cos(final_angle) * blade_len
        local_tip_y = gcy + math.sin(final_angle) * blade_len

        # Layer 1: Outer glow — thick, low alpha
        outer_alpha = int(30 * base_alpha_mult)
        pygame.draw.line(gs, (pr, pg, pb, outer_alpha),
                         (gcx, gcy), (int(local_tip_x), int(local_tip_y)), 20)

        # Layer 2: Mid glow — medium
        mid_alpha = int(80 * base_alpha_mult)
        pygame.draw.line(gs, (pr, pg, pb, mid_alpha),
                         (gcx, gcy), (int(local_tip_x), int(local_tip_y)), 10)

        # Layer 3: Core blade — white tinted with paddle color
        core_r = min(255, pr // 2 + 128)
        core_g = min(255, pg // 2 + 128)
        core_b = min(255, pb // 2 + 128)
        core_alpha = int(240 * base_alpha_mult)
        pygame.draw.line(gs, (core_r, core_g, core_b, core_alpha),
                         (gcx, gcy), (int(local_tip_x), int(local_tip_y)), 4)

        # Layer 4: Tip hotspot — small bright circle
        tip_color = (min(255, pr + 100), min(255, pg + 100), min(255, pb + 100), int(200 * base_alpha_mult))
        pygame.draw.circle(gs, tip_color, (int(local_tip_x), int(local_tip_y)), 5)

        surface.blit(gs, (cx - gcx, cy - gcy))

        # Ignition sparks during animation
        if self.ignite_progress < 1.0 and self._ignite_dir > 0:
            for _ in range(3):
                spark_t = random.uniform(0.3, self.ignite_progress)
                sx = cx + math.cos(final_angle) * SWORD_LENGTH * spark_t + random.uniform(-5, 5)
                sy = cy + math.sin(final_angle) * SWORD_LENGTH * spark_t + random.uniform(-5, 5)
                pygame.draw.circle(surface, (255, 255, 200), (int(sx), int(sy)), random.randint(1, 3))

        # Hilt — dark metallic rectangle at base
        perp_angle = final_angle + math.pi / 2
        hilt_len = 8
        h1x = cx + math.cos(perp_angle) * hilt_len
        h1y = cy + math.sin(perp_angle) * hilt_len
        h2x = cx - math.cos(perp_angle) * hilt_len
        h2y = cy - math.sin(perp_angle) * hilt_len
        pygame.draw.line(surface, (60, 60, 70), (int(h1x), int(h1y)),
                         (int(h2x), int(h2y)), 4)
        # Small pommel
        back_x = cx - math.cos(final_angle) * 6
        back_y = cy - math.sin(final_angle) * 6
        pygame.draw.circle(surface, (50, 50, 60), (int(back_x), int(back_y)), 3)

    def draw_hands(self, surface, paddle, combat_mode=MODE_FORCE):
        """Draw Rayman-style cartoon hands. 3 states: Force, Igniting, Saber."""
        cx = paddle.pos[0] + paddle.width / 2
        cy = paddle.pos[1] + paddle.height / 2
        facing_right = self.is_left
        t = time.monotonic()

        if combat_mode == MODE_SABER and self.ignited and self.ignite_progress > 0.5:
            # SABER STATE: both hands grip the hilt
            final_angle = self._base_angle() + self.angle
            perp = final_angle + math.pi / 2
            hand_dist = 5
            hand_spread = 6
            for sign in (-1, 1):
                hx = cx + math.cos(final_angle) * hand_dist + math.cos(perp) * hand_spread * sign
                hy = cy + math.sin(final_angle) * hand_dist + math.sin(perp) * hand_spread * sign
                _draw_cartoon_hand(surface, hx, hy, facing_right, size=6)

        elif combat_mode == MODE_SABER and self.ignited and self.ignite_progress <= 0.5:
            # IGNITING STATE: hand swoops from behind
            prog = self.ignite_progress / 0.5  # 0..1 during first half
            behind_x = cx + (-15 if facing_right else 15)
            target_x = cx + (8 if facing_right else -8)
            hx = behind_x + (target_x - behind_x) * prog
            hy = cy - 5 * math.sin(prog * math.pi)  # arc motion
            _draw_cartoon_hand(surface, hx, hy, facing_right, size=7)
            # Second hand stays at side
            side_x = paddle.pos[0] + (paddle.width + 5 if self.is_left else -5)
            _draw_cartoon_hand(surface, side_x, cy + 8, facing_right, size=6)

        else:
            # FORCE STATE: floating, bobbing Rayman hands
            bob = math.sin(t * 3) * 4
            hand_offset_x = 12 if facing_right else -12
            # Top hand
            _draw_cartoon_hand(surface, cx + hand_offset_x, cy - 15 + bob,
                               facing_right, size=7)
            # Bottom hand
            _draw_cartoon_hand(surface, cx + hand_offset_x, cy + 15 - bob,
                               facing_right, size=7)


# -----------------------------------------------------------------------
# Lightning bolt data
# -----------------------------------------------------------------------

class _LightningBolt:
    """Active lightning bolt visual."""
    __slots__ = ('path', 'life', 'max_life', 'color', 'width')

    def __init__(self, path, life, color, width=3):
        self.path = path
        self.life = life
        self.max_life = life
        self.color = color
        self.width = width


# -----------------------------------------------------------------------
# CursedCombatManager
# -----------------------------------------------------------------------

class CursedCombatManager:
    """
    Manages all insane cursed mode combat mechanics:
    - Dual combat modes (Force / Saber)
    - Ball grab & launch
    - Paddle grab & throw
    - Directional sword combat with momentum-based damage
    - 3-hit health system with visual damage
    - Permanent paddle death
    - Sword-ball interaction
    - Paddle ramming
    - Lightning bolt kill move
    - Rayman hands
    """

    GRAB_SPEED_THRESHOLD = 12.0  # Ball must be slower than this to grab
    GRAB_RANGE = 50.0
    LAUNCH_SPEED_MULT = 2.5  # Launch speed = paddle speed * this
    PADDLE_GRAB_RANGE = 50.0
    THROW_SPEED = 15.0
    RAM_DAMAGE_THRESHOLD = 4.0  # Min paddle speed for ram damage

    def __init__(self, left_color=None, right_color=None, screen_w=None, screen_h=None):
        self._screen_w = screen_w or WIDTH
        self._screen_h = screen_h or HEIGHT
        self.blood = BloodSystem(screen_h=self._screen_h)
        self._left_color = left_color
        self._right_color = right_color
        self.left_sword = Sword(is_left=True, paddle_color=left_color)
        self.right_sword = Sword(is_left=False, paddle_color=right_color)

        # Combat mode per side
        self.mode_left = MODE_FORCE
        self.mode_right = MODE_FORCE

        # Grab state
        self.ball_grabbed_by = None  # 'left' or 'right' or None
        self.paddle_grabbed = None  # 'left_grabs_right', 'right_grabs_left', None
        self._grab_offset = np.zeros(2)

        # Health system: 3 hits to kill
        self.health = {'left': MAX_HEALTH, 'right': MAX_HEALTH}

        # Cut state: paddle halves (when health reaches 0)
        self.left_cut = False
        self.right_cut = False
        self.left_cut_halves = None
        self.right_cut_halves = None
        self._left_bleed_timer = 0
        self._right_bleed_timer = 0

        # Damage flash timers
        self._damage_flash = {'left': 0, 'right': 0}

        # Lightning system
        self._lightning_charge = {'left': 0.0, 'right': 0.0}
        self._lightning_frozen = {'left': False, 'right': False}
        self._lightning_active = []  # list of _LightningBolt

    def get_mode(self, side):
        return self.mode_left if side == 'left' else self.mode_right

    def set_mode(self, side, mode):
        if side == 'left':
            self.mode_left = mode
        else:
            self.mode_right = mode

    def toggle_mode(self, side):
        """Toggle between Force and Saber mode for a side."""
        current = self.get_mode(side)
        sword = self.left_sword if side == 'left' else self.right_sword
        if current == MODE_FORCE:
            self.set_mode(side, MODE_SABER)
            sword.ignite()
            audio.play('lightsaber_ignite')
        else:
            self.set_mode(side, MODE_FORCE)
            sword.sheathe()
            audio.play('lightsaber_sheathe')

    # ---- Lightning system ----

    def is_lightning_frozen(self, side):
        return self._lightning_frozen[side]

    def update_lightning_charge(self, side, both_held, dt, paddles):
        """Update lightning charge. Call each frame when both push+pull are held."""
        if both_held and self.get_mode(side) == MODE_FORCE:
            self._lightning_charge[side] += dt
            self._lightning_frozen[side] = True  # can't move while charging
            if self._lightning_charge[side] >= LIGHTNING_CHARGE_TIME:
                # FIRE!
                attacker = paddles[0] if side == 'left' else paddles[1]
                target = paddles[1] if side == 'left' else paddles[0]
                self._fire_lightning(side, attacker, target)
                self._lightning_charge[side] = 0.0
                self._lightning_frozen[side] = False
        else:
            self._lightning_charge[side] = 0.0
            self._lightning_frozen[side] = False

    def _fire_lightning(self, side, attacker, target):
        """Fire a lightning bolt at the enemy paddle."""
        ax = attacker.pos[0] + attacker.width / 2
        ay = attacker.pos[1] + attacker.height / 2
        tx = target.pos[0] + target.width / 2
        ty = target.pos[1] + target.height / 2
        dist = math.sqrt((tx - ax) ** 2 + (ty - ay) ** 2)

        audio.play('lightning_strike')

        # Create bolt visual
        color = self._left_color if side == 'left' else self._right_color
        bright = (min(255, color[0] + 150), min(255, color[1] + 150), min(255, color[2] + 150))
        path = _generate_lightning_path(ax, ay, tx, ty, jitter=40, segments=10)
        self._lightning_active.append(_LightningBolt(path, 0.5, bright, width=4))
        # Secondary thinner bolt
        path2 = _generate_lightning_path(ax, ay, tx, ty, jitter=25, segments=7)
        self._lightning_active.append(_LightningBolt(path2, 0.35, color, width=2))

        # Damage if close enough
        if dist < LIGHTNING_KILL_DIST * 3:
            target_side = 'right' if side == 'left' else 'left'
            if not self.is_cut(target_side):
                # Lightning does 2 damage!
                damage = min(2, self.health[target_side])
                for _ in range(damage):
                    self._apply_damage(target, target_side, attacker)

    def get_lightning_charge_frac(self, side):
        return min(1.0, self._lightning_charge[side] / LIGHTNING_CHARGE_TIME)

    def set_sword_direction(self, side, dx, dy):
        """Set sword direction from input keys. Called each frame."""
        sword = self.left_sword if side == 'left' else self.right_sword
        sword.set_direction(dx, dy)

    def try_grab_ball(self, side, paddle, ball):
        """Try to grab the ball. Returns True if grabbed."""
        if self.ball_grabbed_by is not None:
            return False
        if self.paddle_grabbed is not None:
            return False

        dist = np.linalg.norm(ball.pos - paddle.pos -
                              np.array([paddle.width / 2, paddle.height / 2]))
        ball_speed = np.linalg.norm(ball.vel)

        if dist < self.GRAB_RANGE and ball_speed < self.GRAB_SPEED_THRESHOLD:
            self.ball_grabbed_by = side
            self._grab_offset = ball.pos.copy() - paddle.pos.copy()
            ball.vel[:] = 0
            ball.spin = 0
            return True
        return False

    def release_ball(self, paddle, ball):
        """Release a grabbed ball, launching it with the paddle's velocity."""
        if self.ball_grabbed_by is None:
            return
        paddle_speed = np.linalg.norm(paddle.vel)
        if paddle_speed > 0.5:
            direction = paddle.vel / paddle_speed
            launch_speed = max(8.0, paddle_speed * self.LAUNCH_SPEED_MULT)
            ball.vel[:] = direction * launch_speed
        else:
            # Default launch forward
            is_left = self.ball_grabbed_by == 'left'
            ball.vel[:] = [8.0 if is_left else -8.0, 0]
        ball.spin = paddle.vel[1] * 0.3
        self.ball_grabbed_by = None

    def update_grabbed_ball(self, paddle, ball):
        """Keep grabbed ball attached to paddle."""
        if self.ball_grabbed_by is None:
            return
        ball.pos[:] = paddle.pos + self._grab_offset
        ball.vel[:] = 0

    def try_grab_paddle(self, grabber_side, grabber, target):
        """Try to grab the enemy paddle."""
        if self.paddle_grabbed is not None:
            return False
        if self.ball_grabbed_by is not None:
            return False

        gc = grabber.pos + np.array([grabber.width / 2, grabber.height / 2])
        tc = target.pos + np.array([target.width / 2, target.height / 2])
        dist = np.linalg.norm(gc - tc)

        if dist < self.PADDLE_GRAB_RANGE:
            self.paddle_grabbed = f'{grabber_side}_grabs_{"right" if grabber_side == "left" else "left"}'
            self._grab_offset = target.pos.copy() - grabber.pos.copy()
            target.vel[:] = 0
            return True
        return False

    def throw_paddle(self, grabber, target):
        """Throw the grabbed paddle."""
        if self.paddle_grabbed is None:
            return
        grabber_speed = np.linalg.norm(grabber.vel)
        if grabber_speed > 0.5:
            direction = grabber.vel / grabber_speed
            target.vel[:] = direction * max(self.THROW_SPEED, grabber_speed * 2)
        else:
            is_left = 'left_grabs' in self.paddle_grabbed
            target.vel[:] = [self.THROW_SPEED if is_left else -self.THROW_SPEED, 0]
        self.paddle_grabbed = None

    def update_grabbed_paddle(self, grabber, target):
        """Keep grabbed paddle attached to grabber."""
        if self.paddle_grabbed is None:
            return
        target.pos[:] = grabber.pos + self._grab_offset
        target.vel[:] = 0

    def check_sword_hit(self, left_paddle, right_paddle):
        """Check if a sword hits the enemy paddle. Apply damage if so."""
        for sword, attacker, target, target_side, attacker_side in [
            (self.left_sword, left_paddle, right_paddle, 'right', 'left'),
            (self.right_sword, right_paddle, left_paddle, 'left', 'right'),
        ]:
            if not sword.can_hit():
                continue
            if self.is_cut(target_side):
                continue
            # Check if target is blocking
            target_sword = self.right_sword if target_side == 'right' else self.left_sword
            if target_sword.blocking and target_sword.ignited:
                # Block! Clash sound, no damage
                audio.play('lightsaber_clash')
                sword.register_hit()
                continue
            # Get sword line
            (sx, sy), (tx, ty) = sword.get_hitbox(attacker)
            # Check intersection with target paddle rect
            pr = pygame.Rect(int(target.pos[0]), int(target.pos[1]),
                             int(target.width), int(target.height))
            if pr.clipline(sx, sy, tx, ty):
                sword.register_hit()
                self._apply_damage(target, target_side, attacker)

    def check_sword_ball_hit(self, ball):
        """Check if a sword blade intersects the ball. Apply impulse if so."""
        pass  # Handled via _check_sword_ball in update()

    def _check_sword_ball(self, sword, paddle, ball):
        """Check if sword blade hits ball and deflect it."""
        if not sword.ignited or sword.ignite_progress < 0.3:
            return False
        if sword._hit_cooldown > 0:
            return False

        (sx, sy), (tx, ty) = sword.get_hitbox(paddle)

        # Point-to-line-segment distance for ball center
        bx, by = ball.pos[0], ball.pos[1]
        dx, dy = tx - sx, ty - sy
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq < 1:
            return False

        t = max(0, min(1, ((bx - sx) * dx + (by - sy) * dy) / seg_len_sq))
        closest_x = sx + t * dx
        closest_y = sy + t * dy
        dist = math.sqrt((bx - closest_x) ** 2 + (by - closest_y) ** 2)

        if dist < ball.radius + SWORD_WIDTH:
            # Deflect ball in sword direction with impulse
            final_angle = sword._base_angle() + sword.angle
            impulse_strength = min(BALL_SWORD_IMPULSE,
                                   abs(sword.angular_velocity) * SWORD_MASS * 0.5 + 4)
            ball.vel[0] = math.cos(final_angle) * impulse_strength
            ball.vel[1] = math.sin(final_angle) * impulse_strength
            sword.register_hit()
            return True
        return False

    def _apply_damage(self, target, target_side, attacker):
        """Deal 1 damage to a paddle. Cut in half at 0 HP."""
        audio.play('lightsaber_clash')
        self.health[target_side] -= 1
        hp = self.health[target_side]
        self._damage_flash[target_side] = 15  # flash frames

        cx = target.pos[0] + target.width / 2
        mid_y = target.pos[1] + target.height / 2
        direction = 1.0 if attacker.pos[0] < target.pos[0] else -1.0

        if hp <= 0:
            # Kill — cut in half!
            self._apply_cut(target, target_side, attacker)
        else:
            # Damage hit — blood splash scaled by remaining HP
            blood_count = 10 + (MAX_HEALTH - hp) * 10
            self.blood.emit_hit(cx, mid_y, count=blood_count)

    def _apply_cut(self, target, target_side, attacker):
        """Cut a paddle in half! Gore time."""
        mid_y = target.pos[1] + target.height / 2

        if target_side == 'left':
            self.left_cut = True
            self.left_cut_halves = (target.pos[1], mid_y + 8,
                                    target.height)
        else:
            self.right_cut = True
            self.right_cut_halves = (target.pos[1], mid_y + 8,
                                     target.height)

        # Blood explosion at cut point
        cx = target.pos[0] + target.width / 2
        direction = 1.0 if attacker.pos[0] < target.pos[0] else -1.0
        self.blood.emit_slash(cx, mid_y, direction, count=60)

        # Target paddle is now "dead" — halved and can't move
        target.vel[:] = 0

    def is_cut(self, side):
        """Check if a paddle is cut in half (dead)."""
        return self.left_cut if side == 'left' else self.right_cut

    def check_paddle_collision(self, left_paddle, right_paddle):
        """Check if paddles are colliding (ramming)."""
        lr = pygame.Rect(int(left_paddle.pos[0]), int(left_paddle.pos[1]),
                         int(left_paddle.width), int(left_paddle.height))
        rr = pygame.Rect(int(right_paddle.pos[0]), int(right_paddle.pos[1]),
                         int(right_paddle.width), int(right_paddle.height))

        if lr.colliderect(rr):
            rel_vel = left_paddle.vel - right_paddle.vel
            rel_speed = np.linalg.norm(rel_vel)

            if rel_speed > 0.5:
                # Separate paddles
                overlap_x = (lr.right - rr.left)
                if overlap_x > 0:
                    left_paddle.pos[0] -= overlap_x / 2
                    right_paddle.pos[0] += overlap_x / 2

                # Exchange momentum
                temp_vel = left_paddle.vel.copy()
                left_paddle.vel[:] = right_paddle.vel * 0.8
                right_paddle.vel[:] = temp_vel * 0.8

                # Ram blood effect if fast enough
                if rel_speed > self.RAM_DAMAGE_THRESHOLD:
                    impact_x = (lr.right + rr.left) / 2
                    impact_y = (lr.centery + rr.centery) / 2
                    self.blood.emit_impact(impact_x, impact_y,
                                           count=int(rel_speed * 3))

    def update(self, left_paddle, right_paddle, ball):
        """Per-frame update."""
        dt = 1 / 60  # fixed timestep

        self.left_sword.update(dt)
        self.right_sword.update(dt)

        # Decay damage flash
        for side in ('left', 'right'):
            if self._damage_flash[side] > 0:
                self._damage_flash[side] -= 1

        self.check_sword_hit(left_paddle, right_paddle)
        self.check_paddle_collision(left_paddle, right_paddle)

        # Sword-ball interaction (only if sword is ignited)
        if self.ball_grabbed_by is None:
            if self._check_sword_ball(self.left_sword, left_paddle, ball):
                pass  # hit handled
            elif self._check_sword_ball(self.right_sword, right_paddle, ball):
                pass

        # Update lightning bolts
        alive_bolts = []
        for bolt in self._lightning_active:
            bolt.life -= dt
            if bolt.life > 0:
                alive_bolts.append(bolt)
        self._lightning_active = alive_bolts

        # Bleed from damaged/cut paddles
        if self.left_cut:
            self._left_bleed_timer += 1
            if self._left_bleed_timer % 4 == 0:
                mid_y = left_paddle.pos[1] + left_paddle.height / 2
                self.blood.emit_drip(
                    left_paddle.pos[0] + left_paddle.width / 2,
                    mid_y, count=2)
        elif self.health['left'] < MAX_HEALTH:
            self._left_bleed_timer += 1
            if self._left_bleed_timer % 12 == 0:
                mid_y = left_paddle.pos[1] + left_paddle.height / 2
                self.blood.emit_drip(
                    left_paddle.pos[0] + left_paddle.width / 2,
                    mid_y, count=1)

        if self.right_cut:
            self._right_bleed_timer += 1
            if self._right_bleed_timer % 4 == 0:
                mid_y = right_paddle.pos[1] + right_paddle.height / 2
                self.blood.emit_drip(
                    right_paddle.pos[0] + right_paddle.width / 2,
                    mid_y, count=2)
        elif self.health['right'] < MAX_HEALTH:
            self._right_bleed_timer += 1
            if self._right_bleed_timer % 12 == 0:
                mid_y = right_paddle.pos[1] + right_paddle.height / 2
                self.blood.emit_drip(
                    right_paddle.pos[0] + right_paddle.width / 2,
                    mid_y, count=1)

        self.blood.update()

    def draw(self, surface, left_paddle, right_paddle):
        """Draw all combat visuals."""
        W = self._screen_w

        # Blood (under everything)
        self.blood.draw(surface)

        # Hands and swords for alive paddles
        if not self.left_cut:
            self.left_sword.draw_hands(surface, left_paddle, combat_mode=self.mode_left)
            if self.left_sword.ignited:
                self.left_sword.draw(surface, left_paddle)
            self._draw_health_bar(surface, left_paddle, 'left')
            self._draw_damage_state(surface, left_paddle, 'left')
        if not self.right_cut:
            self.right_sword.draw_hands(surface, right_paddle, combat_mode=self.mode_right)
            if self.right_sword.ignited:
                self.right_sword.draw(surface, right_paddle)
            self._draw_health_bar(surface, right_paddle, 'right')
            self._draw_damage_state(surface, right_paddle, 'right')

        # Cut paddle halves with blood gap
        if self.left_cut and self.left_cut_halves:
            self._draw_cut_paddle(surface, left_paddle, self.left_cut_halves)
        if self.right_cut and self.right_cut_halves:
            self._draw_cut_paddle(surface, right_paddle, self.right_cut_halves)

        # Lightning effects
        self._draw_lightning(surface)
        self._draw_lightning_charge_effect(surface, left_paddle, 'left')
        self._draw_lightning_charge_effect(surface, right_paddle, 'right')

        # Mode badges
        self._draw_mode_badges(surface, left_paddle, right_paddle)

        # Grab indicators
        if self.ball_grabbed_by:
            self._draw_grab_indicator(surface, "BALL GRABBED!", (255, 200, 0))
        if self.paddle_grabbed:
            self._draw_grab_indicator(surface, "PADDLE GRABBED!", (255, 100, 100))

    def _draw_lightning(self, surface):
        """Draw active lightning bolts with glow."""
        for bolt in self._lightning_active:
            ratio = bolt.life / bolt.max_life
            alpha = int(255 * ratio)
            r, g, b = bolt.color
            # Glow layer (thicker, dimmer)
            if len(bolt.path) >= 2:
                glow_color = (min(255, r), min(255, g), min(255, b))
                pts = [(int(x), int(y)) for x, y in bolt.path]
                pygame.draw.lines(surface, glow_color, False, pts, bolt.width + 4)
                # Core
                core_color = (min(255, r + 50), min(255, g + 50), min(255, b + 50))
                pygame.draw.lines(surface, core_color, False, pts, bolt.width)
                # White hot center
                pygame.draw.lines(surface, (255, 255, 255), False, pts, max(1, bolt.width - 2))

    def _draw_lightning_charge_effect(self, surface, paddle, side):
        """Draw crackling buildup when charging lightning."""
        frac = self.get_lightning_charge_frac(side)
        if frac <= 0:
            return
        cx = int(paddle.pos[0] + paddle.width / 2)
        cy = int(paddle.pos[1] + paddle.height / 2)

        # Crackling sparks around paddle
        num_sparks = int(frac * 12)
        for _ in range(num_sparks):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 30 + frac * 30)
            sx = cx + math.cos(angle) * dist
            sy = cy + math.sin(angle) * dist
            color = random.choice([(200, 200, 255), (150, 150, 255), (255, 255, 200)])
            pygame.draw.circle(surface, color, (int(sx), int(sy)), random.randint(1, 3))

        # Warning circle grows
        if frac > 0.5:
            radius = int(20 + frac * 40)
            warn_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            alpha = int(40 * frac)
            pygame.draw.circle(warn_surf, (200, 200, 255, alpha),
                               (radius, radius), radius, 2)
            surface.blit(warn_surf, (cx - radius, cy - radius))

    def _draw_mode_badges(self, surface, left_paddle, right_paddle):
        """Draw [FORCE] or [SABER] badge near each paddle."""
        for paddle, side in [(left_paddle, 'left'), (right_paddle, 'right')]:
            mode = self.get_mode(side)
            label = "[FORCE]" if mode == MODE_FORCE else "[SABER]"
            color = (100, 180, 255) if mode == MODE_FORCE else (255, 100, 100)
            text = FONT_TINY_DIGITAL.render(label, True, color)
            x = int(paddle.pos[0] + paddle.width / 2 - text.get_width() / 2)
            y = int(paddle.pos[1]) - 26
            surface.blit(text, (x, y))

    def _draw_health_bar(self, surface, paddle, side):
        """Draw HP pips above paddle."""
        hp = self.health[side]
        bar_y = int(paddle.pos[1]) - 38
        bar_x = int(paddle.pos[0])

        for i in range(MAX_HEALTH):
            px = bar_x + i * 7
            if i < hp:
                color = (0, 220, 0) if hp == 3 else (255, 200, 0) if hp == 2 else (255, 50, 50)
            else:
                color = (60, 60, 60)
            pygame.draw.rect(surface, color, (px, bar_y, 5, 5))

    def _draw_damage_state(self, surface, paddle, side):
        """Draw visual damage on paddle (cracks, flicker)."""
        hp = self.health[side]
        if hp >= MAX_HEALTH:
            return

        px = int(paddle.pos[0])
        py = int(paddle.pos[1])
        pw = int(paddle.width)
        ph = int(paddle.height)

        # Damage flash (white flash on hit)
        if self._damage_flash[side] > 0:
            flash_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            alpha = int(200 * (self._damage_flash[side] / 15))
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, (px, py))

        # Crack lines
        if hp <= 2:
            # First crack
            pygame.draw.line(surface, BLOOD_DARK,
                             (px + 2, py + ph // 3),
                             (px + pw - 2, py + ph // 3 + 5), 1)
        if hp <= 1:
            # Second crack + red pulse
            pygame.draw.line(surface, BLOOD_DARK,
                             (px + 1, py + ph * 2 // 3),
                             (px + pw - 1, py + ph * 2 // 3 - 4), 1)
            pygame.draw.line(surface, BLOOD_RED,
                             (px + pw // 2 - 3, py + ph // 4),
                             (px + pw // 2 + 3, py + ph * 3 // 4), 1)

            # Pulse red overlay
            pulse = abs(math.sin(time.monotonic() * 8)) * 0.4
            pulse_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pulse_surf.fill((255, 0, 0, int(pulse * 100)))
            surface.blit(pulse_surf, (px, py))

    def _draw_cut_paddle(self, surface, paddle, halves):
        """Draw a paddle that's been cut in half with a bleeding gap."""
        top_y, bottom_y, orig_height = halves
        half_h = orig_height / 2 - 4

        # Top half (slides up slightly)
        top_rect = pygame.Rect(int(paddle.pos[0]),
                               int(paddle.pos[1] - 3),
                               int(paddle.width), int(half_h))
        pygame.draw.rect(surface, paddle.color, top_rect)

        # Bottom half (slides down slightly)
        bottom_rect = pygame.Rect(int(paddle.pos[0]),
                                  int(paddle.pos[1] + orig_height / 2 + 3),
                                  int(paddle.width), int(half_h))
        pygame.draw.rect(surface, paddle.color, bottom_rect)

        # Blood in the gap
        gap_y = int(paddle.pos[1] + orig_height / 2)
        for i in range(-3, 4):
            bx = int(paddle.pos[0]) + random.randint(0, int(paddle.width))
            pygame.draw.circle(surface, BLOOD_RED,
                               (bx, gap_y + i), random.randint(1, 3))

    def _draw_grab_indicator(self, surface, text, color):
        """Draw grab state text."""
        W = self._screen_w
        font = FONT_TINY_DIGITAL
        rendered = font.render(text, True, color)
        surface.blit(rendered, (W // 2 - rendered.get_width() // 2, 75))

    def reset(self):
        """Reset all combat state (full game restart)."""
        self.ball_grabbed_by = None
        self.paddle_grabbed = None
        self.health = {'left': MAX_HEALTH, 'right': MAX_HEALTH}
        self.left_cut = False
        self.right_cut = False
        self.left_cut_halves = None
        self.right_cut_halves = None
        self._left_bleed_timer = 0
        self._right_bleed_timer = 0
        self._damage_flash = {'left': 0, 'right': 0}
        self.mode_left = MODE_FORCE
        self.mode_right = MODE_FORCE
        self._lightning_charge = {'left': 0.0, 'right': 0.0}
        self._lightning_frozen = {'left': False, 'right': False}
        self._lightning_active.clear()
        self.left_sword = Sword(is_left=True, paddle_color=self._left_color)
        self.right_sword = Sword(is_left=False, paddle_color=self._right_color)
        self.blood.reset()
