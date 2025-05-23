// src/app/page.js (或者任何你想展示数据的页面)
"use client";
import SummarizedDataViewer from "../components/SummarizedDataViewer"; // 调整路径
import jsonData from "../../analyze/analyze_results/merged_summarized.json";

export default function HomePage() {
  if (!jsonData) {
    return (
      <p className="text-center text-red-600 p-8">加载数据失败: {error}</p>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-center text-gray-800">
          领克900社媒聆听分析报告
        </h1>
      </header>
      <main className="w-full">
        <SummarizedDataViewer data={jsonData} />
      </main>
    </div>
  );
}
