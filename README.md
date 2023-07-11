# Bluescape Extension for Stable Diffusion WebUI

Upload generated images to a Bluescape workspace for review and collaborate with others.

![Uploading images to Bluescape Worksapce](resources/02-uploading-to-bluescape.png "Uploading images to Bluescape Worksapce")

![Generated images of viking king in a Bluescape Workspace](resources/01-bluescape-workspace.png "Generated images in Bluescape Workspace")

## Installation

1. Open "Extensions" tab.
2. Open "Install from URL" tab in the tab.
3. Enter  `https://github.com/Bluescape/sd-webui-bluescape`  to "URL for extension's git repository".
4. Press "Install" button.
5. Wait for 5 seconds, and you will see the message "Installed into stable-diffusion-webui\extensions\sd-webui-bluescape. Use Installed tab to restart".
6. Go to "Installed" tab, click "Check for updates", and then click "Apply and restart UI". (The next time you can also use these buttons to update the extension.)
7. Completely restart A1111 webui including the backend through your terminal

_Note: Currently the Bluescape extension only supports the standard A1111 domain / port `(localhost:7860)`._

## Getting started

Get started using the Bluescape extension:

1. **Open Extension**: Open the Bluescape tab on the A1111 webui
2. **Register**: If you haven’t done so yet, register for a free account by clicking the button
3. **Login**: Log into your account
4. **Select Workspace**: Choose the workspace where you’d like to upload generated images
5. **Enable Upload Option**: Navigate to either the ‘txt2img’ or ‘img2img’ tab and select the “Upload results to Bluescape” option
6. **Generate**: Generate images
7. **Review**: Open your workspace to review, curate and collaborate on the generated images

_Note: The free account has a limit on the number of workspaces and amount of data that can be stored in the workspace. Additional resources are available through paid plans._

![Bluescape Extension](resources/09-extension.png "Bluescape extension")

## Configuration options

These are the defaults for the extension configuration options:

![Default configuration options for the Bluescape extension](resources/03-configuration-options.png "Configuration options")

The options are categorized under General and Canvas sections.

## General

### Include extended generation data in workspace

By default the extension adds a text field to the workspace with the basic generation data:

![Generated image with default generation data in Bluescape Workspace](resources/04-generation-data.png "Generation data")

Enabling extended generation data adds another text field with additional generation information:

![Generated image with default and extended generation data in Bluescape Workspace](resources/05-extended-generation-data.png "Extended generation data")

_Note: The default generation data added to the Bluescape workspace can be copied back to Automatic1111 and re-applied through the prompt._

### Include source image in workspace (img2img)

Whether or not to include the source image in the workspace when using img2img:

![Source image included in Bluescape Workspace](resources/06-source-image.png "Source image")

### Include image mask in workspace (img2img)

Whether or not to include the image mask in the workspace when using img2img with masks.

![Image mask included in Bluescape Workspace](resources/10-image-mask.png "Image mask")

### Scale images to standard size (1000x1000) in workspace

Whether to scale images to standard Bluescape image size of 1000x1000 in the workspace.

Note, that this only applies scaling at the workspace level and does not actually change the image data. You can always resize to original size in the workspace as well:

![Resize to Original context menu item on an image element in Bluescape Workspace](resources/07-resize-to-original-1.png "Resize to original context menu")

![Image element resized to original size in Bluescape Workspace](resources/08-resize-to-original-2.png "Original sized image")

This is a good option to enable when you have a lot of images in the workspace from different sources and it works well when using images between 500-1000. However, if you work on large images of different aspect ratios it is best to turn this off.

### Store generation data as metadata in image object within workspace

When this is enabled the generation data and extended generation data are stored as metadata into the Bluescape workspace image elements. This is in anticipation of future Bluescape functionality that makes it easier to copy the generation data back to A1111 and other workflow improvements as well

You can disable this but it may limit the uploaded images from taking advantage of future A1111 related improvements in Bluescape.

### Send extension usage analytics

Whether to send analytics events about user registration, login and upload events. This helps Bluescape assess the amount of use of the extension.

You can disable this if you'd like.

## Canvas

### Title format

Canvas title is the text above the generation canvas.

Title format allows you to choose from the following options.

#### Default (A1111 | prompt)

"A1111" and the prompt (max 45 characters total).

![Canvas title A1111 with prompt](resources/11-title-a1111.png "Canvas title A1111 with prompt")

#### Generation mode (txt2img / img2img)

Either txt2img or img2img based on the generation mode being active at the moment. No prompt included.

![Canvas title generation mode](resources/12-title-mode.png "Canvas title generation mode")

#### User name (John Smith)

The name of the user that generated the images. By default the name used to register with Bluescape account, but there is an option to override the name in the settings. No prompt included.

![Canvas title user name](resources/13-title-username.png "Canvas title user name")

#### Timestamp (2023-07-06 10:35:41)

The local timestamp as reported by the extension when the canvas was created. No prompt included.

![Canvas title timestamp](resources/14-title-time.png "Canvas title timestamp")

### Header format

Canvas header is the text inside at the top of the generation canvas.

Header format allows you to customize the information included with similar options to the title format. Note, that the prompt is always included in the header format regardless of the option.

#### Default (A1111 | prompt)

"A1111" and the prompt (max 145 characters).

![Canvas header A1111 with prompt](resources/15-header-a1111.png "Canvas header A1111 with prompt")

#### Generation mode + prompt (txt2img / img2img | prompt)

Either txt2img or img2img based on the generation mode being active at the moment and the prompt.

![Canvas header generation mode](resources/16-header-mode.png "Canvas header generation mode")

#### User name + prompt (John Smith | prompt)

The name of the user that generated the images abd the prompt. By default the name used to register with Bluescape account, but there is an option to override the name in the settings.

![Canvas header user name](resources/17-header-username.png "Canvas title user name")

#### Timestamp + prompt (2023-07-06 10:35:41 | prompt)

The local timestamp as reported by the extension when the canvas was created and the prompt.

![Canvas header timestamp](resources/18-header-time.png "Canvas header timestamp")

### User specific canvas placement

When enabled, this option arranges each new generation canvas you create adjacent to your most recent one.

![New generation canvas being created next to the most recent one from the same user in Bluescape workspace](resources/19-userspecific-existing.png "New generation canvas being created next to the most recent one from the same user")

If you have not created any generation canvases previously, a new row will be established for your use.

![New generation canvas being created on a new row in Bluescape workspace](resources/20-new-row.png "New generation canvas being created on a new row")

If you move your most recent canvas manually in the workspace the new generation canvas is created next to it.

![New generation canvas being created next to the most recent one, even if it was moved](resources/21-new-position.png "New generation canvas being created next to the most recent one, even if it was moved")

When this setting is deactivated, your newly created canvas will be positioned alongside the most recent generation canvas of any other user.

![New generation canvas being created next to the most recent one from any user](resources/22-no-user-specific.png "New generation canvas being created next to the most recent one from any user")

### Use canvas border color

By default canvas border color is not used, but you can enable the option and choose a custom color from the color picker.

There are various scenarios this can be used for, for example to differentiate users working in the same workspace even if the user name is not included in the canvas title or header.

![Canvases with different border colors per user](resources/23-canvas-border-colors.png "Canvases with different border colors per user")

### Override user name for title and header

By default canvas title and canvas header user name options use the name user registered their Bluescape account with. For convenience you can override the value here with a nick name or something else.

![Overriding the user name in settings](resources/24-nickname-override.png "Overriding the user name in settings")

![Nick name in workspace](resources/25-nickname-workspace.png "Nick name in workspace")

## Future aspirations

- Upload ControlNet source image and mask to the workspace
- Image element context menu item to copy the generation data in A1111 webui compatible format
- A1111 running in non-default domain/port
- Retrigger image generation with same or modified parameters in A1111 directly from the workspace
- Browse and upload existing generated images from A1111

## Feedback and more information

Feel free to send us any feedback you may have either through Github or
[Bluescape community forums](https://community.bluescape.com/t/stable-diffusion-automatic1111-bluescape-extension/3730).

The extension is open source and licensed under [MIT License](LICENSE).

If you are interested in developing on the Bluescape platform, please take a look at the [developer documentation](https://api.apps.us.bluescape.com/docs/).
