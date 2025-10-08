from google.adk.tools import ToolContext
from google.genai import types
from openai import OpenAI
from typing import List, Dict

client = OpenAI()


async def generate_narrations(
    tool_context: ToolContext,
    voice: str,
    voice_instructions: List[Dict],
):

    generated_narrations = []

    existing_artifacts = await tool_context.list_artifacts()

    for instruction in voice_instructions:
        input = instruction.get("input")
        instruction = instruction.get("instruction")
        scene_id = instruction.get("scene_id")
        filename = f"scene_{scene_id}_narration.mp3"

        if filename in existing_artifacts:
            generated_narrations.append(
                {
                    "scene_id": scene_id,
                    "filename": filename,
                    "input": input,
                    "instructions": instruction[:50],
                }
            )

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts", voice=voice, input=input, instructions=instruction
        ) as response:

            audio_data = response.read()

        artifact = types.Part(
            inline_data=types.Blob(mime_type="audio/mpeg", data=audio_data)
        )

        await tool_context.save_artifact(filename=filename, artifact=artifact)

        generated_narrations.append(
            {
                "scene_id": scene_id,
                "filename": filename,
                "input": input,
                "instructions": instruction,
            }
        )

    return {
        "success": True,
        "narrations": generated_narrations,
        "total_narrations": len(generated_narrations),
    }
