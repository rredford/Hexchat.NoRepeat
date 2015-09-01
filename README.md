# Hexchat.NoRepeat

Just eats joins and leave messages if user repeativly join or leave within 20 minutes.

You can adjust timeout and how many before eating by changing two parameters near top - user_timeout = 1200 (in seconds) and user_toomany (how many times repeat before eat messages)

Script can also be enabled to block too many joins and leaves, reardless of time as long as person had not spoken meanwhile. To enable it, set user_sptoomany to a value higher than user_toomany. 10 or 20 is good value.

# Install

To install, move norepeat.py to your path_to_HexChat_config/addons directory.

# Requirement

XChat Python scripting interface plugin.
