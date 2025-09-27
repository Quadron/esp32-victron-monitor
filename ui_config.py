# ui_config.py
# Central place to manage MQTT topics and screen/page definitions for the ESP32 Victron Monitor

# List of MQTT topics to subscribe to
MQTT_TOPICS = [
    {
        "topic": "N/0/Dc/Battery/Soc",
        "screen": "Battery",
        "label": "Battery SOC",
        "unit": "%",
        "color": "green"
    },
    {
        "topic": "N/0/Dc/Battery/TimeToGo",
        "screen": "Battery",
        "label": "Time to Go",
        "unit": "h",
        "color": "orange"
    },
    {
        "topic": "N/0/Solar/MPPT/0/Power",
        "screen": "Charging",
        "label": "MPPT Power",
        "unit": "W",
        "color": "accent"
    },
    {
        "topic": "N/0/Ac/Charger/0/Power",
        "screen": "Charging",
        "label": "MultiPlus",
        "unit": "W",
        "color": "accent"
    },
    {
        "topic": "N/0/Tank/0/Level",
        "screen": "Tank",
        "label": "Tank Level",
        "unit": "%",
        "color": "grey"
    }
]

# Screen/page order and their topics
SCREENS = [
    {
        "name": "Battery",
        "topics": [
            "N/0/Dc/Battery/Soc",
            "N/0/Dc/Battery/TimeToGo"
        ]
    },
    {
        "name": "Charging",
        "topics": [
            "N/0/Solar/MPPT/0/Power",
            "N/0/Ac/Charger/0/Power"
        ]
    },
    {
        "name": "Tank",
        "topics": [
            "N/0/Tank/0/Level"
        ]
    }
]
