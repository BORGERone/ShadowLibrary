<!-- Language Flags -->
<p align="center">
  <a href="README.ru.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Flag_of_Russia.svg/1280px-Flag_of_Russia.svg.png" alt="Russian" width="30"/></a>
  <a href="README.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Flag_of_the_United_States.svg/1200px-Flag_of_the_United_States.svg.png" alt="English" width="30"/></a>
  <a href="README.fr.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Flag_of_France.svg/40px-Flag_of_France.svg.png" alt="French" width="30"/></a>
  <a href="README.es.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Spain.svg/40px-Flag_of_Spain.svg.png" alt="Spanish" width="30"/></a>
  <a href="README.de.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Germany.svg/1200px-Flag_of_Germany.svg.png" alt="German" width="30"/></a>
  <a href="README.it.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Flag_of_Italy.svg/1200px-Flag_of_Italy.svg.png" alt="Italian" width="30"/></a>
  <a href="README.pl.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Flag_of_Poland.svg/500px-Flag_of_Poland.svg.png" alt="Polish" width="30"/></a>
  <a href="README.pt.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Brazil.svg/1200px-Flag_of_Brazil.svg.png" alt="Portuguese" width="30"/></a>
  <a href="README.ja.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Flag_of_Japan.svg/1200px-Flag_of_Japan.svg.png" alt="Japanese" width="30"/></a>
  <a href="README.ko.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/1200px-Flag_of_South_Korea.svg.png" alt="Korean" width="30"/></a>
  <a href="README.zh.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_the_People%27s_Republic_of_China.svg/1200px-Flag_of_the_People%27s_Republic_of_China.svg.png" alt="Chinese" width="30"/></a>
  <a href="README.hi.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/1200px-Flag_of_India.svg.png" alt="Hindi" width="30"/></a>
</p>

<h1 align="center">
  <img alt="Shadow Library" src="https://img.shields.io/badge/Shadow-Library-blue?style=for-the-badge&logo=steam&logoColor=white">
</h1>

<p align="center">
  <strong>Steam Game Unlock Tool</strong>
</p>

<p align="center">
  <a href="https://github.com/BORGERone/ShadowLibrary/stargazers">
    <img src="https://img.shields.io/github/stars/BORGERone/ShadowLibrary?style=flat-square&logo=github" alt="Stars">
  </a>
  <a href="https://github.com/BORGERone/ShadowLibrary/network/members">
    <img src="https://img.shields.io/github/forks/BORGERone/ShadowLibrary?style=flat-square&logo=github" alt="Forks">
  </a>
  <a href="https://github.com/BORGERone/ShadowLibrary/issues">
    <img src="https://img.shields.io/github/issues/BORGERone/ShadowLibrary?style=flat-square&logo=github" alt="Issues">
  </a>
  <a href="https://github.com/BORGERone/ShadowLibrary/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/BORGERone/ShadowLibrary?style=flat-square&logo=github" alt="License">
  </a>
</p>

---

## Description

**Shadow Library** is a software solution that expands Steam users' capabilities through alternative game activation methods. The application provides a convenient web interface for managing game unlocks through popular tools: **SteamTools** and **GreenLuma**.

---

## Features

### Operation Modes

| Mode | Description |
|------|-------------|
| **SteamTools (Steam++)** | Popular tool for unlocking games through license emulation |
| **GreenLuma** | Alternative solution for bypassing Steam checks |

### Manifest Sources

| Source | Description |
|--------|-------------|
| **SteamAutoCrack / ManifestHub** | Actual manifests with automatic updates |
| **ManifestAutoUpdate** | Alternative manifest source |

### Advantages

- Automatic manifest download from repositories
- Unlock file configuration without manual intervention
- Modern web interface with dark theme
- Multi-language support (Russian, English, Chinese, and more)
- History of unlocked games with depot and tool information

---

## Requirements

Before starting, make sure the following requirements are met:

| Requirement | Description | Link |
|-------------|-------------|------|
| **SteamTools** | Required for SteamTools mode | [steamtools.net](https://steamtools.net/) |
| **Steam** | Installed Steam client | [store.steampowered.com](https://store.steampowered.com/) |

### Installing SteamTools

The program requires SteamTools, which can be downloaded from the official developer website:

1. Visit the official website **[SteamTools](https://steamtools.net/)**
2. Download the latest version of the program
3. Follow the installer instructions

---

## Usage Instructions

### Initial Setup

1. On first launch, open the **"Steam Path"** menu in the top right corner
2. Specify the path to the root Steam folder (where `steam.exe` is located)
3. Click **"Save"**

### Unlocking a Game

#### Step 1. Enter Game Identifier

In the input field, specify:
- **AppID** of the game (numeric value, e.g., `2486820`)
- Or **full link** to the game page in Steam

#### Step 2. Select Unlock Tool

| Tool | Description |
|------|-------------|
| **SteamTools** | Recommended for most games. Creates Lua script in `config/stplug-in` folder |
| **GreenLuma** | Alternative method. Modifies `config.vdf` and creates files in `AppList` |

#### Step 3. Select Manifest Source

| Source | Description |
|--------|-------------|
| **SteamAutoCrack** | Actual manifests from ManifestHub repository |
| **ManifestAutoUpdate** | Alternative manifest source |

#### Step 4. Launch

Click the **"Unlock Game"** button

After successful processing, the game will appear in the list of unlocked games.

### Managing Unlocked Games

| Action | Description |
|--------|-------------|
| **View List** | All unlocked games are displayed at the bottom of the page |
| **Delete** | Click "Delete" to rollback changes and remove entry from database |

---

## Limitations and Compatibility

### Supported Games

- Single-player games with Steam DRM protection
- Games with depots and manifests in public access

### Limitations

| Limitation | Description |
|------------|-------------|
| **Denuvo** | Games can be downloaded through Shadow Library, but Denuvo protection will prevent launch — additional unlock or bypass required |
| **Online Games** | Multiplayer functionality is limited. Online may work if license is available through Family Sharing, but not always |
| **Third-party Launchers** | Games requiring additional launchers (`EA App`, `Ubisoft Connect`, `Battle.net`) are mostly not supported |

### Denuvo Workarounds

1. Launch the legitimate version of the game on your computer — this allows Denuvo to authorize the device, after which you can use the cracked version through Shadow Library
2. Using hypervisor bypasses

---

## Disclaimer

> **Warning**
>
> This project is intended exclusively for **educational and research purposes**.
>
> Authors bear no responsibility for any consequences of using this software.
> Use at **your own risk**.
>
> It is recommended to purchase games in official stores to support developers.

---

## License

The project is distributed without an explicit license. All rights reserved.

---

## Contacts

| Resource | Link |
|----------|------|
| **GitHub** | [BORGERone/ShadowLibrary](https://github.com/BORGERone/ShadowLibrary) |
| **Author** | BORGER |

---

<p align="center">
  <strong>Shadow Library</strong> | Created with Python and FastAPI
</p>
