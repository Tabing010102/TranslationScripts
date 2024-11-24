from llm_translate.GalTranslV2_6 import GalTranslV2_6
from llm_translate.SakuraV1 import SakuraV1


def get_instance(model_name):
    if model_name == "SakuraV1":
        return SakuraV1
    elif model_name == "GalTranslV2_6":
        return GalTranslV2_6
    else:
        raise ValueError(f"Unknown model name: {model_name}")
