from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import os

def create_certificate(name):
    # Dimensions (A4 Landscape approx @ 72dpi is 842x595, let's use 1000x700 for better res)
    width, height = 1000, 750
    background_color = (255, 255, 255)
    border_color = (0, 114, 206) # Blue from theme

    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Draw Border
    border_width = 20
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=border_color,
        width=10
    )

    # Load Fonts
    try:
        # Try to load a nice font
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except IOError:
        # Fallback to default
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Add Logo
    if os.path.exists("logo.png"):
        try:
            logo = Image.open("logo.png")
            # Resize logo to reasonable size (e.g., 150px height)
            logo_height = 150
            aspect_ratio = logo.width / logo.height
            logo_width = int(logo_height * aspect_ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

            # Paste at top center
            x_pos = (width - logo_width) // 2
            y_pos = 50
            img.paste(logo, (x_pos, y_pos), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Error loading logo: {e}")

    # Add Text
    def draw_centered_text(text, font, y, color=(0, 0, 0)):
        # textbbox returns (left, top, right, bottom)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)

    y_offset = 220

    # "SERTIFIKAT"
    draw_centered_text("SERTIFIKAT", title_font, y_offset, color=border_color)
    y_offset += 80

    # "Ushbu sertifikat taqdim etiladi:"
    draw_centered_text("Ushbu sertifikat taqdim etiladi:", subtitle_font, y_offset)
    y_offset += 60

    # Name
    draw_centered_text(name, name_font, y_offset, color=(0, 0, 0))
    y_offset += 100

    # "Matematika bilimdoni"
    draw_centered_text("Matematika bilimdoni", text_font, y_offset, color=border_color)
    y_offset += 80

    # Date
    now = datetime.datetime.now()
    date_str = now.strftime("%d.%m.%Y %H:%M")
    draw_centered_text(f"Sana: {date_str}", small_font, height - 60, color=(100, 100, 100))

    return img
