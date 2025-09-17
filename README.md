# FoodJustice_RenPy

A repo for developing the lightweight, RenPy version of the Food Justice environment.

## Setup Instructions


1. **Clone the repository** to your local machine: [https://github.com/oele-isis-vanderbilt/FoodJustice_RenPy.git]()

   
   1. You should be on the `main` branch by default. If you are doing development work, create a new branch with your initials (i.e. `mv_featurework`) that you will push your changes to before updating the main branch. This is to ensure that broken code doesn’t accidentally get sent to the live server (which pulls from `main`)
2. **Setting up the RenPy SDK:**

   
   1. Download the RenPy SDK from https://www.renpy.org/latest.html. A file that looks like `renpy-8.3.7-sdk.dmg` will download.
   2. Unzip the `.dmg` file. This unzipped folder will be called `renpy-8.3.7-sdk`.
   3. Keep your project folder (`FoodJustice_RenPy`) and the SDK folder (`renpy-8.3.7-sdk`) in the same parent directory, for example:
      * `/Users/morganavickery/Documents/GitHub/FoodJustice_RenPy/`
      * `/Users/morganavickery/Documents/GitHub/renpy-8.3.7-sdk/`
   4. Open the terminal and navigate to the RenPy SDK folder:
      * `cd /Users/morganavickery/Documents/GitHub/renpy-8.3.7-sdk/`
   5. Run the command in the terminal: `chmod +x renpy.sh` (this will make the renpy.sh file executable - you should only have to do this once)

# Launch Instructions \[GUI\]


1. From the terminal, navigate to the parent folder of the RenPy SDK and the FoodJustice_RenPy repo, then run the following command: `./renpy.sh SciStoryPollinators/`


::: warning -- If you see a "permission denied" error, run: `chmod +x renpy.sh` from inside the RenPySDK folder first, and then try again. :::

# Launch Instructions \[Web\]


1. Open the renpy launcher (by double-clicking the `renpy.app` file in the in the unzipped `renpy-8.3.7-sdk` folder)
2. There should be a list of "projects" on the left side of the window. Click on the `SciStoryPollinators` project.
3. Under Actions, click on `Web`

   
   1. **Build Web Application:** This option creates a web-ready package of your Ren'Py game. It generates a web.zip file and a folder containing all your game's assets. This package is designed for web hosting; you can't directly run the game from the folder. You'd need to upload this folder (or the .zip file) to a web server to make your game accessible to others.
   2. **Build and Run in Browser:** This option also packages your game for the web, but it goes a step further by automatically running a local web server and opening the game in a browser.

      
      1. This will open a browser tab with the game running in it. The URL will be something like `http://127.0.0.1:8042/index.html` or `localhost:8042/`. As you are editing code, you can refresh this page to see your changes in real-time.
      2. You may be prompted to download `RenPy Web` -- approve these downloads/installations as needed
      3. As you are editing code, you can `Build & Run in Browser` again to update the browser version and test your changes. If you're concerned your browser isn't reflecting the recent code changes, are seeing weird errors/behaviors, have recently switched branches, you should check the `Force Recompile` box before clicking `Build & Run in Browser`. This will ensure that the browser version is up-to-date with the latest code changes.



:::tip
**FYI**: After building, you may notice that a new folder has appeared in your local FoodJustice-RenPy repo called `SciStoryPollinators-1.0-dists`. Running the web version of the game will create this folder, which contains the web-ready package of your Ren'Py game. This folder is what you would upload to a web server to host your game online.

:::


