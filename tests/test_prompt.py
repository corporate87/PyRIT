# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
from pyrit.prompt_converter import Base64Converter, StringJoinConverter
from pyrit.prompt_normalizer.prompt_class import Prompt, PromptTarget, PromptConverter

class MockPromptTarget(PromptTarget):
    def __init__(self, id = None) -> None:
        self.id = id

    def set_system_prompt(self, prompt: str, conversation_id: str, normalizer_id: str) -> None:
        pass

    def send_prompt(self, normalized_prompt: str, conversation_id: str, normalizer_id: str) -> None:
        self.prompt_sent = normalized_prompt
        pass

class MockPromptConverter(PromptConverter):

    def __init__(self) -> None:
        pass

    def convert(self, prompt: str) -> str:
        return prompt

def test_prompt_init_valid_arguments():
    prompt_target = MockPromptTarget()
    prompt_converters = [MockPromptConverter()]
    prompt_text = "Hello"
    conversation_id = "123"

    prompt = Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

    assert prompt.prompt_target == prompt_target
    assert prompt.prompt_converter == prompt_converters
    assert prompt.prompt_text == prompt_text
    assert prompt.conversation_id == conversation_id

def test_prompt_init_invalid_prompt_target():
    prompt_target = "InvalidPromptTarget"
    prompt_converters = [MockPromptConverter()]
    prompt_text = "Hello"
    conversation_id = "123"

    with pytest.raises(ValueError):
        Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

def test_prompt_init_invalid_prompt_converters():
    prompt_target = MockPromptTarget()
    prompt_converters = ["InvalidPromptConverter"]
    prompt_text = "Hello"
    conversation_id = "123"

    with pytest.raises(ValueError):
        Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

def test_prompt_init_empty_prompt_converters():
    prompt_target = MockPromptTarget()
    prompt_converters = []
    prompt_text = "Hello"
    conversation_id = "123"

    with pytest.raises(ValueError):
        Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

def test_prompt_init_invalid_prompt_text():
    prompt_target = MockPromptTarget()
    prompt_converters = [MockPromptConverter()]
    prompt_text = 123
    conversation_id = "123"

    with pytest.raises(ValueError):
        Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

def test_prompt_init_invalid_conversation_id():
    prompt_target = MockPromptTarget()
    prompt_converters = [MockPromptConverter()]
    prompt_text = "Hello"
    conversation_id = 123

    with pytest.raises(ValueError):
        Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

def test_prompt_send_prompt():
    prompt_target = MockPromptTarget()
    prompt_converters = [Base64Converter(), StringJoinConverter("_")]
    prompt_text = "Hello"
    conversation_id = "123"

    prompt = Prompt(prompt_target, prompt_converters, prompt_text, conversation_id)

    normalizer_id = "456"
    prompt.send_prompt(normalizer_id)

    assert prompt_target.prompt_sent == 'S_G_V_s_b_G_8_='