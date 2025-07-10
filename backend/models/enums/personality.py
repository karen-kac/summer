from enum import Enum


PERSONALITY_LABELS = {
    "curious": "好奇心旺盛",
    "patient": "根気強い",
    "creative": "創造的",
    "active": "活動的",
    "careful": "丁寧・慎重",
    "social": "協調性がある",
    "analytical": "分析的・論理的",
    "independent": "自立している",
}


class Personality(str, Enum):
    curious = "curious"
    patient = "patient"
    creative = "creative"
    active = "active"
    careful = "careful"
    social = "social"
    independent = "independent"
    analytical = "analytical"

    @property
    def label(self) -> str:
        return PERSONALITY_LABELS[self.value]
