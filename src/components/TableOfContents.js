import React, { useMemo } from "react";

const TableOfContents = ({ data }) => {
  const sortedThemes = useMemo(() => {
    return Object.entries(data).map(([theme, themeData]) => {
      let totalCount = 0;
      themeData.summary_list?.forEach((summaryItem) => {
        summaryItem.points?.forEach((pointItem) => {
          totalCount += pointItem.original_content?.length || 0;
        });
      });
      const sortedSummaryList = themeData.summary_list
        ? [...themeData.summary_list].sort((a, b) => {
            let aContentCount = 0;
            a.points?.forEach((p) => {
              aContentCount += p.original_content?.length || 0;
            });

            let bContentCount = 0;
            b.points?.forEach((p) => {
              bContentCount += p.original_content?.length || 0;
            });

            const aPercentage = totalCount > 0 ? aContentCount / totalCount : 0;
            const bPercentage = totalCount > 0 ? bContentCount / totalCount : 0;

            return bPercentage - aPercentage; // 降序排序
          })
        : [];

      return { theme, summaries: sortedSummaryList };
    });
  }, [data]);

  return (
    <div className="sticky top-4 bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-indigo-700 mb-4 pb-2 border-b border-indigo-200">
        目录
      </h3>
      <nav className="max-h-[calc(100vh-8rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-200 scrollbar-track-gray-100 pr-2">
        <ul className="space-y-2">
          <li className="space-y-1">
            <a
              href="#totalAnalysis"
              className="block px-3 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out font-medium"
            >
              总体分析
            </a>
          </li>
          <li className="space-y-1">
            <a
              href="#suggestion"
              className="block px-3 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out font-medium"
            >
              决策建议
            </a>
          </li>
          {sortedThemes.map(({ theme, summaries }, themeIndex) => {
            const themeId = theme.replaceAll("*", "").replaceAll(" ", "-");
            return (
              <li key={themeIndex} className="space-y-1">
                <a
                  href={`#${themeId}`}
                  className="block px-3 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out font-medium"
                >
                  {theme.replaceAll("*", "")}
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
