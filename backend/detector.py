# backend/detector.py
import torch
from PIL import Image
from transformers import AutoModelForImageClassification, AutoImageProcessor
import io
import os
import tempfile
import cv2

# Путь к предварительно обученной модели на Hugging Face
MODEL_PATH = "haywoodsloan/ai-image-detector-dev-deploy"

# Глобальные переменные для хранения модели и процессора
# Это позволяет загружать их только один раз при старте приложения
model = None
processor = None

def load_model():
    """
    Загружает модель и процессор из Hugging Face.
    Эта функция вызывается один раз при запуске FastAPI-приложения.
    """
    global model, processor
    try:
        print("Загрузка AI модели...")
        # Загружаем процессор для предобработки изображений
        processor = AutoImageProcessor.from_pretrained(MODEL_PATH)
        # Загружаем саму модель для классификации изображений
        model = AutoModelForImageClassification.from_pretrained(MODEL_PATH)
        print("AI модель успешно загружена.")
    except Exception as e:
        # Обработка ошибок, если модель не может быть загружена
        print(f"Ошибка при загрузке модели: {e}")
        # В реальном приложении здесь можно было бы предпринять дополнительные действия,
        # например, завершить работу приложения или перейти в "безопасный" режим.
        raise


def _get_artificial_class_id():
    artificial_id = None
    for class_id, class_label in model.config.id2label.items():
        if str(class_label).lower() == "artificial":
            artificial_id = int(class_id)
            break
    return artificial_id


def _classify_pil_image(image: Image.Image) -> dict:
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits

    probabilities = torch.nn.functional.softmax(logits, dim=1)
    predicted_class_id = probabilities.argmax().item()
    confidence = probabilities.max().item()
    label = model.config.id2label[predicted_class_id]
    is_ai = label == "artificial"

    artificial_id = _get_artificial_class_id()
    if artificial_id is not None:
        ai_probability = probabilities[0][artificial_id].item()
        real_probability = 1 - ai_probability
    else:
        ai_probability = confidence if is_ai else 1 - confidence
        real_probability = 1 - ai_probability

    return {
        "is_ai": is_ai,
        "confidence": confidence,
        "label": "AI Generated" if is_ai else "Real Image",
        "ai_probability": ai_probability,
        "real_probability": real_probability,
    }

def analyze_image(image_bytes: bytes) -> dict:
    """
    Анализирует изображение и определяет, было ли оно сгенерировано ИИ.

    Args:
        image_bytes: Изображение в виде байтовой строки.

    Returns:
        Словарь с результатами анализа:
        {
            "is_ai": bool,      # True, если изображение сгенерировано ИИ
            "confidence": float, # Уверенность модели в предсказании (от 0 до 1)
            "label": str        # Человекочитаемая метка ("AI Generated" или "Real Image")
        }
    """
    if not model or not processor:
        # Этого не должно произойти, если load_model() была вызвана при старте
        raise RuntimeError("Model was not loaded. Call load_model() before analysis.")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        result = _classify_pil_image(image)
        result["input_type"] = "image"
        result["provider"] = "main_model"

        return result

    except Exception as e:
        print(f"Image analysis error: {e}")
        raise ValueError(f"Failed to process image. Make sure this is a valid image file. Error: {e}")


def analyze_video(video_bytes: bytes, sample_interval_sec: float = 1.0) -> dict:
    if not model or not processor:
        raise RuntimeError("Model was not loaded. Call load_model() before analysis.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(video_bytes)
            temp_path = temp_file.name

        capture = cv2.VideoCapture(temp_path)
        if not capture.isOpened():
            raise ValueError("Unable to read video file.")

        fps = capture.get(cv2.CAP_PROP_FPS) or 0
        if fps <= 0:
            fps = 25.0

        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration_seconds = (total_frames / fps) if total_frames > 0 else 0
        frame_step = max(int(round(fps * sample_interval_sec)), 1)

        frame_index = 0
        sampled_frames = 0
        ai_frames = 0
        confidence_sum = 0.0
        ai_probability_sum = 0.0

        while True:
            ok, frame = capture.read()
            if not ok:
                break

            if frame_index % frame_step == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = Image.fromarray(rgb_frame)
                frame_result = _classify_pil_image(frame_image)

                sampled_frames += 1
                if frame_result["is_ai"]:
                    ai_frames += 1

                confidence_sum += frame_result["confidence"]
                ai_probability_sum += frame_result["ai_probability"]

            frame_index += 1

        capture.release()

        if sampled_frames == 0:
            raise ValueError("No frames were extracted from the video.")

        ai_probability = ai_probability_sum / sampled_frames
        real_probability = 1 - ai_probability
        confidence = confidence_sum / sampled_frames
        ai_ratio = ai_frames / sampled_frames
        is_ai_video = ai_ratio > 0.5

        return {
            "input_type": "video",
            "is_ai": is_ai_video,
            "label": "AI Generated Video" if is_ai_video else "Real Video",
            "confidence": confidence,
            "ai_probability": ai_probability,
            "real_probability": real_probability,
            "sampled_frames": sampled_frames,
            "ai_frames": ai_frames,
            "real_frames": sampled_frames - ai_frames,
            "sample_interval_sec": sample_interval_sec,
            "duration_seconds": round(duration_seconds, 2),
        }
    except Exception as e:
        print(f"Video analysis error: {e}")
        raise ValueError(f"Failed to process video. Make sure this is a valid video file. Error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# Пример использования (для тестирования)
if __name__ == '__main__':
    # Этот блок будет выполнен только при запуске файла напрямую (python detector.py)
    # Используется для быстрой проверки работоспособности
    try:
        load_model()
        # Попробуем проанализировать тестовое изображение (нужно создать/скачать)
        with open("test_image.jpg", "rb") as f:
            image_bytes = f.read()
            result = analyze_image(image_bytes)
            print("Результат анализа:", result)
    except FileNotFoundError:
        print("Для запуска теста создайте файл 'test_image.jpg' в той же директории.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
