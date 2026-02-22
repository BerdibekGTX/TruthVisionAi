# backend/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Импортируем функции из нашего модуля detector
from backend.detector import load_model, analyze_image, analyze_video

# Определяем "продолжительность жизни" приложения с помощью asynccontextmanager
# Это современный способ выполнения действий при старте и завершении работы приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, который выполнится перед запуском приложения
    print("Запуск приложения...")
    load_model()  # Загружаем AI модель при старте
    yield
    # Код, который выполнится после завершения работы приложения
    print("Завершение работы приложения.")

# Создаем экземпляр FastAPI с определенной "продолжительностью жизни"
app = FastAPI(lifespan=lifespan)

# --- Настройка CORS ---
# Определяем, каким frontend-приложениям разрешено отправлять запросы
# В данном случае "*" означает, что разрешены все источники.
# Для продакшена рекомендуется указывать конкретный URL вашего фронтенда.
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Create React App dev server
    "https://truthvision-ai.vercel.app", # Пример URL для продакшена на Vercel
    "*" # Для простоты разработки
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, etc.)
    allow_headers=["*"],  # Разрешить все заголовки
)

# --- Определение констант ---
# Максимальный размер файлов в байтах
MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024
MAX_VIDEO_FILE_SIZE = 100 * 1024 * 1024

# Допустимые MIME-типы
ACCEPTED_IMAGE_MEDIA_TYPES = ["image/jpeg", "image/png", "image/webp"]
ACCEPTED_VIDEO_MEDIA_TYPES = [
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-matroska",
    "video/x-msvideo",
]
ACCEPTED_MEDIA_TYPES = ACCEPTED_IMAGE_MEDIA_TYPES + ACCEPTED_VIDEO_MEDIA_TYPES

# --- Эндпоинты API ---

@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки работоспособности сервиса.
    Отвечает простым JSON-сообщением. Используется системами мониторинга.
    """
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    """
    Основной эндпоинт для анализа изображения или видео.
    Для видео берется 1 кадр в секунду, каждый кадр анализируется моделью.
    """
    max_file_size = MAX_VIDEO_FILE_SIZE if file.content_type in ACCEPTED_VIDEO_MEDIA_TYPES else MAX_IMAGE_FILE_SIZE
    file_size = file.size or 0
    if file_size > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size must not exceed {max_file_size / 1024 / 1024:.0f}MB."
        )

    # 2. Валидация типа файла
    if file.content_type not in ACCEPTED_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed formats: {', '.join(ACCEPTED_MEDIA_TYPES)}"
        )

    try:
        file_bytes = await file.read()
        if file.content_type in ACCEPTED_VIDEO_MEDIA_TYPES:
            result = analyze_video(file_bytes, sample_interval_sec=1.0)
        else:
            result = analyze_image(file_bytes)

        return result

    except ValueError as ve:
        # Обрабатываем ошибку, если изображение не может быть обработано
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        # Обрабатываем любые другие непредвиденные ошибки на сервере
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred. Please try again later."
        )

# --- Запуск сервера (для локальной разработки) ---
# Этот блок позволяет запустить сервер напрямую командой `python main.py`
if __name__ == "__main__":
    # uvicorn.run принимает строку в формате "имя_файла:имя_приложения"
    # host="0.0.0.0" делает сервер доступным в локальной сети
    # port=8000 - стандартный порт для веб-сервисов
    # reload=True автоматически перезапускает сервер при изменениях в коде
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
