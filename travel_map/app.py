import json
from pathlib import Path

import branca
import folium
import pandas as pd
import pydantic
import streamlit as st
from streamlit_folium import st_folium
import tomli


class Config(pydantic.BaseModel):
    countries: list[str]
    states: list[str]

    @pydantic.validator("countries")
    def validate_countries(cls, countries):
        valid = geo_countries()
        valid_names = {entry["properties"]["name"] for entry in valid["features"]}

        for country in countries:
            if country not in valid_names:
                raise ValueError(f"Country {country} not found.")

        return countries


    @pydantic.validator("states")
    def validate_states(cls, states):
        valid = geo_states()
        valid_names = {entry["properties"]["name"] for entry in valid["features"]}

        for state in states:
            if state not in valid_names:
                raise ValueError(f"State {state} not found.")

        return states

    def visited_countries(self) -> pd.DataFrame:
        return pd.DataFrame(dict(
            country=self.countries,
            visited=[1] * len(self.countries)
        ))

    def visited_states(self) -> pd.DataFrame:
        return pd.DataFrame(dict(
            state=self.states,
            visited=[1] * len(self.states)
        ))


def main():
    st.set_page_config("Visited Countries", layout="wide")
    st.title("Visited Countries")

    config = get_config()
    show_map(config)

    left, right = st.columns(2)
    left.subheader("Countries")
    left.table(config.visited_countries())

    right.subheader("US States")
    right.table(config.visited_states())


def asset_folder() -> Path:
    return Path.cwd() / 'assets'


def config_file() -> Path:
    return asset_folder().parent / "config.toml"


def get_config() -> Config:
    return Config(**tomli.loads(config_file().read_text()))

def geo_states():
    return json.loads((asset_folder() / "us_states.json").read_text())


def geo_countries():
    return json.loads((asset_folder() / "world_countries.json").read_text())


# colormap = branca.colormap.LinearColormap(
#     vmin=df["change"].quantile(0.0),
#     vmax=df["change"].quantile(1),
#     colors=["red", "orange", "lightblue", "green", "darkgreen"],
#     caption="State Level Median County Household Income (%)",
# )


def show_map(config: Config):
    state_geo = geo_states()
    state_data = config.visited_states()

    countries_geo = geo_countries()
    # Here we remove the US since we're going to be using states instead
    countries_geo["features"] = [c for c in countries_geo["features"] if c["id"] != "USA"]
    country_data = config.visited_countries()

    m = folium.Map(location=[48, -102], zoom_start=3)

    folium.Choropleth(
        geo_data=countries_geo,
        name="choropleth",
        data=country_data,
        columns=["country", "visited"],
        key_on="feature.properties.name",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_opacity=0,
        legend_name="Visited Countries",
        highlight=True,
    ).add_to(m)

    # state_popup = folium.GeoJsonPopup(
    #     fields=["name"],
    #     aliases=["State"],
    #     localize=True,
    #     labels=True,
    #     style="background-color: yellow;",
    # )

    # state_tooltip = folium.GeoJsonTooltip(
    #     fields=["name"],
    #     aliases=["State:"],
    #     localize=True,
    #     sticky=False,
    #     labels=True,
    #     style="""
    #         background-color: #F0EFEF;
    #         border: 2px solid black;
    #         border-radius: 3px;
    #         box-shadow: 3px;
    #     """,
    #     max_width=800,
    # )


    folium.Choropleth(
        geo_data=state_geo,
        name="choropleth",
        data=state_data,
        columns=["state", "visited"],
        # key_on="feature.id",  # for state two letter shorthand
        key_on="feature.properties.name",
        # fill_color="YlGn",
        # fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_opacity=0,
        legend_name="Visited States",
        highlight=True,
    ).add_to(m)

    state_popup = folium.GeoJsonPopup(
        fields=["name",],
        aliases=["State: "],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    state_tooltip = folium.GeoJsonTooltip(
        fields=["name"],
        aliases=["State: "],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    folium.GeoJson(
        state_geo,
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "transparent",
        },
        # style_function=lambda x: {
        #     "fillColor": colormap(x["properties"]["change"])
        #     if x["properties"]["change"] is not None
        #     else "transparent",
        #     "color": "black",
        #     "fillOpacity": 0.4,
        # },
        tooltip=state_tooltip,
        # popup=state_popup,
    ).add_to(m)

    country_popup = folium.GeoJsonPopup(
        fields=["name",],
        aliases=["Country: ",],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    country_tooltip = folium.GeoJsonTooltip(
        fields=["name"],
        aliases=["Country: "],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    folium.GeoJson(
        countries_geo,
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "transparent",
        },
        tooltip=country_tooltip,
        # popup=country_popup,
    ).add_to(m)


    folium.LayerControl().add_to(m)
    st_folium(m, use_container_width=True, height=800)


if __name__ == "__main__":
    main()