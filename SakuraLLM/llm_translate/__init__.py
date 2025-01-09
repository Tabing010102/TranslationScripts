from enum import Enum

from .AiNiee import AiNiee
from .GalTranslV2_6 import GalTranslV2_6
from .SakuraV1 import SakuraV1


class Lang(Enum):
    ZH = 0
    ZHT = 1
    JA = 2
    EN = 3
    KO = 4
    RU = 5


MODEL_NAMES_DICT = {
    "SakuraV1": SakuraV1,
    "GalTranslV2_6": GalTranslV2_6,
    "AiNiee": AiNiee
}


def get_instance(model_name):
    if model_name in MODEL_NAMES_DICT:
        return MODEL_NAMES_DICT[model_name]
    else:
        raise ValueError(f"Unknown model name: {model_name}")
