# 🚀 SkyBurner Ultimate

**The most intense arcade shooter for Pythonista 3 & iOS Devices**
*Powered by the Atlas Nexus Engine · PCVR STUDIOS*

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3-blue.svg)
![Platform](https://img.shields.io/badge/Platform-iOS%20%2F%20Pythonista%203-lightgrey.svg)

---

## Downloads

| Download | Link |
|---|---|
| **🎮 Game Download** | [Download SkyBurner Ultimate](https://discord.com/channels/1316937801995911198/1484003872178573495/1484552464639332605) |
| **🎵 Music Download** | [Download Game Music](https://discord.com/channels/1316937801995911198/1484003872178573495/1484595490828845229) |

---

## Community

| | Link |
|---|---|
| 💬 **Discord** | [Join our Discord](https://discord.gg/E7bW3Zh4x) |
| 🐦 **Twitter / X** | [@pcvr2024](https://x.com/pcvr2024?s=21) |
| 🎮 **PCVR Games Hub** | [AIVaneer/Eve-Repository](https://github.com/AIVaneer/Eve-Repository) |

---

## Overview

SkyBurner Ultimate is a vertical-scrolling arcade space-shooter written
entirely in Python for [Pythonista 3](http://omz-software.com/pythonista/)
on iPhone and iPad.  No external assets are required — every visual is drawn
with Pythonista's built-in `scene` and `ui` modules, giving the game a
clean vector-art look that runs at full frame-rate on any modern iOS device.

---

## Features

| Feature | Details |
|---|---|
| **Atlas Nexus Engine** | Custom entity-component system with AABB collision, wave management, and score/multiplier tracking |
| **4 weapon tiers** | Single laser → Dual cannon → Triple spread → Homing missiles |
| **3 enemy types** | Fighter, Cruiser, Boss (every 5th wave) |
| **Multi-phase boss** | Entry → Attack 1 → Attack 2 → Rage mode |
| **Power-ups** | Weapon upgrade, shield boost, health pack, extra bomb, speed burst |
| **Combo system** | Build kill-streaks to raise your score multiplier (up to ×8) |
| **Scrolling star-field** | 115-star parallax background |
| **Full HUD** | Score, high-score, health bar, shield bar, lives, bomb count, wave indicator, boss health bar |

---

## Controls

| Input | Action |
|---|---|
| **Drag left side** of screen | Move your ship |
| **Tap right side** of screen | Detonate a screen-clearing BOMB |
| *(automatic)* | Your ship fires continuously |

---

## How to Run

1. Install **Pythonista 3** from the App Store.
2. Copy the three files into a folder inside Pythonista:
   - `atlas_nexus.py` — Atlas Nexus Engine (no dependencies)
   - `entities.py` — Game entity classes + visual node builders
   - `skyburner.py` — Main scene and entry point
3. Open `skyburner.py` and tap the **▶ Run** button.

---

## File Structure

```
atlas_nexus.py   Core engine — entity/component system, collision,
                 score management, wave management
entities.py      Entity classes (player, enemies, bullets, power-ups)
                 and Pythonista scene-node builder helpers
skyburner.py     Pythonista Scene subclass, HUD, star-field,
                 game states, touch input, entry point
```

---

## Built With

| Component | Details |
|---|---|
| **Python 3** | 100% Python — no compiled extensions |
| **Pythonista 3** | Uses the built-in `scene` and `ui` modules for all rendering and input |
| **Atlas Nexus Engine** | Custom in-house entity-component engine (collision, wave management, scoring) |
| **No external dependencies** | Everything ships in three `.py` files |

---

## Tips

- Destroy **5 enemies in quick succession** to increase your multiplier.
- Wave **5, 10, 15 …** are Boss waves — save at least one bomb!
- Collect the **green W capsule** to upgrade your weapon through four tiers.
- The **blue shield capsule** absorbs damage; it auto-deactivates when
depleted and must be recharged by collecting another capsule.
- Every wave cleared awards a **wave-clear bonus** on top of kill scores.

---

## Related Projects

| Project | Description |
|---|---|
| [**Warp Protocol**](https://github.com/AIVaneer/Eve-Repository) | Fast-paced arcade shooter with cinematic intro, dynamic starfield, and diverse enemy archetypes |
| [**PCVR Game Shell**](https://github.com/AIVaneer/PCVR-game-shell-) | Foundational 2D VR game framework for Oculus Quest 3 |

---

## About PCVR Studios

> PCVR Studios builds immersive games across multiple platforms — from iOS arcade shooters to VR experiences on Oculus Quest 3. All projects are powered by custom in-house engines and open-source collaboration.

---

*© PCVR STUDIOS 2026 · Atlas Nexus Engine v1.0*