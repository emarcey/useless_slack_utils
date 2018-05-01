import logging

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def load_homophones(init_homophones=None):
    """
    Takes a list of homophones and duplicates it to ensure every key is a value and vice versa
    i.e. makes sure that if "your": "you're" is in the list, then "you're": "your" is as well

    :param init_homophones: (dict) initial list of homophones to duplicate. If None, default list is provided
    :return homophones: (dict) homophones (key) with their alternate (value)
    """
    if not init_homophones:
        init_homophones = {
            "your": "you're",
            "air": "heir",
            "aisle": "isle",
            "ante-": "anti-",
            "eye": "I",
            "bare": "bear",
            "be": "bee",
            "brake": "break",
            "buy": "by",
            "cell": "sell",
            "cent": "scent",
            "cereal": "serial",
            "coarse": "course",
            "complement": "compliment",
            "dam": "damn",
            "dear": "deer",
            "die": "dye",
            "fair": "fare",
            "fir": "fur",
            "flour": "flower",
            "for": "four",
            "hair": "hare",
            "heal": "heel",
            "hear": "here",
            "him": "hymn",
            "hole": "whole",
            "hour": "our",
            "idle": "idol",
            "in": "inn",
            "knight": "night",
            "knot": "not",
            "know": "no",
            "made": "maid",
            "mail": "male",
            "meat": "meet",
            "morning": "mourning",
            "none": "nun",
            "oar": "or",
            "one": "won",
            "pair": "pear",
            "peace": "piece",
            "plain": "plane",
            "poor": "pour",
            "pray": "prey",
            "principal": "principle",
            "profit": "prophet",
            "real": "reel",
            "right": "write",
            "root": "route",
            "sail": "sale",
            "sea": "see",
            "seam": "seem",
            "sight": "site",
            "sew": "so",
            "shore": "sure",
            "sole": "soul",
            "some": "sum",
            "son": "sun",
            "stair": "stare",
            "stationary": "stationery",
            "steal": "steel",
            "suite": "sweet",
            "tail": "tale",
            "their": "there",
            "theyre": "there",
            "there": "they're",
            "to": "too",
            "toe": "tow",
            "waist": "waste",
            "wait": "weight",
            "way": "weigh",
            "weak": "week",
            "wear": "where",
            "hay": "hey"
        }
    homophones = {}
    for ih in init_homophones:
        try:
            homophones[ih] = init_homophones[ih]
        except KeyError:
            logger.debug("Homophone already exists for {i}".format(i=ih))
        try:
            homophones[init_homophones[ih]] = ih
        except KeyError:
            logger.debug("Homophone already exists for {i}".format(i=ih))
    return homophones

