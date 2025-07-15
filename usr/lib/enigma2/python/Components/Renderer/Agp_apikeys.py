#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
"""
#########################################################
#                                                       #
#  AGP - Advanced Graphics Renderer                     #
#  Version: 3.5.0                                       #
#  Created by Lululla (https://github.com/Belfagor2005) #
#  License: CC BY-NC-SA 4.0                             #
#  https://creativecommons.org/licenses/by-nc-sa/4.0    #
#                                                       #
#  Last Modified: "18:14 - 20250512"                    #
#                                                       #
#  Credits:                                             #
#  - Original concept by Lululla                        #
#  - Poster renderer                                    #
#  - Backdrop renderer                                  #
#  - Poster EMC renderer                                #
#  - InfoEvents renderer                                #
#  - Star rating renderer                               #
#  - Parental control renderer                          #
#  - Genre detection and renderer                       #
#                                                       #
#  - Advanced download management system                #
#  - Atomic file operations                             #
#  - Thread-safe resource locking                       #
#  - TMDB API integration                               #
#  - TVDB API integration                               #
#  - OMDB API integration                               #
#  - FANART API integration                             #
#  - IMDB API integration                               #
#  - ELCINEMA API integration                           #
#  - GOOGLE API integration                             #
#  - PROGRAMMETV integration                            #
#  - MOLOTOV API integration                            #
#  - Advanced caching system                            #
#  - Fully configurable via AGP Setup Plugin            #
#                                                       #
#  Usage of this code without proper attribution        #
#  is strictly prohibited.                              #
#  For modifications and redistribution,                #
#  please maintain this credit header.                  #
#########################################################
"""
__author__ = "Lululla"
__copyright__ = "AGP Team"

# Standard library imports
from Components.config import config
from pathlib import Path
from threading import Lock

# Initialize thread lock for API access synchronization
api_lock = Lock()

# ================ START SERVICE API CONFIGURATION ===============

# Default API keys (fallback values)
API_KEYS = {
    "tmdb_api": "3c3efcf47c3577558812bb9d64019d65",
    "omdb_api": "4ca6ea60",
    "thetvdb_api": "a99d487bb3426e5f3a60dea6d3d3c7ef",
    "fanart_api": "6d231536dea4318a88cb2520ce89473b",
}


def setup_api_keys():
    """
    Configures API keys using the following priority:
    1. Plugin Configuration (if enabled and key provided)
    2. Skin Directory Key Files
    3. Hardcoded Defaults

    To configure via plugin:
    - Enable the API in plugin settings
    - Enter the key in the corresponding field

    To configure via skin files:
    - Create files named tmdbkey, omdbkey, etc. in the skin directory
    - Each file should contain only the API key
    """
    pass


def _load_api_keys():
    """
    Internal function that loads API keys from plugin config, skin files, or defaults.
    Also saves the keys to the plugin configuration.
    """
    try:
        cur_skin = config.skin.primary_skin.value.replace("/skin.xml", "")
        skin_path = Path(f"/usr/share/enigma2/{cur_skin}")

        if not skin_path.exists():
            print(f"[API Config] Skin path not found: {skin_path}")
            return False

        # Map API key names to skin file paths
        key_files = {
            "tmdb_api": skin_path / "tmdb_api",
            "omdb_api": skin_path / "omdb_api",
            "thetvdb_api": skin_path / "thetvdb_api",
            "fanart_api": skin_path / "fanart_api"
        }

        # Plugin configuration reference
        plugin_cfg = config.plugins.Aglare

        # API enablement and keys from plugin config
        plugin_keys = {
            "tmdb_api": (plugin_cfg.tmdb.value, plugin_cfg.tmdb_api.value),
            "omdb_api": (plugin_cfg.omdb.value, plugin_cfg.omdb_api.value),
            "thetvdb_api": (plugin_cfg.thetvdb.value, plugin_cfg.thetvdb_api.value),
            "fanart_api": (plugin_cfg.fanart.value, plugin_cfg.fanart_api.value),
        }

        keys_loaded = False
        with api_lock:
            for key_name in key_files:
                # Check if enabled in plugin and key is set
                enabled, key_value = plugin_keys.get(key_name, (False, ""))
                if enabled and key_value.strip():
                    API_KEYS[key_name] = key_value.strip()
                    print(f"[API Config] Using plugin key for {key_name}")
                    keys_loaded = True
                    continue
                else:
                    print(f"[API Config] Plugin key for {key_name} not available or disabled, checking fallback...")

                # Fallback to skin file
                file_path = key_files[key_name]
                if file_path.exists():
                    try:
                        with open(file_path, "r") as f:
                            key_value = f.read().strip()
                            API_KEYS[key_name] = key_value
                        print(f"[API Config] Loaded {key_name} from {file_path}")
                        keys_loaded = True

                        # Save the key to the plugin config if successfully loaded from file
                        if key_name == "tmdb_api":
                            plugin_cfg.tmdb_api.value = key_value
                        elif key_name == "omdb_api":
                            plugin_cfg.omdb_api.value = key_value
                        elif key_name == "thetvdb_api":
                            plugin_cfg.thetvdb_api.value = key_value
                        elif key_name == "fanart_api":
                            plugin_cfg.fanart_api.value = key_value

                        # Commit changes to the plugin configuration
                        plugin_cfg.save()
                    except Exception as e:
                        print(f"[API Config] Error reading {file_path}: {str(e)}")
                else:
                    print(f"[API Config] Using default key for {key_name} (file not found)")

        # Update global namespace with current API keys
        globals().update(API_KEYS)
        return keys_loaded

    except Exception as e:
        print(f"[API Config] Critical error loading keys: {str(e)}")
        return False


# Initialize API keys during module import
if not _load_api_keys():
    print("[API Config] Using default API keys")

# ================ END SERVICE API CONFIGURATION ================
