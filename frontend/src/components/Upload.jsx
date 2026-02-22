// frontend/src/components/Upload.jsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

// `onFileSelect` - функция для передачи выбранного файла в родительский компонент (App.jsx)
// `preview` - URL-адрес для предварительного просмотра медиа
function Upload({ onFileSelect, preview, file }) {
  // `onDrop` - это callback, который будет вызван, когда пользователь выберет файл(ы)
  const onDrop = useCallback((acceptedFiles) => {
    // Мы ожидаем только один файл, поэтому берем первый из массива
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  // Hook `useDropzone` из библиотеки react-dropzone
  // Он предоставляет все необходимые props для создания drag-and-drop зоны
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.png', '.jpg', '.webp'],
      'video/*': ['.mp4', '.webm', '.mov', '.mkv']
    },
    multiple: false // Разрешаем выбор только одного файла
  });

  const isVideo = file?.type?.startsWith('video/');

  return (
    <div className="w-full text-center">
      {preview ? (
        <div className="mb-4">
          {isVideo ? (
            <video src={preview} controls className="rounded-2xl mx-auto max-h-72 shadow-md" />
          ) : (
            <img src={preview} alt="Image preview" className="rounded-2xl mx-auto max-h-72 shadow-md" />
          )}
          <p className="text-sm text-[#6b7280] mt-3">
            {isVideo ? 'Video selected. We analyze 1 frame per second.' : 'Image selected. Click Analyze to continue.'}
          </p>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`
            p-10 border-2 border-dashed rounded-3xl cursor-pointer
            transition-colors duration-200
            ${isDragActive ? 'border-[#2f80ed] bg-[#eff6ff]' : 'border-[#bfdbfe] hover:border-[#93c5fd] bg-white'}
          `}
        >
          <input {...getInputProps()} />
          <div className="mx-auto mb-4 h-16 w-16 rounded-2xl bg-[#eff6ff] border border-[#bfdbfe] flex items-center justify-center text-3xl">
            🎞️
          </div>
          <p className="text-[#111827] text-xl font-semibold">
            {isDragActive ?
              "Drop file to upload" :
              "Drag an image/video here or click to choose"
            }
          </p>
          <p className="text-[#6b7280] mt-2">For video: frame-by-frame analysis (1 frame/sec)</p>
          <p className="text-[#6b7280] mt-1 text-sm">Max image: 5MB, max video: 100MB</p>
        </div>
      )}
    </div>
  );
}

export default Upload;
