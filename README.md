# Travel Map

I always wanted one of those maps where you scratch off the countries you've been to. But I would not know where to
put it, and I'm pretty sure it would not look good... so instead I made a webapp for it!

# Usage

1. Populate the `config.toml` with the countries and states you've visited.

2. Run the following command from the root folder of the repo.


```bash
docker build -t travel-map .
docker run -dp 127.0.0.1:7001:7001 travel-map
```


Or, if you want to run without docker:
```bash
poetry run streamlit -- run travel_map/app.py
```


# Improvement ideas

- Store the date (or year) of last visit, and show color map by age of last visit
- Store the count of visits or array of dates, and show visit count or weighted average of visits