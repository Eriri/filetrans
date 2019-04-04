from CD import *
import os


class MainModel(object):
    def __init__(self, Id, name, pwd, ctime, probs, proj_path):
        self.Id = Id
        self.name = name
        self.pwd = pwd
        self.ctime = ctime
        vprobs = []
        for prob in probs:
            v = "□"*len(prob)
            for suf in LANGUAGE_CONFIG:
                if os.path.isfile(os.path.join(proj_path, Id, prob+suf)):
                    v = prob
            vprobs.append(v)
        self.ws = "|".join(vprobs)
