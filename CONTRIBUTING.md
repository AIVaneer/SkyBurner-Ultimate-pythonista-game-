# Contributing to SkyBurner Ultimate

Thank you for your interest in contributing to **SkyBurner Ultimate**! 🚀  
Whether you're reporting a bug, suggesting a feature, or submitting code — every contribution helps make the game better. We appreciate your time and effort.

---

## How to Report Bugs

Found a bug? Please [open a GitHub Issue](https://github.com/AIVaneer/SkyBurner-Ultimate-pythonista-game-/issues/new) and include the following:

- **Steps to reproduce** — what did you do to trigger the bug?
- **Expected behaviour** — what should have happened?
- **Actual behaviour** — what actually happened?
- **Device info** — iPhone or iPad model (e.g. iPhone 14 Pro, iPad Air 5th gen)
- **Pythonista 3 version** — found in Settings → Pythonista 3 → Version

The more detail you provide, the faster we can track it down.

---

## How to Suggest Features

Have an idea that would improve the game? [Open a GitHub Issue](https://github.com/AIVaneer/SkyBurner-Ultimate-pythonista-game-/issues/new) and:

1. Add the **`enhancement`** label to the issue.
2. Describe the feature clearly — what it does and how it would work.
3. Explain **why** it would improve the gameplay or developer experience.

We review all suggestions and will respond as soon as possible.

---

## How to Submit a Pull Request

1. **Fork** this repository to your own GitHub account.
2. **Create a feature branch** from `main`:
   ```
   git checkout -b feature/my-improvement
   ```
3. **Make your changes** and keep each commit focused on a single change.
4. **Test in Pythonista 3** on a real iOS device or the Pythonista simulator.
5. **Submit a Pull Request** with a clear title and description explaining what you changed and why.

We'll review your PR and may suggest adjustments before merging.

---

## Code Style Guidelines

| Rule | Detail |
|---|---|
| **Language** | Python 3 only |
| **Style** | Follow [PEP 8](https://peps.python.org/pep-0008/) |
| **Type hints** | Use type hints where possible |
| **Compatibility** | Must work with Pythonista 3's `scene` and `ui` modules |
| **Dependencies** | Zero external dependencies — keep it pure Python |

Please do not introduce third-party packages. All rendering must go through Pythonista's built-in `scene` and `ui` modules.

---

## File Structure Reference

The entire game lives in three files:

```
atlas_nexus.py   Core engine — entity/component system, collision,
                 score management, wave management

entities.py      Entity classes (player, enemies, bullets, power-ups)
                 and Pythonista scene-node builder helpers

skyburner.py     Pythonista Scene subclass, HUD, star-field,
                 game states, touch input, entry point
```

When making changes, keep logic in the appropriate file to preserve this architecture.

---

## Community

| Platform | Link |
|---|---|
| **💬 Discord** | [Join PCVR Studios](https://discord.gg/E7bW3Zh4x) |
| **🐦 Twitter / X** | [@pcvr2024](https://x.com/pcvr2024?s=21) |
| **🏠 PCVR Games Hub** | [Eve-Repository](https://github.com/AIVaneer/Eve-Repository) |

---

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE) — the same license that covers this project.

---

*© PCVR STUDIOS 2026 · Atlas Nexus Engine v1.0*
