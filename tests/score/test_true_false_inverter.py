# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
import pytest

from typing import Generator
from unittest.mock import MagicMock


from pyrit.memory.memory_interface import MemoryInterface
from pyrit.models.prompt_request_piece import PromptRequestPiece


from pyrit.score import SubStringScorer, TrueFalseInverterScorer
from tests.mocks import get_image_request_piece, get_memory_interface


@pytest.fixture
def image_request_piece() -> PromptRequestPiece:
    return get_image_request_piece()


@pytest.fixture
def memory() -> Generator[MemoryInterface, None, None]:
    yield from get_memory_interface()


@pytest.mark.asyncio
async def test_inverter_scorer_validate(image_request_piece: PromptRequestPiece):
    sub_scorer = SubStringScorer(substring="test", category="new_category")
    scorer = TrueFalseInverterScorer(memory=memory, scorer=sub_scorer, threshold=0.5)

    with pytest.raises(ValueError, match="Expected text data type"):
        await scorer.score_async(image_request_piece)

    os.remove(image_request_piece.converted_value)



@pytest.mark.asyncio
@pytest.mark.parametrize("sub_string", ["I can't answer", "Not present"])
async def test_substring_scorer_score(sub_string: str, memory: MemoryInterface):
    full_text = "blah I can't answer that too"

    sub_scorer = SubStringScorer(substring=sub_string, category="new_category", memory=memory)
    scorer = TrueFalseInverterScorer(memory=memory, scorer=sub_scorer, threshold=0.5)

    score = await scorer.score_text_async(full_text)

    assert len(score) == 1

    # score_value should be the opposite of substring scorer since results are inverted
    assert score[0].score_value != str(sub_string in full_text)
    assert score[0].score_type == "true_false"
    assert score[0].score_category == "new_category"
    assert score[0].prompt_request_response_id is None


@pytest.mark.asyncio
async def test_substring_scorer_adds_to_memory():
    memory = MagicMock(MemoryInterface)

    scorer = SubStringScorer(substring="string", category="new_category", memory=memory)
    await scorer.score_text_async(text="string")

    memory.add_scores_to_memory.assert_called_once()
