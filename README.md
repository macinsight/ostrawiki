# OstraWiki

## About
This repository contains scripts related to uploading the data of the game [Ostranauts](https://store.steampowered.com/app/1022980/Ostranauts/) into its [Wiki](https://ostranauts.wiki.gg/).

## Dependencies
To use the files in this repository, the following prerequisites have to be met:
* Python 3 must be available on your system.
* Ostranauts must be installed. Yes, a legal copy. No, don't argue with me. Support BBG.

## How to use this stuff
So you want to support the ~~war~~ wiki effort! Good human! Or cat. Or whatever, really. Good entity.
### Execution details
1. Download this repository either by cloning or by [downloading the .zip file](https://github.com/macinsight/ostrawiki/archive/refs/heads/main.zip).
2. Place the script in your `condowners` folder.
3. Execute the script as follows:
  `python3 infobox.py ItmCooler01On condowners.json`

### Parameters
The script takes two parameters as inputs. The first (`ItmCooler01n`) is the `strItemDefinition` value of the item you're looking for. The second is the condowners.json file. This can be adapted for the other condowner files as needed.

### Output
The output will look like this for the item specified above:
```
{{Quote|A Sokol cooling unit, consisting of an internal air conditioner connected to radiator panels on the external hull. Safe cabin temperatures fall between 290 and 300 degrees Kelvin. Can be linked to a thermostat.|Item description}}
{{Infobox item
|images=
    ItmCooler01Off.png:Intact,
    ItmCooler01OffDmg.png:Damaged
| Name = Cooler
| Type = Item
| Category = HVAC
| ItemDefinition = ItmCooler01On
| Interactions = GUICooler
| Conditions = HiddenInv, Installed, Cooler, SalvageValueHigh, Solid, ReadyHeat, Powered, Mechanical, Signalable
| Stats = BasePrice, HeatArea, HeatVol, DismantleProgressMax, InstallProgressMax, UninstallProgressMax, Mass, SolidTemp, DamageMax
| BasePrice = 7360.0
| HeatArea = 2.0
| HeatVol = 1.0
| DismantleProgressMax = 250
| InstallProgressMax = 700
| UninstallProgressMax = 700
| Mass = 130.0
| SolidTemp = 600.0
| DamageMax = 3
| Portrait = ItmCooler01Off
}}

```

Safe travels,
macinsight
