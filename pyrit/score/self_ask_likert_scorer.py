# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import uuid
import yaml

from dataclasses import dataclass
import enum
from pathlib import Path
from typing import Dict, Union

from pyrit.score import Score, Scorer
from pyrit.models import PromptRequestPiece, PromptRequestResponse, PromptTemplate
from pyrit.prompt_target import PromptChatTarget
from pyrit.common.path import CONTENT_CLASSIFIERS_PATH, LIKERT_SCALES_PATH, SCORING_INSTRUCTIONS_PATH
from pyrit.score.scorer import FloatScaleScorer


@dataclass
class LIKERT_SCALE_DESCIPTIONS:
    name: str
    description: str



class ContentClassifiers(enum.Enum):
    BIAS_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "bias.yaml").resolve()
    CURRENT_EVENTS_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "current_events.yaml").resolve()
    GROUNDEDNESS_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "grounded.yaml").resolve()
    HARMFUL_CONTENT_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "harmful_content.yaml").resolve()
    PROMPT_INJECTION_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "prompt_injection_detector.yaml").resolve()
    QUESTION_ANSWERING_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "question_answering.yaml").resolve()
    REFUSAL_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "refusal.yaml").resolve()
    SENTIMENT_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "sentiment.yaml").resolve()
    SEXUAL_CONTENT_CLASSIFIER = Path(CONTENT_CLASSIFIERS_PATH, "sexual_content.yaml").resolve()


class LikertScales(enum.Enum):
    CYBER_SCALE = Path(LIKERT_SCALES_PATH, "cyber.yaml").resolve()
    FAIRNESS_BIAS_SCALE = Path(LIKERT_SCALES_PATH, "fairness_bias.yaml").resolve()
    HARM_SCALE = Path(LIKERT_SCALES_PATH, "harm.yaml").resolve()
    HATE_SPEECH_SCALE = Path(LIKERT_SCALES_PATH, "hate_speech.yaml").resolve()
    PERSUASION_SCALE = Path(LIKERT_SCALES_PATH, "persuasion.yaml").resolve()
    PHISH_EMAILS_SCALE = Path(LIKERT_SCALES_PATH, "phish_emails.yaml").resolve()
    POLITICAL_MISINFO_SCALE = Path(LIKERT_SCALES_PATH, "political_misinfo.yaml").resolve()
    SEXUAL_SCALE = Path(LIKERT_SCALES_PATH, "sexual.yaml").resolve()
    VIOLENCE_SCALE = Path(LIKERT_SCALES_PATH, "violence.yaml").resolve()


class SelfAskLikertScorer(FloatScaleScorer):
    """A class that represents a self-ask score for text scoring for an individual category.

    This class is responsible for scoring text using a self-ask approach. It takes a chat target,
    a prompt template path, and classifier categories path as input.

    """

    def __init__(
        self,
        chat_target: PromptChatTarget,
        likert_scale_path: LikertScales,
    ) -> None:

        likert_scale = yaml.safe_load(likert_scale_path.read_text(encoding="utf-8"))

        if likert_scale["category"]:
            self._score_category = likert_scale["category"]
        else:
            raise ValueError(f"Impropoerly formated likert scale yaml file. Missing category in {likert_scale_path}.")

        likert_scale = self._likert_scale_description_to_string(likert_scale["scale_descriptions"])


        scoring_instructions_template = PromptTemplate.from_yaml_file(SCORING_INSTRUCTIONS_PATH / "likert_system_prompt.yaml")
        self._system_prompt = scoring_instructions_template.apply_custom_metaprompt_parameters(
                                likert_scale=likert_scale,
                                category=self._score_category)


        self._score_type = "float_scale"
        self._chat_target: PromptChatTarget = chat_target
        self._conversation_id = str(uuid.uuid4())

        self._chat_target.set_system_prompt(
            system_prompt=self._system_prompt,
            conversation_id=self._conversation_id,
            orchestrator_identifier=None,
        )

    def _likert_scale_description_to_string(self, descriptions: list[Dict[str, str]]) -> str:
        if not descriptions:
            raise ValueError("Impropoerly formated likert scale yaml file. No likert scale_descriptions provided")

        likert_scale_description = ""

        for description in descriptions:
            name = description["name"]
            desc = description["description"]

            if int(name) < 0 or int(name) > 5:
                raise ValueError("Impropoerly formated likert scale yaml file. Likert scale values must be between 1 and 5")

            likert_scale_description += f"'{name}': {desc}\n"

        return likert_scale_description


    async def score(self, request_response: PromptRequestPiece) -> list[Score]:
        """
        Scores the given text using the chat target.
        """
        self.validate(request_response)


        request = PromptRequestResponse(
            [
                PromptRequestPiece(
                    role="user",
                    original_value=request_response.converted_value,
                    conversation_id=self._conversation_id,
                    prompt_target_identifier=self._chat_target.get_identifier(),
                )
            ]
        )

        response_text = await self._chat_target.send_chat_prompt_async(prompt_request=request).request_pieces[0].converted_value

        try:
            parsed_response = json.loads(response_text)

            # score_likert_value = 

            score = Score(
                score_type=self._score_type,
                score_value=parsed_response["score_value"],
                score_description=parsed_response["category_description"],
                score_explanation=parsed_response["rationale"],
                raw_output_score_text=response_text,
            )
            return score

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from chat target: {response_text}") from e

    def validate(self, request_response: PromptRequestPiece):
        if request_response.converted_value_data_type != "text":
            raise ValueError("Expected text data type")


"""
class SelfAskGptClassifier(SelfAskScorer):
    def __init__(
        self,
        content_classifier: ContentClassifiers,
        chat_target: PromptChatTarget,
    ) -> None:

        super().__init__(
            scoring_instructions_path=ScoringInstructions.CLASSIFICATION_SYSTEM_PROMPT,
            content_classifier=content_classifier,
            chat_target=chat_target,
        )


class SelfAskGptLikertScale(SelfAskScorer):
    def __init__(
        self,
        content_classifier: LikertScales,
        chat_target: PromptChatTarget,
    ) -> None:

        super().__init__(
            scoring_instructions_path=ScoringInstructions.LIKERT_SYSTEM_PROMPT,
            content_classifier=content_classifier,
            chat_target=chat_target,
        )
"""