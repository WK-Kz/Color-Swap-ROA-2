# Color Swap Guide for Rivals of Aether 2
#### Credit to both [Keryan666](https://gamebanana.com/tools/18380) for the original tool and [Pixel956](https://gamebanana.com/tools/18562) for providing an updated version of the tool and updated assets.

This program allows you to change character colors in **Rivals of Aether 2** on **Linux**. 

## Requirements to Run:
- python > 3.12 
- wine
- Pillow

#### Fedora:
1. `sudo dnf install python3-pillow-tk`
1. `sudo dnf install wine`

#### Arch/Steam Deck:
1. `sudo pacman -S python-pillow`
2. Wine install on Steam Deck is under investigation right now.
* I am not in possession of a steam deck / arch distro, so this can be subject to change.

## Installation

### Download
- Download the zip file from [Releases](https://github.com/WK-Kz/Color-Swap-ROA-2/releases) and extract the ZIP file of the program.

### [Optional] Creating the Mods Folder 
With the new fork, it will prompt you to provide a direct path to the Rivals2/Paks folder. Once a valid directory has been provided, it will generate a Mods folder. However, you must still select the mods folder when generating your recolored skin.

If this folder already exists, nothing will happen, and the program will continue as usual.

**Original Instructions**
- Create a folder named `Mods` in the following location within your game directory:

   ```css
   ~/.steam/steam/steamapps/common/Rivals 2/Rivals2/Content/Paks/Mods
   ```

## Usage

### Warning
- Make sure to close the game before using the program.

### Launching the Program
- Unzip this folder
- Right click Start.sh
- Click `Run as Program`

### Selecting the Mods Folder
- Click on the yellow button and select the location of the `Mods` folder you created.

### Customization
- Now you can select the character/skin/color to modify.
- Choose your preferred color for the selected part by clicking on the colors or entering the HEX color code directly (e.g., #FFFFFF).
- After making changes, you can save the preset to reuse these colors later.
- Finally, click on "Replace Colors" to apply the modification in the game.

### Troubleshooting:
- I can't run the Start.sh script
    - Open terminal and navigate to this folder
    - Type in your terminal `chmod +x Start.sh` and press enter. Keep the terminal open.
    - Go back to your file explorer (ie. Nautilus / Dolphin / Etc ), attempt to right click again, and click on 'Run As Program'
    - "That still doesn't work"
        - In your terminal: type `./Start.sh`

- I'm geting `Python3 is not installed` 
    - Make sure your system has python3 installed. Based on your distro, use your package manager to install python3 and python3-pillow

- I'm able to successfully run the program; however, it's stating that wine isn't installed.
    - Make sure your system has wine installed. Based on your distro, use your package manager to install wine.


#### Q&A:
- How often will this tool be updated?
    - Whenever I have time or if someone wants to make a PR.
    - It also depends on when new files are provided from Pixels956. This repository was originally focused on getting the Color Mod tool to work and generate the appropriate .pak files.

- Why is wine required?
    - Based on investigation, UnrealPak provided from the orgiinal creator is version 4.17.2. Unreal Engine does not provide that binary, and attempting to build it from source requires a number of tweaks to an xml file and also requires clang < 4.0. It is not within the scope of this repository at this point in time to get an isolated UnrealPak 4.17.2 binary for Linux Systems.

## Terms of Use:
This repository is licensed under [Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/).
