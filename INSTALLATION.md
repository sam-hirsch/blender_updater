This tool uses python 3 and PySide6 (QT bindings for python).

Run `install.sh`:
```
$ ./install.sh
```

Doing so creates a happy little python environment with everything set up.

The configuration file `blender_updater.conf` allows you to specify your blender git project location and customize the location of builds. Before running the application for the first time, set the `BASE_PATH` variable appropriately. If you followed the building Blender wiki instructions, your `BASE_PATH` is probably `/your/home/folder/blender-git/blender`.

 To run the application do:
 ```
$ ./run.sh
 ```

Notes for nerds:

- If you're having problems after editing blender_updater.sh, make sure you're using unix newlines.
- The python env is just a little home for PySide6. If you already have PySide you don't need to install it again or make an env. Adjust the version appropriately.
- blender_updater.conf is valid bash. Source it wherever you want.

Enjoy :-)
