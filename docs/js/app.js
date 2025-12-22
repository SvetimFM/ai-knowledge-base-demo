/**
 * FBI Document Explorer - Shared Utilities
 */

// Global state
let manifestData = null;
let searchCorpus = null;

// HuggingFace dataset URL - PDFs not uploaded, use OCR text instead
const HF_DATASET = 'https://huggingface.co/datasets/svetfm/epstein-fbi-files';
const HF_RAG_SPACE = 'https://svetfm-epstein-fbi-rag.hf.space';
// Note: Original PDFs not hosted - view OCR text in search corpus

/**
 * Load manifest data (cached)
 */
async function loadManifest() {
    if (manifestData) return manifestData;

    try {
        const response = await fetch('data/manifest.json');
        manifestData = await response.json();
        return manifestData;
    } catch (error) {
        console.error('Failed to load manifest:', error);
        throw error;
    }
}

/**
 * Load search corpus (for client-side search)
 */
async function loadSearchCorpus() {
    if (searchCorpus) return searchCorpus;

    try {
        const response = await fetch('data/search-corpus.json');
        searchCorpus = await response.json();
        return searchCorpus;
    } catch (error) {
        console.error('Failed to load search corpus:', error);
        throw error;
    }
}

/**
 * Get PDF URL from HuggingFace dataset
 */
function getPdfUrl(doc) {
    // PDFs hosted on HuggingFace
    const path = doc.path || doc.id;
    return `https://huggingface.co/datasets/svetfm/epstein-fbi-files/resolve/main/pdfs/${path}`;
}

/**
 * Get OCR text for a document from the search corpus
 */
async function getOcrText(docId) {
    const corpus = await loadSearchCorpus();
    const doc = corpus.find(d => d.id === docId);
    return doc ? doc.text : null;
}

/**
 * Filter documents based on criteria
 */
function filterDocuments(docs, filters) {
    return docs.filter(doc => {
        if (filters.category && doc.cat !== filters.category) return false;
        if (filters.volume && doc.vol !== parseInt(filters.volume)) return false;
        if (filters.search) {
            const searchLower = filters.search.toLowerCase();
            if (!doc.id.toLowerCase().includes(searchLower)) return false;
        }
        return true;
    });
}

/**
 * Sort documents
 */
function sortDocuments(docs, sortBy, sortDir = 'asc') {
    const sorted = [...docs];
    sorted.sort((a, b) => {
        let valA = a[sortBy];
        let valB = b[sortBy];

        if (typeof valA === 'string') {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
        }

        if (valA < valB) return sortDir === 'asc' ? -1 : 1;
        if (valA > valB) return sortDir === 'asc' ? 1 : -1;
        return 0;
    });
    return sorted;
}

/**
 * Paginate array
 */
function paginate(items, page, perPage = 50) {
    const start = (page - 1) * perPage;
    return {
        items: items.slice(start, start + perPage),
        totalPages: Math.ceil(items.length / perPage),
        currentPage: page,
        totalItems: items.length,
        startIndex: start + 1,
        endIndex: Math.min(start + perPage, items.length)
    };
}

/**
 * Render pagination controls
 */
function renderPagination(containerId, pagination, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const { currentPage, totalPages } = pagination;

    let html = '';

    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="window.goToPage(${currentPage - 1})">&laquo; Prev</button>`;

    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    if (startPage > 1) {
        html += `<button onclick="window.goToPage(1)">1</button>`;
        if (startPage > 2) html += `<span>...</span>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="window.goToPage(${i})">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<span>...</span>`;
        html += `<button onclick="window.goToPage(${totalPages})">${totalPages}</button>`;
    }

    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="window.goToPage(${currentPage + 1})">Next &raquo;</button>`;

    container.innerHTML = html;

    // Store callback
    window.goToPage = onPageChange;
}

/**
 * Get category badge HTML
 */
function getCategoryBadge(category) {
    const labels = {
        'typed_memo': 'Typed Memo',
        'photograph': 'Photograph',
        'digital_text': 'Digital Text',
        'unknown': 'Unknown'
    };
    return `<span class="badge badge-${category}">${labels[category] || category}</span>`;
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Get URL parameter
 */
function getUrlParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Set URL parameter without reload
 */
function setUrlParam(name, value) {
    const url = new URL(window.location);
    if (value) {
        url.searchParams.set(name, value);
    } else {
        url.searchParams.delete(name);
    }
    window.history.replaceState({}, '', url);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Simple client-side search
 */
function searchDocuments(corpus, query, limit = 50) {
    if (!query || query.length < 2) return [];

    const queryLower = query.toLowerCase();
    const words = queryLower.split(/\s+/).filter(w => w.length > 1);

    const results = [];

    for (const doc of corpus) {
        const textLower = doc.text.toLowerCase();
        const idLower = doc.id.toLowerCase();

        // Check if all words are present
        const allWordsFound = words.every(word =>
            textLower.includes(word) || idLower.includes(word)
        );

        if (allWordsFound) {
            // Find snippet around first match
            const firstWord = words[0];
            const matchIndex = textLower.indexOf(firstWord);
            const snippetStart = Math.max(0, matchIndex - 50);
            const snippetEnd = Math.min(doc.text.length, matchIndex + 150);
            let snippet = doc.text.substring(snippetStart, snippetEnd);

            if (snippetStart > 0) snippet = '...' + snippet;
            if (snippetEnd < doc.text.length) snippet = snippet + '...';

            // Highlight matches
            words.forEach(word => {
                const regex = new RegExp(`(${word})`, 'gi');
                snippet = snippet.replace(regex, '<mark>$1</mark>');
            });

            results.push({
                id: doc.id,
                snippet: snippet,
                score: words.reduce((score, word) => {
                    return score + (textLower.split(word).length - 1);
                }, 0)
            });
        }

        if (results.length >= limit) break;
    }

    // Sort by score
    results.sort((a, b) => b.score - a.score);

    return results;
}

// Export for use in other files
window.app = {
    loadManifest,
    loadSearchCorpus,
    getPdfUrl,
    getOcrText,
    filterDocuments,
    sortDocuments,
    paginate,
    renderPagination,
    getCategoryBadge,
    formatNumber,
    getUrlParam,
    setUrlParam,
    debounce,
    searchDocuments,
    HF_DATASET,
    HF_RAG_SPACE
};
