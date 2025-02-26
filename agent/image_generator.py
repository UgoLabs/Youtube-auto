import torch
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import \
    StableDiffusionPipeline


def generate_image(prompt: str):
    """
    Generates an image using the FLUX.1-dev model from Hugging Face on CPU.
    """
    model_id = "black-forest-labs/FLUX.1-dev"
    device = "cpu"  # Change to "cuda" if a GPU is available
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=torch.float32
    )
    pipe.to(device)
    image = pipe.__call__(prompt, guidance_scale=7.5).images[0]
    # Save the image locally
    from pathlib import Path
    IMAGE_DIR = Path(__file__).resolve().parent.parent / "output/images"
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    image_file = IMAGE_DIR / "temp_image.png"
    image.save(str(image_file))
    return str(image_file)