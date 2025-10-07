from openai import OpenAI
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import base64

client = OpenAI()


async def generate_images(tool_context: ToolContext):
    prompt_builder_output = tool_context.state.get("prompt_builder_output")
    optimized_prompts = prompt_builder_output.get("optimized_prompts")

    existing_artifacts = tool_context.list_artifacts()

    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")
        file_name = f"scene_{scene_id}_image.jpeg"

        if file_name in existing_artifacts:
            generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": enhanced_prompt,
                    "filename": file_name,
                }
            )
            continue

        image = client.images.generate(
            prompt=enhanced_prompt,
            model="gpt-image-1",
            quality="medium",
            n=1,
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1536",
        )

        image_bytes = base64.b64decode(image.data[0].b64_json)

        artifact = types.Part(
            inline_data=types.Blob(
                mine_type="image/jpeg",
                data=image_bytes,
            )
        )

        await tool_context.save_artifact(
            filename=file_name,
            artifact=artifact,
        )

        generated_images.append(
            {
                "scene_id": scene_id,
                "prompt": enhanced_prompt,
                "filename": file_name,
            },
        )

    return {
        "total_images": len(generate_images),
        "generated_images": generated_images,
        "status": "complete",
    }
