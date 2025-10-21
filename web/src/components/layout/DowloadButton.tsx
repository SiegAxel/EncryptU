"use client";

import React from 'react';

interface DownloadButtonProps {
    imageUrl: string;
    fileName: string;
    className?: string;
    children: React.ReactNode; // <-- Añade children aquí
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ imageUrl, fileName, className, children }) => { // <-- Recíbelo
    // ... tu función handleDownload no cambia ...
    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <button onClick={handleDownload} className={className}>
            {children} {/* <-- Úsalo aquí en lugar de texto fijo */}
        </button>
    );
};

export default DownloadButton;