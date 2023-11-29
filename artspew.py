import random
import os
import argparse
import torch
import logging
from src.stable_diffusion_sd15 import StableDiffusionSD15
from src.stable_diffusion_sdxl import StableDiffusionSDXL
from pathvalidate import sanitize_filename

MODEL_ID_SD15 = 'runwayml/stable-diffusion-v1-5'
MODEL_ID_SDXL = 'stabilityai/stable-diffusion-xl-base-1.0'
DEFAULT_WIDTH_SD15 = 512
DEFAULT_HEIGHT_SD15 = 512
DEFAULT_WIDTH_SDXL = 1024
DEFAULT_HEIGHT_SDXL = 1024
DEFAULT_LCM_STEPS = 8
DEFAULT_INFER_STEPS = 20
DEFAULT_GUIDANCE_SD = 8.
DEFAULT_GUIDANCE_LCM = 0.


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--xl', action=argparse.BooleanOptionalAction,
                        help='Use SDXL')
    parser.add_argument('-m', '--model-id', type=str, default='auto',
                        help='Specify the input file')
    parser.add_argument('-p', '--prompt', type=str,
                        help='Specify the start of the prompt')
    parser.add_argument('--width', type=int, default=-1,
                        help='Image width, -1 for auto')
    parser.add_argument('--height', type=int, default=-1,
                        help='Image height, -1 for auto')
    parser.add_argument('-c', '--batch-count', type=int, default=1,
                        help='Number of batches to do')
    parser.add_argument('-b', '--batch-size', type=int, default=1,
                        help='Batch Size')
    parser.add_argument('-s', '--steps', type=int, default=-1,
                        help='Number of inference steps, -1 for auto')
    parser.add_argument('-n', '--random-tokens', type=int, default=5,
                        help='Number of random tokens added')
    parser.add_argument('-l', '--lcm', action='store_true',
                        help='Use LCM')
    parser.add_argument('-t', '--tiny-vae', action='store_true',
                        help='Use the tiny VAE')
    parser.add_argument('-g', '--guidance', type=float, default=-1,
                        help='Guidance value, -1 for auto')
    parser.add_argument('-z', '--torch-compile', action='store_true',
                        help='Using torch.compile for faster inference')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show debug info')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Only show errors')        
    
    args = parser.parse_args()

    if args.model_id == 'auto':
        args.model_id = MODEL_ID_SDXL if args.xl else MODEL_ID_SD15
    args.width = DEFAULT_WIDTH_SDXL if args.xl else DEFAULT_WIDTH_SD15
    args.height = DEFAULT_HEIGHT_SDXL if args.xl else DEFAULT_HEIGHT_SD15
    args.steps = DEFAULT_LCM_STEPS if args.lcm else DEFAULT_INFER_STEPS
    args.guidance = DEFAULT_GUIDANCE_LCM if args.lcm else DEFAULT_GUIDANCE_SD

    return args


def main():
    args = parse_arguments()

    if not os.path.exists('spew'):
        os.makedirs('spew')

    # Setup Logger.
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ArtSpew")

    logger.info(
        f"Generating {args.batch_count*args.batch_size} images with {args.steps} steps. "
        "It can take a few minutes to download the model the very first run. "
        "After that it can take 10s of seconds to load the stable diffusion model. "
    )

    seed = random.randint(0, 2147483647)
    torch.manual_seed(seed)

    if args.xl:
        model = StableDiffusionSDXL(args.model_id, args.tiny_vae, args.lcm, args.width, args.height, seed, args.batch_count, args.batch_size, args.random_tokens, args.steps, args.guidance, args.torch_compile)
    else:
        model = StableDiffusionSD15(args.model_id, args.tiny_vae, args.lcm, args.width, args.height, seed, args.batch_count, args.batch_size, args.random_tokens, args.steps, args.guidance, args.torch_compile)

    sequence_number = -1
    if not os.path.exists('spew'):
        os.makedirs('spew')

    files = [entry.name for entry in os.scandir('spew') if entry.name.startswith(model.get_filename_prefix())]

    if files:
        sorted_files = sorted(files, key=lambda x: int(x.split('-')[1]))
        sequence_number = int(sorted_files[-1].split('-')[1])

    images = model.generate_images(args.prompt)
    for idx, image in enumerate(images):
        sequence_number += 1
        safe_prompt = sanitize_filename(image.prompt_text)
        image.save(f"spew/{model.get_filename_prefix()}{sequence_number:09d}-{idx:02d}-{safe_prompt}.jpg")


if __name__ == "__main__":
    main()
