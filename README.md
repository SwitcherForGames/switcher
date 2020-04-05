# Switcher

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](/LICENSE)
[![Code style: Black](https://img.shields.io/badge/code_style-black-black)](https://github.com/psf/black)

*Note: Switcher is still in development.*

Switcher is a free, open-source program which allows you to easily create and switch between graphics/keymap profiles for games. Switcher also supports game saves.

Possible use cases:

- You want to tweak some graphics settings or keybindings without losing your current settings.
- You switch between VR and non-VR mode in games, which means changing graphics settings and keybindings every time.
- You want to back up your game saves, or switch between game saves for two different players in a game with only one save slot.

![Screenshot of the main Switcher window.](/docs/img/switcher.png)

> **Disclaimer:** The images shown in the above screenshot are not distributed with Switcher, and there is no affiliation between their copyright holders and the Switcher developers.

## Supported games

Switcher uses a plugin architecture to theoretically support any game. Plugins are automatically downloaded from GitHub, providing a seamless experience. 

If a plugin doesn't exist for your favourite game, you can [create one](https://github.com/SwitcherForGames/plugin-tutorial) for everyone to use! Most games can be supported without writing a single line of code, but more advanced plugins can also be implemented in Python.

## Installation

To install Switcher, go to the [Releases](https://github.com/SwitcherForGames/switcher/releases) page, expand the `Assets` dropdown and download the executable appropriate for your system.

> :warning: Do not download Switcher from any other website. This repository is the only legitimate source.

## Security

Security is important to us. This section explains why Switcher can be trusted on your system.

### Plugins

Plugins are able to run arbitrary code on your system. To mitigate this, potentially huge, security risk:

- Only plugins published by the [SwitcherForGames](https://github.com/SwitcherForGames) can be installed by default.
- To allow safe installation of community plugins, they will be vetted and forked by [SwitcherForGames](https://github.com/SwitcherForGames).

### Open-source

Switcher is open-source, so you can inspect the entire codebase for malicious code. If you don't trust the installers, you can download and run the program from source!

A common misconception is that since anyone can contribute to an open-source program, an attacker could insert malicious code. While it's true that anyone can contribute, contributions (known as "pull requests") are carefully inspected and won't be accepted unless they are completely safe.

### Windows Smartscreen

When running the installer, Windows Smartscreen will block it with a dialog. This dialog must be dismissed by clicking `More info`, then `Run anyway`.

#### Why does this happen?

To ensure that an executable was produced by a genuine source, it can be signed with a digital certificate. 

This protects against:

- Cases where an attacker hacks a website and replaces the real executable with a modified version.

This does **not** protect against:

- Cases where a malicious actor uses their certificate to sign a malicious executable.

#### Why does Switcher not have a certificate?

To filter out less determined attackers, certificates are expensive. Unfortunately, this approach also filters out developers of free software.

#### How is this mitigated?

- Executables are only distributed via GitHub Releases, which is much more secure than using a self-hosted website.
- The only GitHub account authorised to publish Releases is protected by a strong password and 2-factor authentication.

### Installing updates

Switcher is able to automatically download and install updates. To ensure that this process is safe:

- New releases are downloaded over HTTPS, directly from the GitHub Releases page.
- When a new release is downloaded, the installer will only be executed if its `sha256` checksum matches the checksum posted on the Releases page. 

## License

You may use, distribute and modify this software under the terms of the [GNU General Public License v3.0](https://opensource.org/licenses/GPL-3.0). See [LICENSE](/LICENSE).