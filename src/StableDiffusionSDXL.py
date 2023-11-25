from src.StableDiffusionBase import StableDiffusionBase
from diffusers import StableDiffusionXLPipeline, AutoPipelineForText2Image
import torch


class StableDiffusionSDXL(StableDiffusionBase):
    def load_pipeline(self):
        if self.model_id.endswith('.safetensors') or self.model_id.endswith('.ckpt'):
            pipe = StableDiffusionXLPipeline.from_single_file(
                self.model_id,
                torch_dtype = torch.float16,
                variant = "fp16",
                safety_checker = None,
                requires_safety_checker = False)
        else:
            pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_id,
                torch_dtype = torch.float16,
                variant = "fp16",
                safety_checker = None,
                requires_safety_checker = False)
        return pipe

    def get_tiny_vae_model_id(self):
        return 'madebyollin/taesdxl'

    def get_lcm_adapter_id(self):
        return 'latent-consistency/lcm-lora-sdxl'

    def get_filename_prefix(self):
        return "sdxl-"

    def get_tokenizers(self):
        return [self.pipe.tokenizer, self.pipe.tokenizer_2]
    
    def get_text_encoders(self):
        return [self.pipe.text_encoder, self.pipe.text_encoder_2]