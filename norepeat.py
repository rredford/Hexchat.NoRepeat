__module_name__ = 'NoRepeat'
__module_version__ = '1.0'
__module_description__ = 'Removes repeative join/part messages'

import hexchat
from time import time

last_seen = {}      # For each entry: the key is the user's nickname, the entry
                    # is a list: element 0: last seen time
                    #            element 1: how many times join/leave

user_timeout = 1200  # How long before join/leave timer resets (20 min)
user_toomany = 2    # (how many leave/join before shut up)

halt = False

def new_msg(word, word_eol, event, attrs):
    user = hexchat.strip(word[0])
    # If the user logged in before we did (which means the Join part of
    # filter_msg didn't take effect), add him to the dict.
    if user not in last_seen:
        last_seen[user]= [time(), 1]
        return hexchat.EAT_NONE
    # person spoke! reset join/leave count.
    last_seen[user]= [time(), 1]
    return hexchat.EAT_NONE
    


def filter_msg(word, word_eol, event, attrs):
    """Filters join and part messages"""
    user = hexchat.strip(word[0])
    # If the user just joined, add
    if user not in last_seen and event != "Change Nick":
        last_seen[user] = [time(), 1]
        return hexchat.EAT_NONE

    # If the user changed his nick, check if we've been tracking him before
    # and transfer his stats if so. Otherwise, add him to the dict.
    if event == "Change Nick":
        user = hexchat.strip(word[1])
        old = hexchat.strip(word[0])
        if old in last_seen:
            # reset time but not how many times.
            last_seen[user] = [time(), last_seen[old][1]]
            del last_seen[old]
            return hexchat.EAT_NONE
        else:
            last_seen[user] = [time(), 1]
            return hexchat.EAT_NONE

    # Not many yet, count and set time again
    if last_seen[user][1] <= user_toomany:
        last_seen[user][0] = time()
        last_seen[user][1] += 1
        return hexchat.EAT_NONE
    # too many times join/leave? no spam! (also count and set time again)
    elif last_seen[user][1] > user_toomany:
        last_seen[user][0] = time()
        last_seen[user][1] += 1
        print("now blocked 20 min for join/leave: ", user)
        return hexchat.EAT_ALL

hooks_new = ["Your Message", "Channel Message", "Channel Msg Hilight",
             "Your Action", "Channel Action", "Channel Action Hilight"]
hooks_filter = ["Join", "Change Nick", "Part", "Part with Reason", "Quit"]
# hook_print_attrs is used for compatibility with my other scripts,
# since priorities are hook specific
for hook in hooks_new:
    hexchat.hook_print_attrs(hook, new_msg, hook, hexchat.PRI_HIGH)
for hook in hooks_filter:
    hexchat.hook_print_attrs(hook, filter_msg, hook, hexchat.PRI_HIGH)
print("\00304", __module_name__, "successfully loaded.\003")
