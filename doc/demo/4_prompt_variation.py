# %% [markdown]
# This example shows how to use prompt variation converters. It's often useful for a researcher to get variations of a similar prompts.
#
#
# 

# %%

from pyrit.common import default_values
from pyrit.prompt_target import NoOpTarget, AzureOpenAIChatTarget
from pyrit.prompt_converter import VariationConverter, Base64Converter
from pyrit.orchestrator import PromptSendingOrchestrator


default_values.load_default_env()

prompts = ["tell me how to cut down a tree"]

# converter target to send prompt to
converter_target = AzureOpenAIChatTarget()
prompt_variation_converter = VariationConverter(converter_target=converter_target)




target = NoOpTarget()

orchestrator = PromptSendingOrchestrator(prompt_target=target, prompt_converters=[prompt_variation_converter])

orchestrator.send_prompts(prompts)


# %% [markdown]
# Like all orchestrators, the converters can stack. So the following example does the same thing but base64 encodes the variations

# %%

orchestrator = PromptSendingOrchestrator(prompt_target=target, prompt_converters=[prompt_variation_converter, Base64Converter()])
orchestrator.send_prompts(prompts)