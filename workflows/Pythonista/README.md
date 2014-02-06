# qtodoflow

Script that takes arguments, filters TaskPaper lists and prints them in Pythonista console.

![pythonista](http://procrastinationlog.net/img/pythonista.png)

Can be launched from Launch Center Pro with url scheme:

    pythonista://qtodoflow?action=run&args={query}

## Installation

1. Install and configure [seamless dropbox](https://github.com/bevesce/Seamless-Dropbox/blob/master/seamless_dropbox.py), you'll need app key and secret from [dropbox developer site](https://www.dropbox.com/developers/apps) (probably you should read what seamless dropbox does)
2. Install todoflow - you can do this running *import todolow.py* or manually (if so read about Hacky stuff at the end of readme)
3. Install parsedatetime if you want to use it, manually or using *import parsedatetime.py*
4. Copy qtodoflow.py
5. Done

### Hacky stuff

Obviously using *open* in Pythonista won't work when using path from OSX, so before downloading every file with *import todoflow.py* I prepend it with this code:

    from seamless_dropbox import open

it overwrites *open* from standard library with *open* from *seamless_dropbox* that will work in Pythonista (only for reading, at least for now), it downloads files from dropbox (it can take a while).