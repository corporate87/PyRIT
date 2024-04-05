# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging

import pathlib
from typing import Optional
from uuid import uuid4

from pyrit.common.path import DATASETS_PATH
from pyrit.memory import MemoryInterface
from pyrit.models import PromptTemplate
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.prompt_normalizer import Prompt, PromptNormalizer
from pyrit.prompt_target import PromptTarget
from pyrit.prompt_converter import PromptConverter, NoOpConverter
from pyrit.prompt_target.prompt_chat_target.prompt_chat_target import PromptChatTarget

logger = logging.getLogger(__name__)


class PromptVariationOrchestrator(PromptSendingOrchestrator):
    """
    This orchestrator takes a set of prompts, expands them using infra,
    converts them using the list of PromptConverters, and sends them to a target.
    """

    def __init__(
        self,
        prompt_target: PromptTarget,
        prompt_variation_target: PromptChatTarget,
        number_variations: int,
        variation_strategy: PromptTemplate = None,
        prompt_converters: Optional[list[PromptConverter]] = None,
        memory: MemoryInterface = None,
        batch_size: int = 10,
        include_original_prompts: bool = False,
        verbose: bool = False,
    ) -> None:
        super().__init__(
            prompt_target=prompt_target,
            prompt_converters=prompt_converters,
            memory=memory,
            batch_size=batch_size,
            verbose=verbose)
        
        # set to default strategy if not provided
        prompt_template = (
            variation_strategy
            if variation_strategy
            else PromptTemplate.from_yaml_file(
                pathlib.Path(DATASETS_PATH) / "orchestrators" / "prompt_sending" / "variations.yaml"
            )
        )

        self._number_variations = number_variations
        self._prompt_variation_target = prompt_variation_target

        self.system_prompt = str(
            prompt_template.apply_custom_metaprompt_parameters(number_iterations=str(self.number_variations))
        )

        self._prompt_variation_target.set_system_prompt(
            prompt=self.system_prompt,
            conversation_id=str(uuid4.uuid()),
            normalizer_id=str(uuid4.uuid()),
        )

    async def send_prompt_variations_batch_async(self, prompt_strings: list[str]):
        """
        For each prompt that's passed, get number_variations variations and send them
        """

        normalized_prompts = self._get_normalized_prompts(prompt_strings)

        await self._prompt_normalizer.send_prompt_batch_async(normalized_prompts, batch_size=self.batch_size)