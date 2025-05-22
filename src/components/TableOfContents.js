import React, { useMemo } from 'react';

const TableOfContents = ({ data, onItemClick }) => {
    // 使用与 SummarizedDataViewer 相同的排序逻辑
    const sortedThemes = useMemo(() => {
        return Object.entries(data).map(([theme, themeData]) => {
            let totalCount = 0;
            themeData.summary_list?.forEach(summaryItem => {
                summaryItem.points?.forEach(pointItem => {
                    totalCount += pointItem.original_content?.length || 0;
                });
            });
            return { theme, totalCount };
        }).sort((a, b) => b.totalCount - a.totalCount); // 按讨论度降序排序
    }, [data]);

    return (
        <div className="sticky top-4 bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-indigo-700 mb-4 pb-2 border-b border-indigo-200">
                目录
            </h3>
            <nav className="max-h-[calc(100vh-8rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-200 scrollbar-track-gray-100 pr-2">
                <ul className="space-y-2">
                    {sortedThemes.map(({ theme }, index) => {
                        const themeId = theme.replaceAll('*', '').replaceAll(' ', '-');
                        return (
                            <li key={index}>
                                <a
                                    href={`#${themeId}`}
                                    className="block px-3 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out"
                                >
                                    {theme.replaceAll('*', '')}
                                </a>
                            </li>
                        );
                    })}
                </ul>
            </nav>
        </div>
    );
};

export default TableOfContents;