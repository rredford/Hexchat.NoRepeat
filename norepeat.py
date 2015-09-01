# By Rolf Redford Aug 10 2015
# 
# Modified from https://github.com/hexchat/hexchat-addons/tree/master/python/smart_filter
# Thanks for awesome script, gave me ideas!

__module_name__ = 'NoRepeat'
__module_version__ = '1.0'
__module_description__ = 'Removes repeative join/part messages'

import hexchat
from time import time

last_seen = {}      # For each entry: the key is the user's nickname, the entry
                    # is a list: element 0: last seen time
                    #            element 1: how many times join/leave
                    #            element 2: how many times join/leave special case

user_timeout = 1200  # How long before join/leave timer resets (20 min)

user_toomany = 1     # how many leave/join before start eating join/leave

user_sptoomany = -1  # Special case for those who very rarely talk and disconnect
                     # but overall spam channel with disc/c. -1 means disabled.
                     # MUST be above user_toomany to work properly.

def new_msg(word, word_eol, event, attrs):
    user = hexchat.strip(word[0]) + "@" +  hexchat.get_info("network")
    # person spoke! reset join/leave count.
    last_seen[user]= [time(), 0, 0] # this is only way to reset "special case".
    return hexchat.EAT_NONE


def filter_msg(word, word_eol, event, attrs):
    """Filters join and part messages"""
    user = hexchat.strip(word[0]) + "@" +  hexchat.get_info("network")
    # If the user just joined, add
    if event != "Change Nick":
        if user not in last_seen:
            last_seen[user] = [time(), 0, 0]
            return hexchat.EAT_NONE
        elif last_seen[user][0] + user_timeout < time():
            # it has aged off so reset
            last_seen[user] = [time(), 0, last_seen[user][2]] # do not reset special case, it has no expire)
            # now, is special case enabled? if so, check if above special case number.
            if user_sptoomany > -1:
              if last_seen[user][2] >= user_sptoomany:
		last_seen[user] = [time(), last_seen[user][1] + 1, last_seen[user][2] + 1]
		#print("now blocked special case: ", user)
                return hexchat.EAT_ALL

    # If the user changed his nick, check if we've been tracking before
    # and transfer the stats if so. Otherwise, add to the dict.
    if event == "Change Nick":
        user = hexchat.strip(word[1]) + "@" +  hexchat.get_info("network")
        old = hexchat.strip(word[0]) + "@" +  hexchat.get_info("network")
        if old in last_seen:
            # first, check age
            if last_seen[old][0] + user_timeout < time():
                # it has aged off so reset
                last_seen[user] = [time(), 0, last_seen[old][2]] # dont reset special case
	    else:
	        # reset time but not how many times nor special case
	        last_seen[user] = [time(), last_seen[old][1], last_seen[old][2]]
	    # bye old
            del last_seen[old]
            return hexchat.EAT_NONE
        else:
            last_seen[user] = [time(), 0, 0]
            return hexchat.EAT_NONE

    # Not many yet, count and set time again
    if last_seen[user][1] <= user_toomany:
        last_seen[user][0] = time()
        last_seen[user][1] += 1
        last_seen[user][2] += 1
        return hexchat.EAT_NONE
    # too many times join/leave? no spam! (also count and set time again)
    elif last_seen[user][1] > user_toomany:
        last_seen[user][0] = time()
        last_seen[user][1] += 1
        last_seen[user][2] += 1
        #print("now blocked 20 min for join/leave: ", user)
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
print(__module_name__, "successfully loaded.\003")
