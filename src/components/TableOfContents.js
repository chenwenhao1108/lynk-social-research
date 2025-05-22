import React from 'react';

const TableOfContents = ({ data, onItemClick }) => {
    return (
        <div className="sticky top-4 bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-indigo-700 mb-4 pb-2 border-b border-indigo-200">
                目录
            </h3>
            <nav className="max-h-[calc(100vh-8rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-200 scrollbar-track-gray-100 pr-2">
                <ul className="space-y-2">
                    {Object.keys(data).map((theme, index) => (
                        <li key={theme}>
                            <button
                                onClick={() => onItemClick(theme)}
                                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 rounded-md transition-colors duration-150 ease-in-out cursor-pointer"
                            >
                                {theme.replaceAll('*', '')}
                            </button>
                        </li>
                    ))}
                </ul>
            </nav>
        </div>
    );
};

export default TableOfContents;