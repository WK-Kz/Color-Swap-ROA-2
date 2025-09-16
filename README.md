# Color Swap Guide for Rivals of Aether 2
#### Credit to both [Keryan666](https://gamebanana.com/tools/18380) for the original tool and [Pixel956](https://gamebanana.com/tools/18562) for providing an updated version of the tool

This program allows you to change character colors in **Rivals of Aether 2** on **Linux**. 

## Requirements to Run:
python > 3.12 
wine
Pillow

#### Fedora:
`sudo dnf install python3-pillow-tk`
`sudo dnf install wine`

#### Arch/Steam Deck:
`sudo pacman -S python-pillow`
`sudo pacman -S wine`
* I am not in possession of a steam deck / arch distro, so this can be subject to change.

## Installation

### Download
- Download the zip file from [Releases](https://github.com/WK-Kz/Color-Swap-ROA-2/releases) and extract the ZIP file of the program.

### Creating the Mods Folder **Optional**
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
    - Type in your terminal `chmod +x Start.sh` and press enter

## Terms of Use:
This repository is licensed under [Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/).
