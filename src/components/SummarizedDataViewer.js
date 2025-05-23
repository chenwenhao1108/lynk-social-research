// src/components/SummarizedDataViewer.js
"use client"
import React, { useState, useMemo, } from 'react'; // 引入 useMemo
import TableOfContents from './TableOfContents';

const SummarizedDataViewer = ({ data }) => {
    const [expandedPoints, setExpandedPoints] = useState({});

    if (!data || Object.keys(data).length === 0) {
        return <p className="text-gray-600 text-lg p-4">暂无数据可展示。</p>;
    }

    const toggleExpandPoint = (themeIndex, originalSummaryIndex, pointIndex) => {
        const key = `${themeIndex}-${originalSummaryIndex}-${pointIndex}`
        setExpandedPoints(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    // 使用 useMemo 优化排序和计算过程，仅当 data 变化时重新计算
    const processedData = useMemo(() => {
        return Object.entries(data).map(([theme, themeData]) => {
            let themeTotalOriginalContentCount = 0;
            themeData.summary_list?.forEach(summaryItem => {
                summaryItem.points?.forEach(pointItem => {
                    themeTotalOriginalContentCount += pointItem.original_content?.length || 0;
                });
            });

            const sortedSummaryList = themeData.summary_list
                ? [...themeData.summary_list].sort((a, b) => {
                    let aContentCount = 0;
                    a.points?.forEach(p => { aContentCount += p.original_content?.length || 0; });
                    
                    let bContentCount = 0;
                    b.points?.forEach(p => { bContentCount += p.original_content?.length || 0; });

                    const aPercentage = themeTotalOriginalContentCount > 0 ? (aContentCount / themeTotalOriginalContentCount) : 0;
                    const bPercentage = themeTotalOriginalContentCount > 0 ? (bContentCount / themeTotalOriginalContentCount) : 0;
                    
                    return bPercentage - aPercentage; // 降序排序
                  })
                : [];

            return { theme, themeData: { ...themeData, summary_list: sortedSummaryList }, themeTotalOriginalContentCount };
        });
    }, [data]);

    return (
        <div className="flex gap-6">
            <div className="hidden lg:block w-64 flex-shrink-0">
                <TableOfContents data={data} />
            </div>
            <div className="font-sans text-gray-800 bg-gray-50 rounded-lg shadow-lg grid grid-cols-1 md:grid-cols-2 w-full gap-6 p-6">
                {processedData.map(({ theme, themeData, themeTotalOriginalContentCount }, themeIndex) => {
                    // 将主题名称转换为有效的 HTML id
                    const themeId = theme.replaceAll('*', '').replaceAll(' ', '-');
                    return (
                        <div key={theme} id={themeId} className="mb-8 p-6 bg-white border border-gray-200 rounded-md shadow-sm flex flex-col">
                            <h2 className="text-2xl font-bold text-indigo-700 mb-6 pb-3 border-b-2 border-indigo-500">
                                {theme.replaceAll('*', '')}
                            </h2>
                        <div className="flex-grow">
                            {themeData.summary_list && themeData.summary_list.length > 0 ? (
                                themeData.summary_list.map((summaryItem, summaryIndex) => {
                                    const summaryId = `${themeId}-${summaryItem.summary}`;
                                    let summaryOriginalContentCount = 0;
                                    summaryItem.points?.forEach(pointItem => {
                                        summaryOriginalContentCount += pointItem.original_content?.length || 0;
                                    });

                                    const discussionPercentage = themeTotalOriginalContentCount > 0 
                                        ? ((summaryOriginalContentCount / themeTotalOriginalContentCount) * 100).toFixed(2)
                                        : 0;
                                    const originalSummaryIndex = data[theme].summary_list.findIndex(s => s.summary === summaryItem.summary); 

                                    return (
                                        <div key={summaryIndex} id={summaryId} className="mb-6 p-4 bg-indigo-50 border-l-4 border-indigo-500 rounded-r-md">
                                            <div className="flex justify-between items-start mb-3">
                                                <h3 className="text-xl font-semibold text-indigo-600 flex-1 break-words">
                                                    {summaryItem.summary}
                                                </h3>
                                                {themeTotalOriginalContentCount > 0 && (
                                                    <span className="ml-4 px-2 py-1 text-xs font-semibold text-indigo-700 bg-indigo-200 rounded-full whitespace-nowrap">
                                                        讨论度: {discussionPercentage}%
                                                    </span>
                                                )}
                                            </div>
                                            {summaryItem.points && summaryItem.points.length > 0 ? (
                                                <ul className="list-none pl-0">
                                                    {summaryItem.points.map((pointItem, pointIndex) => {
                                                        const pointKey = `${themeIndex}-${originalSummaryIndex}-${pointIndex}`;
                                                        const isExpanded = !!expandedPoints[pointKey];
                                                        const displayContents = isExpanded 
                                                            ? pointItem.original_content 
                                                            : pointItem.original_content?.slice(0, 2) || [];

                                                        return (
                                                            <li key={pointIndex} className="mb-4 p-3 bg-white border border-gray-300 rounded-md shadow-xs">
                                                                <p className="text-base text-gray-700 mb-2 break-words">
                                                                    <strong className="font-medium text-gray-900">要点：</strong> {pointItem.point}
                                                                </p>
                                                                {pointItem.original_content && pointItem.original_content.length > 0 && (
                                                                    <div className="mt-2 pl-4 border-l-2 border-gray-300">
                                                                        <p className="text-sm font-medium text-gray-700 mb-1">
                                                                            <strong>典型用户原声 ({pointItem.original_content.length})：</strong>
                                                                        </p>
                                                                        <ul className="list-disc pl-5 space-y-1">
                                                                            {displayContents.map((content, contentIndex) => (
                                                                                <li key={contentIndex} className="text-sm text-gray-600 leading-relaxed break-words">
                                                                                    {content}
                                                                                </li>
                                                                            ))}
                                                                        </ul>
                                                                        {pointItem.original_content.length > 2 && (
                                                                            <button 
                                                                                onClick={() => toggleExpandPoint(themeIndex, originalSummaryIndex, pointIndex)}
                                                                                className="mt-2 text-xs text-indigo-600 hover:text-indigo-800 font-medium focus:outline-none
                                                                                cursor-pointer"
                                                                            >
                                                                                {isExpanded ? '收起' : `...等 ${pointItem.original_content.length - 2} 条更多`}
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                )}
                                                            </li>
                                                        );
                                                    })}
                                                </ul>
                                            ) : (
                                                <p className="text-gray-500 italic">该总结下无具体要点。</p>
                                            )}
                                        </div>
                                    );
                                })
                            ) : (
                                <p className="text-gray-500 italic">该主题下无总结内容。</p>
                            )}
                        </div>
                    </div>
                );
            })}
            <div className="mb-8 p-6 bg-white border border-gray-200 rounded-md shadow-sm flex flex-col">
                        <h2 className="text-2xl font-bold text-indigo-700 mb-6 pb-3 border-b-2 border-indigo-500">
                        用户在考虑领克900时，对比的竞品车型有哪些；
                        </h2>
                        <div className="flex-grow">
                                        <div className="mb-6 p-4 bg-indigo-50 border-l-4 border-indigo-500 rounded-r-md">
                                            <div className="flex justify-between items-start mb-3">
                                                <h3 className="text-xl font-semibold text-indigo-600 flex-1 break-words">
                                                    竞品车型：
                                                </h3>
                                            </div>
                                                <ul className="list-none pl-0">
                                                            <li className="mb-4 p-3 bg-white border border-gray-300 rounded-md shadow-xs">
                                                                <p className="text-base text-gray-700 mb-2 break-words">
                                                                    <strong className="font-medium text-gray-900">深蓝S09，蓝山，极氪9x，问界M8，理想L9，腾势N9</strong>
                                                                </p>
                                                            </li>
                                                </ul>
                                        </div>
                        </div>
                    </div>
        </div>
        </div>
    );
};

export default SummarizedDataViewer;