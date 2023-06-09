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
import io

from .templates import status_block, workspace_label_block
from .expired_token_exception import ExpiredTokenException
from .extension import BluescapeUploadManager
from .config import Config
import modules.scripts as scripts
from modules.processing import Processed, StableDiffusionProcessingImg2Img, StableDiffusionProcessingTxt2Img
import gradio as gr
from .traits import get_canvas_traits, get_image_traits
from .bluescape_layout import BluescapeLayout
from .misc import FindSpaceDirection, find_on_key, find_on_key_value, is_hex_color
import uuid

class Script(scripts.Script):

    manager = BluescapeUploadManager()
    manager.initialize()

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def title(self):
        self.manager.state.read_versions(self.filename)
        return "Bluescape upload extension"

    def ui(self, is_img2img):

        with gr.Row(variant="panel"):
            do_upload = gr.Checkbox(info="Bluescape", label="Upload results to Bluescape")
        with gr.Row(variant="panel"):
            workspace_label = gr.HTML(value=workspace_label_block)
        with gr.Row(variant="panel"):
            if is_img2img:
                status = gr.HTML(value=status_block("bluescape-status-img2img"))
            else:
                status = gr.HTML(value=status_block("bluescape-status-txt2img"))
        return [do_upload, workspace_label, status]

    def process(self, p, *args):
        # Uploads the UI state
        self.manager.set_status("Waiting...", self.is_txt2img)

    # Only for AlwaysVisible scripts
    def postprocess(self, p, processed: Processed, do_upload, *args):

        if do_upload == True:
            # Lets generate a consistent id for this upload session
            upload_id = str(uuid.uuid4())
            print(f"Uploading images to Bluescape - (upload_id: {upload_id})")

            # Uploads the UI state
            self.manager.set_status("Preparing...", self.is_txt2img)

            # Check for some common settings
            enable_verbose = self.manager.state.enable_verbose
            enable_metadata = self.manager.state.enable_metadata
            img2img_include_init_images = self.manager.state.img2img_include_init_images
            img2img_include_mask_image = self.manager.state.img2img_include_mask_image
            scale_to_standard_size = self.manager.state.scale_to_standard_size
            user_swimlane = self.manager.state.user_swimlane
            use_canvas_border_color = self.manager.state.use_canvas_border_color
            canvas_border_color = self.manager.state.canvas_border_color
            user_id = self.manager.state.user_id

            # Detect what we are using to generate
            generation_type = "unknown"
            if self.is_txt2img and not self.is_img2img:
                generation_type = "txt2img"
                p_img2img = None
            elif self.is_img2img and not self.is_txt2img:
                generation_type = "img2img"
                p_img2img: StableDiffusionProcessingImg2Img = p
            else:
                print(f"Unkown image generation type - txt2img: {self.is_txt2img}, img2img: {self.is_img2img} - (upload_id: {upload_id})")

            # Detect number of images we are dealing with
            index_of_first_image = processed.index_of_first_image

            num_init_images = 0
            include_mask = False

            if img2img_include_init_images and generation_type == "img2img" and p_img2img:
                num_init_images = len(p_img2img.init_images)

            if img2img_include_mask_image and p_img2img is not None and p_img2img.image_mask is not None:
                num_init_images = num_init_images + 1
                include_mask = True

            num_generated_images = len(processed.images) - index_of_first_image
            num_images =  num_init_images + num_generated_images

            image_size = (1000, 1000) if scale_to_standard_size else (processed.width, processed.height)

            # Lets calculate the layout
            layout = BluescapeLayout(num_images, image_size, enable_verbose)
            # How much space we need
            canvas_bounding_box = layout.get_canvas_bounding_box()

            # Default to going "Right"
            direction = FindSpaceDirection.Right

            # We'll use this for padding between the swimlanes, if necessary
            canvas_y_padding = 1500

            try:
                # Ok, now lets see where to place this. This is quite ugly.

                # First, lets try to get all existing Canvases in the workspace
                existing_canvases = self.manager.get_existing_canvases()
                if existing_canvases:
                    # Let's filter the canvases with ones that are generated by our extension
                    extension_canvases = find_on_key(existing_canvases, "http://bluescape.dev/automatic1111-extension/v1/enabled")
                    if extension_canvases:
                        if user_swimlane:
                            # If the user has selected user_swimlane option, then we need to
                            # check whether the user has previously created a canvas in this workspace
                            # with the extension and aim for the latest one.
                            user_canvases = find_on_key_value(extension_canvases, "http://bluescape.dev/automatic1111-extension/v1/userId", user_id)
                            if user_canvases:
                                latest_canvas = max(user_canvases, key=lambda obj: obj.get("id", 0))
                                if latest_canvas:
                                    canvas_bounding_box = (latest_canvas.get("transform").get("x"), latest_canvas.get("transform").get("y"), canvas_bounding_box[2], canvas_bounding_box[3])
                                    print(f"Existing user canvas found - going RIGHT from there - (upload_id: {upload_id})")
                                else:
                                    print(f"Invalid user canvas, no id found - going DOWN from origin - (upload_id: {upload_id})")
                                    direction = FindSpaceDirection.Down
                            else:
                                # If no existing canvas found for this user, lets start from
                                # 0,0, but go down to find a start for this user's swimlane
                                print(f"No existing user canvas found - going DOWN from origin - (upload_id: {upload_id})")
                                direction = FindSpaceDirection.Down
                        else:
                            # Otherwise check if anybody has created a generation canvas
                            # in this workspace and aim for the latest one.
                            latest_canvas = max(extension_canvases, key=lambda obj: obj.get("id", 0))
                            if latest_canvas:
                                canvas_bounding_box = (latest_canvas.get("transform").get("x"), latest_canvas.get("transform").get("y"), canvas_bounding_box[2], canvas_bounding_box[3])
                                print(f"Existing extension canvas found - going RIGHT from there - (upload_id: {upload_id})")
                            else:
                                print(f"Invalid extension canvas, no id found - going DOWN from origin - (upload_id: {upload_id})")
                                direction = FindSpaceDirection.Down
                    else:
                        # If nobody has done it, we'll start from 0,0, but go down to
                        # find space for a shared swimlane
                        print(f"No extension canvas found - going DOWN from origin - (upload_id: {upload_id})")
                        direction = FindSpaceDirection.Down

                else:
                    print(f"No canvas found - going DOWN from origin - (upload_id: {upload_id})")
                    direction = FindSpaceDirection.Down

                # Find available space for us
                available_canvas_bounding_box = self.manager.find_space(canvas_bounding_box, direction.value)

                if direction == FindSpaceDirection.Down and available_canvas_bounding_box[1] != 0:
                    # Looks like there wasn't space at 0,0, but found space further down. However,
                    # let's add some padding to make the swimlane clear.
                    new_bounding_box = (available_canvas_bounding_box[0], available_canvas_bounding_box[1] + canvas_y_padding, available_canvas_bounding_box[2], available_canvas_bounding_box[3])
                    print(f"Adjusting canvas location further to add padding - (upload_id: {upload_id})")
                    available_canvas_bounding_box = self.manager.find_space(new_bounding_box, direction.value)

                # We found space here
                print(f"Target canvas location found: {str(available_canvas_bounding_box)} - (upload_id: {upload_id})")

                # Move layout to target that
                layout.translate(available_canvas_bounding_box)

                # Create canvas
                canvas_title = layout.get_canvas_name(self.manager.state, processed.prompt, generation_type)
                canvas_traits = get_canvas_traits(enable_metadata, processed, generation_type, upload_id, num_images, user_id)

                canvas_color = canvas_border_color if is_hex_color(canvas_border_color) and use_canvas_border_color else "#ffffff"
                canvas_id = self.manager.create_canvas_at(canvas_title, available_canvas_bounding_box, canvas_traits, canvas_color)

                # Create title inside the canvas
                top_title_location = layout.get_top_title_location()
                (header, top_title) = layout.get_top_title(processed.prompt, generation_type, self.manager.state)
                self.manager.create_top_title(top_title_location, top_title, header)

                # Create generation data section regardless
                infotext_location = layout.get_infotext_location()
                self.manager.create_generation_data(infotext_location, processed.infotexts[0])
                infotext_label_location = layout.get_infotext_label_location()
                self.manager.create_generation_label(infotext_label_location, f"Generation data ({generation_type}):")

                # Create extended data section only if verbose_mode enabled
                if (enable_verbose):
                    extended_generation_data = [
                        ( "Image CFG scale", processed.image_cfg_scale ),
                        ( "Subseed strength", processed.subseed_strength ),
                        ( "Seed resize from w", processed.seed_resize_from_w ),
                        ( "Seed resize from h", processed.seed_resize_from_h ),
                        ( "DDIM Discretize", processed.ddim_discretize ),
                        ( "ETA", processed.eta ),
                        ( "Clip skip", processed.clip_skip ),
                        ( "Sigma churn", processed.s_churn ),
                        ( "Sigma noise", processed.s_noise ),
                        ( "Sigma tmin", processed.s_tmin ),
                        ( "Sigma tmax", processed.s_tmax ),
                        ( "Sampler noise scheduler override", processed.sampler_noise_scheduler_override ),
                        ( "Is using inpainting conditioning", processed.is_using_inpainting_conditioning ),
                        ( "Extra generation params", processed.extra_generation_params ),
                        ( "Bluescape upload id", upload_id ),
                    ]
                    bottom_small_infobar_location = layout.get_bottom_infobar_location()
                    self.manager.create_extended_data(bottom_small_infobar_location, extended_generation_data)
                    infotext_label_location = layout.get_extended_generation_data_label_location()
                    self.manager.create_generation_label(infotext_label_location, f"Extended generation data:")

                # Get image coordinates
                image_layout = layout.get_image_grid_layout()
                # Get seed / label coordinates
                label_layout = layout.get_label_grid_layout()

                # We'll use the shared 'i' between the first iterator (init images)
                # and the second one (generated images). This is used to address image_layout
                # and seed_layout, which account for both sets of images.
                i = 0

                # First check for init images (source images)
                if img2img_include_init_images and generation_type == "img2img" and p_img2img:
                    for index, image in enumerate(p_img2img.init_images):
                        seed = "source_image"
                        subseed = "unknown"
                        infotext = "source_image"

                        self.manager.set_status(f"Uploading image: {i + 1} / {num_images}", self.is_txt2img)

                        traits = get_image_traits(enable_metadata, processed, seed, subseed, infotext, generation_type, upload_id, user_id)

                        x, y = image_layout[i]
                        width, height = image_size

                        # Filename based on the index
                        filename = f"source-image_{index}.png"
                        png_data = io.BytesIO()
                        image.save(png_data, format="PNG")
                        self.manager.upload_image_at(png_data.getvalue(), filename, (x, y, width, height), traits)

                        label_x, label_y = label_layout[i]
                        label_width = image_size[0]
                        label_height = 50
                        self.manager.create_label((label_x, label_y, label_width, label_height), "Source image")

                        i += 1

                        print(f"Init image has been uploaded to Bluescape - (upload_id: {upload_id})")

                    if include_mask:
                        self.manager.set_status(f"Uploading image: {i + 1} / {num_images}", self.is_txt2img)
                        x, y = image_layout[i]
                        width, height = image_size

                        # Filename based on the index
                        filename = f"image_mask.png"
                        png_data = io.BytesIO()
                        p_img2img.image_mask.save(png_data, format="PNG")

                        seed = "image_mask"
                        subseed = "unknown"
                        infotext = "image_mask"

                        traits = get_image_traits(enable_metadata, processed, seed, subseed, infotext, generation_type, upload_id, user_id)

                        self.manager.upload_image_at(png_data.getvalue(), filename, (x, y, width, height), traits)

                        label_x, label_y = label_layout[i]
                        label_width = image_size[0]
                        label_height = 50
                        self.manager.create_label((label_x, label_y, label_width, label_height), "Image mask")

                        i += 1

                        print(f"Mask image has been uploaded to Bluescape - (upload_id: {upload_id})")

                # i continues where it was left of above
                # Now we'll deal with the generated images
                for index, image in enumerate(processed.images):
                    if index >= index_of_first_image:
                        adjusted_index = index - index_of_first_image

                        self.manager.set_status(f"Uploading image: {i + 1} / {num_images}", self.is_txt2img)

                        seed = processed.all_seeds[adjusted_index]
                        subseed = processed.all_subseeds[adjusted_index]
                        infotext = processed.infotexts[adjusted_index]

                        traits = get_image_traits(enable_metadata, processed, seed, subseed, infotext, generation_type, upload_id, user_id)

                        x, y = image_layout[i]
                        width, height = image_size

                        # Filename based on seed and subseed
                        filename = f"{seed}-{subseed}.png"
                        png_data = io.BytesIO()
                        image.save(png_data, format="PNG")
                        self.manager.upload_image_at(png_data.getvalue(), filename, (x, y, width, height), traits)

                        label_x, label_y = label_layout[i]
                        label_width = image_size[0]
                        label_height = 50
                        self.manager.create_seed_label((label_x, label_y, label_width, label_height), seed, subseed)

                        i += 1

                        print(f"Image {index} has been uploaded to Bluescape - (upload_id: {upload_id})")
                    else:
                        print(f"Ignoring generated image with index {index}, as it is smaller than index of first generated image: {index_of_first_image} - (upload_id: {upload_id})")

                # Provide a link to the canvas back to the UI
                state = self.manager.state
                link_to_canvas = f"{Config.client_base_domain}/applink/{state.selected_workspace_id}?objectId={canvas_id}"
                self.manager.set_status(f"Upload complete - <a href='{link_to_canvas}' target='_blank'>Click here to open workspace</a>", self.is_txt2img)

                # Analytics
                self.manager.analytics.send_uploaded_generated_images_event(state.user_token, state.selected_workspace_id, num_images, state.user_id)

                print(f"Upload complete - (upload_id: {upload_id})")
            except ExpiredTokenException:
                self.manager.state.token_expired = True

        return True
