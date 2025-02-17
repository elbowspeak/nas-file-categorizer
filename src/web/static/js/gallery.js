// Load and process categories
async function loadCategories() {
    try {
        const categories = new Set();
        state.allImages.forEach(image => {
            const category = image.file_info.path.split('/')[0];
            categories.add(category);
        });

        const categoryFilters = document.getElementById('category-filters');
        categoryFilters.innerHTML = Array.from(categories).map(category => `
            <button
                class="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 transition-all"
                onclick="toggleFilter('${category}')"
                data-category="${category}">
                ${category}
            </button>
        `).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadImages(category = null) {
    try {
        const url = category ? `/api/images?category=${category}` : '/api/images';
        const response = await fetch(url);
        const images = await response.json();
        // Update UI with images
        return images;
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

// Handle sorting
function handleSort() {
    const criteria = document.getElementById('sort-select').value;
    applyFiltersAndSort(criteria);
}

// Apply filters and sorting
function applyFiltersAndSort(sortCriteria) {
    let filtered = [...state.allImages];

    // Apply category filters
    if (state.activeFilters.size > 0) {
        filtered = filtered.filter(image => {
            const category = image.file_info.path.split('/')[0];
            return state.activeFilters.has(category);
        });
    }

    // Apply sorting
    if (sortCriteria) {
        filtered.sort((a, b) => {
            switch (sortCriteria) {
                case 'date':
                    return b.file_info.modified - a.file_info.modified;
                case 'name':
                    return a.file_info.name.localeCompare(b.file_info.name);
                case 'size':
                    return b.file_info.size - a.file_info.size;
                default:
                    return 0;
            }
        });
    }

    state.filteredImages = filtered;
    displayImages(filtered);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadCategories();
    await loadImages();
});