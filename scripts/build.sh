# Invoke plugins here to populate the cache
python3 -m plugins.xkcd 480x480       # Presto (Full Res)
python3 -m plugins.xkcd 800x480       # Inky 7.3"
python3 -m plugins.xkcd 600x448       # Inky 5.7"
python3 -m plugins.xkcd 640x400       # Inky 4.0"
python3 -m plugins.jokeapi 480x480 $1 # Presto (Full Res)
python3 -m plugins.jokeapi 800x480 $1 # Inky 7.3"
python3 -m plugins.jokeapi 600x448 $1 # Inky 5.7"
python3 -m plugins.jokeapi 640x400 $1 # Inky 4.0"
python3 -m plugins.nasa_apod 480x480  # Presto (Full Res)
python3 -m plugins.nasa_apod 800x480  # Inky 7.3"
python3 -m plugins.nasa_apod 600x448  # Inky 5.7"
python3 -m plugins.nasa_apod 640x400  # Inky 4.0"
