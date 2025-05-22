import React, { useMemo } from 'react';

const TableOfContents = ({ data }) => {
    const sortedThemes = useMemo(() => {
        return Object.entries(data).map(([theme, themeData]) => {
            let totalCount = 0;
            const summaries = themeData.summary_list?.map((summaryItem, index) => {
                let summaryCount = 0;
                summaryItem.points?.forEach(pointItem => {
                    summaryCount += pointItem.original_content?.length || 0;
                });
                totalCount += summaryCount;
                return { summary: summaryItem.summary, count: summaryCount, index };
            }) || [];
            return { theme, summaries, totalCount };
        }).sort((a, b) => b.totalCount - a.totalCount);
    }, [data]);

    return (
        <div className="sticky top-4 bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-indigo-700 mb-4 pb-2 border-b border-indigo-200">
                目录
            </h3>
            <nav className="max-h-[calc(100vh-8rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-200 scrollbar-track-gray-100 pr-2">
                <ul className="space-y-2">
                    {sortedThemes.map(({ theme, summaries }, themeIndex) => {
                        const themeId = theme.replaceAll('*', '').replaceAll(' ', '-');
                        return (
                            <li key={themeIndex} className="space-y-1">
                                <a
                                    href={`#${themeId}`}
                                    className="block px-3 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out font-medium"
                                >
                                    {theme.replaceAll('*', '')}
                                </a>
                                <ul className="pl-6 space-y-1">
                                    {summaries.map((summary, summaryIndex) => (
                                        <li key={summaryIndex}>
                                            <a
                                                href={`#${themeId}-${summary.summary}`}
                                                className="block px-3 py-1 text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out"
                                            >
                                                {summary.summary}
                                            </a>
                                        </li>
                                    ))}
                                </ul>
                            </li>
                        );
                    })}
                </ul>
            </nav>
        </div>
    );
};

export default TableOfContents;