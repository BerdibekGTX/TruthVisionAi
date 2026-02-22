// frontend/src/App.jsx
import React, { useState, useCallback } from 'react';
import axios from 'axios';

// Импортируем дочерние компоненты
import Upload from './components/Upload';
import Loading from './components/Loading';
import Result from './components/Result';

// URL нашего бэкенда. Для локальной разработки используем localhost.
// ВАЖНО: Перед деплоем на Vercel нужно будет заменить на URL от Railway.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null); // Выбранный пользователем файл
  const [preview, setPreview] = useState(null); // URL для превью изображения
  const [result, setResult] = useState(null); // Результат анализа от API
  const [loading, setLoading] = useState(false); // Состояние загрузки (идет ли анализ)
  const [error, setError] = useState(null); // Сообщение об ошибке

  // --- Обработчики событий ---

  // Вызывается, когда пользователь выбирает файл в компоненте Upload
  const handleFileSelect = useCallback((selectedFile) => {
    setFile(selectedFile);
    setError(null); // Сбрасываем предыдущие ошибки
    // Создаем временный URL для отображения превью изображения
    setPreview(URL.createObjectURL(selectedFile));
  }, []);

  // Вызывается при клике на кнопку "Analyze"
  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    // FormData - стандартный способ отправки файлов через HTTP
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Отправляем POST-запрос на бэкенд с помощью axios
      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data); // Сохраняем результат в состоянии
    } catch (err) {
      // Обрабатываем ошибки, которые могут прийти от API
      const errorMessage = err.response?.data?.detail || err.message || 'An unknown error occurred.';
      setError(errorMessage);
      console.error("Analysis error:", errorMessage);
    } finally {
      // Вне зависимости от результата, выключаем индикатор загрузки
      setLoading(false);
    }
  };

  // Сбрасывает все состояния к начальным значениям
  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setLoading(false);
    setError(null);
  };

  const renderContent = () => {
    if (loading) {
      return <Loading />;
    }
    if (result) {
      return <Result result={result} onReset={handleReset} />;
    }
    // По умолчанию показываем компонент для загрузки
    return (
      <>
        <Upload onFileSelect={handleFileSelect} preview={preview} file={file} />
        {file && (
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-6 w-full bg-[#2f80ed] text-white font-semibold py-3 px-8 rounded-full hover:bg-[#1f6dd7] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze Media'}
          </button>
        )}
      </>
    );
  };

  return (
    <div className="min-h-screen w-full px-6 py-8 md:px-12 lg:px-20 text-[#111827]">
      <header className="mx-auto max-w-6xl flex items-center justify-between mb-14">
        <div className="text-2xl font-extrabold tracking-tight">
          Truth<span className="text-[#2f80ed]">Vision</span>Ai
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-[#1f2937]">
          <a href="#" className="hover:text-[#2f80ed] transition-colors">Blog</a>
          <a href="mailto:truthvisionai@gmail.com" className="hover:text-[#2f80ed] transition-colors">Contact</a>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl grid lg:grid-cols-2 gap-10 lg:gap-16 items-start">
        <section>
          <h1 className="text-5xl md:text-6xl font-extrabold leading-[1.02] tracking-tight">
            Moderate AI-Generated Media<br />
            <span className="text-[#2f80ed]">with Confidence</span>
          </h1>
          <p className="mt-8 text-xl leading-relaxed text-[#4b5563] max-w-xl">
            TruthVISION detects AI-generated images and videos and helps platforms label synthetic content to ensure transparency and trust.
          </p>
          <p className="mt-4 text-lg leading-relaxed text-[#64748b] max-w-xl">
            Automated moderation for social networks, marketplaces, video platforms, and online services.
          </p>
          <div className="mt-12 grid grid-cols-2 gap-8 max-w-xl">
            <div className="bg-white/70 border border-[#dbeafe] rounded-2xl p-5 shadow-[0_18px_45px_-28px_rgba(30,64,175,0.50)]">
              <p className="text-[#111827] text-2xl font-bold leading-tight">AI content is growing fast</p>
              <p className="mt-2 text-[#4b5563] text-lg leading-snug">across images and video</p>
            </div>
            <div className="bg-white/70 border border-[#dbeafe] rounded-2xl p-5 shadow-[0_18px_45px_-28px_rgba(30,64,175,0.50)]">
              <p className="text-[#111827] text-2xl font-bold leading-tight">Platforms need tools</p>
              <p className="mt-2 text-[#4b5563] text-lg leading-snug">to detect and label AI media</p>
            </div>
          </div>
        </section>

        <section className="relative">
          <p className="hidden md:block absolute -top-10 left-20 text-4xl text-[#2f80ed] rotate-[-6deg]" style={{ fontFamily: 'cursive' }}>
            Try it now
          </p>
          <div className="bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] border border-[#dbeafe] rounded-[30px] p-7 shadow-[0_28px_80px_-32px_rgba(30,64,175,0.48)] backdrop-blur-sm">
            <div className="text-sm font-bold uppercase tracking-wide">Beta</div>
            <p className="mt-3 text-center text-2xl font-semibold">Check if media is AI-generated</p>

            <div className="mt-5">
              {error && (
                <div className="bg-red-100 border border-red-300 text-red-700 text-center p-3 rounded-xl mb-4">
                  <p><span className="font-bold">Error:</span> {error}</p>
                </div>
              )}
              {renderContent()}
            </div>
          </div>
        </section>
      </main>

      <footer className="mx-auto max-w-6xl text-center mt-10 text-[#6b7280] text-sm">
        Powered by <a href="https://huggingface.co/haywoodsloan/ai-image-detector-dev-deploy" target="_blank" rel="noopener noreferrer" className="underline hover:text-[#2f80ed]">haywoodsloan/ai-image-detector</a>
      </footer>
    </div>
  );
}

export default App;
