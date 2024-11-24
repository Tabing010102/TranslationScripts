from llm_translate.GalTranslV2_6 import GalTranslV2_6
from llm_translate.SakuraV1 import SakuraV1


MODEL_NAMES_DICT = {
    "SakuraV1": SakuraV1,
    "GalTranslV2_6": GalTranslV2_6
}


def get_instance(model_name):
    if model_name in MODEL_NAMES_DICT:
        return MODEL_NAMES_DICT[model_name]
    else:
        raise ValueError(f"Unknown model name: {model_name}")
