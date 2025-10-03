from models import TechnicalOutputGuardRailOutput, UserAccountContext
from agents import (
    Agent,
    Runner,
    RunContextWrapper,
    output_guardrail,
    GuardrailFunctionOutput,
)

technical_output_guardrail_agent = Agent(
    name="technical output guardrail agent",
    instructions="""
    Analyze the technical support response to check if it inappropriately contains:
    
    - Billing information (payments, refunds, charges, subscriptions)
    - Order information (shipping, tracking, delivery, returns)
    - Account management info (passwords, email changes, account settings)
    
    Technical agents should ONLY provide technical troubleshooting, diagnostics, and product support.
    Return true for any field that contains inappropriate content for a technical support response.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def technical_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    output: str,
    agent: Agent[UserAccountContext],
):
    result = await Runner.run(
        technical_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = validation(
        validation.contains_off_topic,
        validation.contains_billing_data,
        validation.contains_account_data,
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered
    )
