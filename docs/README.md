# Mii Plaza Decoder

## Overview

This is a project that decodes the file `meet.dat` from the Mii Plaza of the Nintendo 3DS. It is mostly used to extract statistics and information about the Miis that have been encountered in the plaza.

## Contributing

### To a [Mii](/mii.py)

There are still many bytes of code in the [Mii](/mii.py) data structure that their meaning is unknown. There are still [outfits](/mappings/outfit.py) that do not have their mapping and some [software](/mappings/software.py) whose ID is not in the other databases.

To investigate the unknown bytes, the `findPossibleBits` function from [Mii Plaza](/miiPlaza.py) could be used. Another option is to have 2 3DS consoles and slowly change the characteristics of one and checking the changes in the [unknown bytes](/miisUnknownBytes.csv) file.

### To the [Mii Plaza](/miiPlaza.py)

All other info except the Miis has not been decoded yet. You can find online resources that add collectables to the savefile, so this kind of software must show where that data is encoded. Here is an [example](https://github.com/marcrobledo/savegame-editors/blob/master/streetpass-mii-plaza/streetpass-mii-plaza.js).

### To the [graphs](/grapher.py)

To show a categorical piece of info of all Miis I wanted to create a pie chart with a scrollable legend because sometimes there are a lot of categories (last software used for example). Attempts were made with TKinter and matplotlib, but they didn't quite work as I intended. If you know more about graphs, please collaborate with the project.
