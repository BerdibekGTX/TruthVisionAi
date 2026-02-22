// frontend/src/components/Result.jsx
import React from 'react';

// `result` - объект с данными от API ({ label, confidence, is_ai })
// `onReset` - функция для сброса состояния и возврата к экрану загрузки
function Result({ result, onReset }) {
  const isAiGenerated = result.is_ai;
  const resultColor = isAiGenerated ? 'text-[#dc2626]' : 'text-[#059669]';
  const resultIcon = isAiGenerated ? '🤖' : '✅';
  const aiProbability = (result.ai_probability ?? (isAiGenerated ? result.confidence : 1 - result.confidence)) * 100;
  const realProbability = (result.real_probability ?? (100 - aiProbability) / 100) * 100;
  const confidenceValue = result.confidence * 100;
  const confidencePercentage = confidenceValue.toFixed(1);
  const isVideo = result.input_type === 'video';
  const hasGrok = !!result.grok;

  const getReliability = () => {
    if (confidenceValue > 99.9) {
      return {
        title: 'Reliability coefficient: Very High',
        desc: 'Above 99.9%: result is highly reliable.',
        style: 'bg-[#ecfdf3] border-[#86efac] text-[#166534]',
      };
    }
    if (confidenceValue >= 90) {
      return {
        title: 'Reliability coefficient: Suspicious',
        desc: 'From 90% to 99.9%: double-check manually.',
        style: 'bg-[#fff7ed] border-[#fdba74] text-[#9a3412]',
      };
    }
    return {
      title: 'Reliability coefficient: Low',
      desc: 'Below 90%: low reliability, verification recommended.',
      style: 'bg-[#fef2f2] border-[#fca5a5] text-[#991b1b]',
    };
  };

  const reliability = getReliability();

  return (
    <div className="flex flex-col items-center justify-center text-center p-4 md:p-6">
      <div className={`text-8xl mb-4 ${resultColor}`}>{resultIcon}</div>

      <h2 className={`text-4xl font-bold mb-2 ${resultColor}`}>{result.label}</h2>

      <p className="text-5xl font-black text-[#111827] mb-1">
        {confidencePercentage}%
      </p>
      <p className="text-[#6b7280] mb-6">Model confidence</p>

      {isVideo && (
        <div className="w-full max-w-md mb-6 rounded-xl bg-[#eff6ff] border border-[#bfdbfe] p-4 text-left">
          <p className="text-sm text-[#1e3a8a] font-semibold">Video analysis details</p>
          <p className="text-sm text-[#334155] mt-1">Frames analyzed: {result.sampled_frames}</p>
          <p className="text-sm text-[#334155]">AI frames: {result.ai_frames}</p>
          <p className="text-sm text-[#334155]">Real frames: {result.real_frames}</p>
          <p className="text-sm text-[#334155]">Sampling: {result.sample_interval_sec}s</p>
          <p className="text-sm text-[#334155]">Duration: {result.duration_seconds}s</p>
        </div>
      )}

      <div className="w-full max-w-md text-left space-y-4 mb-8">
        <div>
          <div className="flex items-center justify-between text-sm font-semibold mb-1">
            <span className="text-[#111827]">AI probability</span>
            <span className="text-[#2f80ed]">{aiProbability.toFixed(1)}%</span>
          </div>
          <div className="h-2.5 w-full bg-[#dbeafe] rounded-full overflow-hidden">
            <div className="h-full bg-[#2f80ed]" style={{ width: `${aiProbability}%` }} />
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between text-sm font-semibold mb-1">
            <span className="text-[#111827]">Real image probability</span>
            <span className="text-[#059669]">{realProbability.toFixed(1)}%</span>
          </div>
          <div className="h-2.5 w-full bg-[#d1fae5] rounded-full overflow-hidden">
            <div className="h-full bg-[#059669]" style={{ width: `${realProbability}%` }} />
          </div>
        </div>
      </div>

      {hasGrok && (
        <div className="w-full max-w-md rounded-xl border border-[#c7d2fe] bg-[#eef2ff] p-4 text-left mb-6">
          <p className="font-bold text-[#3730a3]">Grok cross-check</p>
          <p className="text-sm mt-1 text-[#4338ca]">
            Label: {result.grok.label} ({(result.grok.confidence * 100).toFixed(1)}%)
          </p>
          {result.ensemble && (
            <p className="text-sm mt-1 text-[#4338ca]">
              Ensemble: {result.ensemble.label} ({(result.ensemble.confidence * 100).toFixed(1)}%), agreement: {result.ensemble.agreement ? 'yes' : 'no'}
            </p>
          )}
        </div>
      )}

      <div className={`w-full max-w-md rounded-xl border p-4 text-left mb-8 ${reliability.style}`}>
        <p className="font-bold">{reliability.title}</p>
        <p className="text-sm mt-1">{reliability.desc}</p>
      </div>

      <button
        onClick={onReset}
        className="bg-[#2f80ed] text-white font-semibold py-3 px-8 rounded-full hover:bg-[#1f6dd7] transition-colors duration-200"
      >
        Check another image
      </button>
    </div>
  );
}

export default Result;
