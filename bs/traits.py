#
# MIT License
#
# Copyright (c) 2023 Thought Stream, LLC dba Bluescape.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from modules.processing import Processed

def get_image_traits(enable_metadata: bool, processed: Processed, seed, subseed, infotext, generation_type, upload_id, user_id):

    if enable_metadata:
        traits = {
            "http://bluescape.dev/automatic1111-extension/v1/enabled": True,
            "http://bluescape.dev/automatic1111-extension/v1/postprocess": str({
                "type": str(generation_type),
                "prompt": str(processed.prompt),
                "negative_prompt": str(processed.negative_prompt),
                "seed": str(seed),
                "subseed": str(subseed),
                "infotext": str(infotext),
                "subseed_strength": str(processed.subseed_strength),
                "width": str(processed.width),
                "height": str(processed.height),
                "sampler_name": str(processed.sampler_name),
                "cfg_scale": str(processed.cfg_scale),
                "image_cfg_scale": str(processed.image_cfg_scale),
                "restore_faces": str(processed.restore_faces),
                "face_restoration_model": str(processed.face_restoration_model),
                "sd_model_hash": str(processed.sd_model_hash),
                "seed_resize_from_w": str(processed.seed_resize_from_w),
                "seed_resize_from_h": str(processed.seed_resize_from_h),
                "denoising_strength": str(processed.denoising_strength),
                "extra_generation_params": str(processed.extra_generation_params),
                "clip_skip": str(processed.clip_skip), # missing in infobar
                "eta": str(processed.eta),
                "ddim_discretize": str(processed.ddim_discretize),
                "s_churn": str(processed.s_churn),
                "s_tmin": str(processed.s_tmin),
                "s_tmax": str(processed.s_tmax),
                "s_noise": str(processed.s_noise),
                "sampler_noise_scheduler_override": str(processed.sampler_noise_scheduler_override),
                "is_using_inpainting_conditioning": str(processed.is_using_inpainting_conditioning),
                "upload_id": str(upload_id),
            }),
            "http://bluescape.dev/automatic1111-extension/v1/uploadId": str(upload_id),
            "http://bluescape.dev/automatic1111-extension/v1/userId": str(user_id),
        }
    else:
        traits = {
            "http://bluescape.dev/automatic1111-extension/v1/enabled": False,
            "http://bluescape.dev/automatic1111-extension/v1/userId": str(user_id),
        }

    return traits

def get_canvas_traits(enable_metadata: bool, processed: Processed, generation_type, upload_id, num_images, user_id):

    if enable_metadata:
        traits = {
            "http://bluescape.dev/automatic1111-extension/v1/enabled": True,
            "http://bluescape.dev/automatic1111-extension/v1/processed": str({
                "type": str(generation_type),
                "prompt": str(processed.prompt),
                "negative_prompt": str(processed.negative_prompt),
                # No seed, subseed
                "subseed_strength": str(processed.subseed_strength),
                "width": str(processed.width),
                "height": str(processed.height),
                "sampler_name": str(processed.sampler_name),
                "cfg_scale": str(processed.cfg_scale),
                "image_cfg_scale": str(processed.image_cfg_scale),
                "restore_faces": str(processed.restore_faces),
                "face_restoration_model": str(processed.face_restoration_model),
                "sd_model_hash": str(processed.sd_model_hash),
                "seed_resize_from_w": str(processed.seed_resize_from_w),
                "seed_resize_from_h": str(processed.seed_resize_from_h),
                "denoising_strength": str(processed.denoising_strength),
                "extra_generation_params": str(processed.extra_generation_params),
                "clip_skip": str(processed.clip_skip), # missing in infobar
                "eta": str(processed.eta),
                "ddim_discretize": str(processed.ddim_discretize),
                "s_churn": str(processed.s_churn),
                "s_tmin": str(processed.s_tmin),
                "s_tmax": str(processed.s_tmax),
                "s_noise": str(processed.s_noise),
                "sampler_noise_scheduler_override": str(processed.sampler_noise_scheduler_override),
                "is_using_inpainting_conditioning": str(processed.is_using_inpainting_conditioning),
                "num_images": str(num_images),
                "all_prompts": str(processed.all_prompts),
                "all_negative_prompts": str(processed.all_negative_prompts),
                "all_seeds": str(processed.all_seeds),
                "all_subseeds": str(processed.all_subseeds),
                "infotexts": str(processed.infotexts),
                "upload_id": str(upload_id),
            }),
            "http://bluescape.dev/automatic1111-extension/v1/uploadId": str(upload_id),
            "http://bluescape.dev/automatic1111-extension/v1/userId": str(user_id),
        }
    else:
        traits = {
            "http://bluescape.dev/automatic1111-extension/v1/enabled": False,
            "http://bluescape.dev/automatic1111-extension/v1/userId": str(user_id),
        }

    return traits
