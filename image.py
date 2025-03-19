from PIL import Image, ImageDraw, ImageFont

def wrap_text_by_pixel(draw, text, font, max_width):
    """
    Splits `text` into multiple lines so that no line exceeds `max_width` in pixels.
    Returns a list of lines.
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        candidate_line = ' '.join(current_line + [word])
        left, top, right, bottom = draw.textbbox((0, 0), candidate_line, font=font)
        candidate_width = right - left

        if candidate_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def create_cover_with_top_image(
    title_text: str,
    top_image_path: str = "test.png",
    output_path: str = "output.png",
    font_path: str = "OpenSans-Bold.ttf",
    # The width used for layout (text wrapping, top image scaling):
    layout_width: int = 1194,
    font_size: int = 40,
    text_color=(0, 0, 0),
    margin_x: int = 20,
    top_margin: int = 5,
    bottom_margin: int = 50,
    corner_radius: int = 30,
    # The final width after we finish all processing (None means no extra downscale).
    final_resize_width: int = None
):
    """
    Creates an image with:
      1) A top image (resized to layout_width),
      2) A white background below it with wrapped text,
      3) Rounded corners,
      4) (Optional) Final downscale to `final_resize_width`.

    :param title_text:        Text to display beneath the top image.
    :param top_image_path:    Path to the top image (e.g., 'test.png').
    :param output_path:       Where to save the final image (e.g., 'output.png').
    :param font_path:         Path to a .ttf font (e.g., 'OpenSans-Bold.ttf').
    :param layout_width:      The width used during layout (default=1194).
    :param font_size:         Font size for drawing the text.
    :param text_color:        (R, G, B) color for text.
    :param margin_x:          Left margin for the text area.
    :param top_margin:        Space between bottom of top image & start of text.
    :param bottom_margin:     Space below the final line of text.
    :param corner_radius:     Radius for rounded corners (default=30).
    :param final_resize_width:If set, the resulting image will be proportionally
                              scaled to this width. Height is scaled accordingly.
                              If None, no additional downscale.
    """

    # 1. Load and resize top image to layout_width
    top_img = Image.open(top_image_path).convert("RGB")
    orig_w, orig_h = top_img.size
    scale_factor = layout_width / orig_w
    new_height = int(orig_h * scale_factor)
    top_img = top_img.resize((layout_width, new_height), Image.LANCZOS)

    # 2. Prepare font and measure-draw
    font = ImageFont.truetype(font_path, font_size)
    temp_img = Image.new("RGB", (1, 1))
    measure_draw = ImageDraw.Draw(temp_img)

    # 3. The max text width for each line
    max_text_width = layout_width - margin_x

    # 4. Wrap text by pixel width
    wrapped_lines = wrap_text_by_pixel(measure_draw, title_text, font, max_text_width)

    # 5. Determine line height
    line_height = font.getmetrics()[0] + 5

    # 6. Compute total text block height
    text_block_height = line_height * len(wrapped_lines)

    # 7. Calculate final layout image height
    total_height = new_height + top_margin + text_block_height + bottom_margin

    # 8. Create the layout image (white background, the same size we used for layout)
    final_img = Image.new("RGB", (layout_width, total_height), color="white")

    # 9. Paste top image at the top
    final_img.paste(top_img, (0, 0))

    # 10. Draw text left-aligned
    draw = ImageDraw.Draw(final_img)
    current_y = new_height + top_margin
    for line in wrapped_lines:
        left, top, right, bottom = measure_draw.textbbox((0, 0), line, font=font)
        draw.text((margin_x, current_y), line, font=font, fill=text_color)
        current_y += line_height

    # 11. Convert to RGBA so we can apply a rounded corner mask
    final_img = final_img.convert("RGBA")

    # 12. Create a mask for rounded corners
    mask = Image.new("L", (layout_width, total_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (layout_width, total_height)],
        corner_radius,
        fill=255
    )

    # 13. Apply the mask for rounded corners
    final_img.putalpha(mask)

    # 14. If final_resize_width is specified, downscale proportionally
    if final_resize_width is not None and final_resize_width < layout_width:
        # compute new height to maintain aspect ratio
        new_scale_factor = final_resize_width / layout_width
        new_resized_height = int(total_height * new_scale_factor)
        final_img = final_img.resize(
            (final_resize_width, new_resized_height), Image.LANCZOS
        )

    # 15. Save final result
    final_img.save(output_path)


def generate_my_post_image(title_text):
    """
    A helper function you can call from your main.
    Example usage with final_resize_width=600 to shrink after layout.
    """
    create_cover_with_top_image(
        title_text=title_text,
        top_image_path="assets/default/template.png",
        output_path="assets/cache/reddit_post_cover.png",
        font_path="assets/default/OpenSans-Bold.ttf",
        layout_width=1194,    # Do all text layout at 1194px wide
        font_size=70,
        text_color=(0, 0, 0),
        margin_x=20,
        top_margin=5,
        bottom_margin=50,
        corner_radius=30,
        final_resize_width=900  # for example, final output will be 600px wide
    )


# ---------------
# Example direct call from main:
#if __name__ == "__main__":
    # generate_my_post_image('AITA for "ruining" my coworker\'s big reveal by guessing it right away?')
