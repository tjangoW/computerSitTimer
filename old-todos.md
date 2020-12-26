# Todos/Issue trackers

- Advanced features (wishes):
    - Visual
        - [x] icon
        - [ ] tray icon & main icon that changes over time
    - [x] stay just at tray notification and no active window and run in background
        - using not the native tray icon but good enough  
    - [X] notification sound
    - [ ] dim out screen when time's up
    - [x] always on top when time is up!
        - `window.keepOnTop` does not work, instead use solution from 
          [this GitHub issue](https://github.com/PySimpleGUI/PySimpleGUI/issues/2977)
- Bug-ish
    - [ ] (medium) as Ui is blocking call, any action on the tray will queue up and executed after UI is closed
    - [ ] (performance, enhancement) `ShowUI` call is a bit slow, takes about 8 seconds for the ui to pop-up when time's up
    - [ ] (performance, minor) right-click on tray hangs the loop, as in time is not updated during that time.
          Not really that much of an issue for me because I won't right click all the time and accurate time is not needed.
