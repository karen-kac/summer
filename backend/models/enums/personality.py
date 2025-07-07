from enum import Enum


class Personality(str, Enum):
    curious = "curious"
    patient = "patient"
    creative = "creative"
    active = "active"
    careful = "careful"
    social = "social"
    independent = "independent"
    persistent = "persistent"
    analytical = "analytical"

    _LABELS = {
        "curious": "好奇心旺盛",
        "patient": "根気強い",
        "creative": "創造的",
        "active": "活動的",
        "careful": "丁寧・慎重",
        "social": "協調性がある",
        "analytical": "分析的・論理的",
        "independent": "自立している",
    }

    @property
    def label(self) -> str:
        return self._LABELS[self.value]
