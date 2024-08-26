from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import io

def compress_image(image, quality=70):
    """
    Сжимает изображение до указанного качества (по умолчанию 70%)
    и возвращает сжатое изображение.
    """
    img = Image.open(image)
    img = img.convert("RGB")  # Убедитесь, что изображение в формате RGB
    output_io_stream = io.BytesIO()
    img.save(output_io_stream, format='JPEG', quality=quality)  # Сжимаем изображение
    output_io_stream.seek(0)
    return InMemoryUploadedFile(
        output_io_stream, 'ImageField', f"{image.name.split('.')[0]}.jpg", 'image/jpeg', output_io_stream.getbuffer().nbytes, None
    )
