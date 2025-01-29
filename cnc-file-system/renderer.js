// renderer.js

const fs = require('fs');
const path = require('path');
const { ipcRenderer } = require('electron'); // Use ipcRenderer to communicate with main process
const { shell } = require('electron'); // Import shell module to open files

console.log('Modules loaded successfully!');

// Base directory
const baseDir = path.join(__dirname, 'files');
let currentSelectedFolder = baseDir; // Track currently selected folder
let currentSelectedFile = null; // Track currently selected file
console.log('Loading folder tree for base directory:', baseDir);

// Function to create a folder tree
function createFolderTree(directory, parentElement) {
    try {
        const items = fs.readdirSync(directory); // Correct usage of fs.readdirSync

        items.forEach(item => {
            const fullPath = path.join(directory, item);
            const li = document.createElement('li');
            li.classList.add('folder-item'); // Add CSS class for styling

            if (fs.statSync(fullPath).isDirectory()) {
                li.textContent = `📁 ${item}`; // Folder icon

                // Add click event to select folder and toggle content visibility
                li.addEventListener('click', (event) => {
                    event.stopPropagation(); // Prevent parent folder from toggling
                    currentSelectedFolder = fullPath;
                    currentSelectedFile = null; // Clear file selection
                    console.log('Selected folder:', currentSelectedFolder);

                    const ul = li.querySelector('ul');
                    if (ul) {
                        ul.style.display = ul.style.display === 'none' ? 'block' : 'none';
                    } else {
                        // If the folder is empty, ensure it is still selectable
                        console.log('Empty folder selected:', currentSelectedFolder);
                    }
                });

                const ul = document.createElement('ul');
                ul.style.display = 'none'; // Initially hide folder content
                ul.classList.add('child-folder'); // Add CSS class for styling

                if (fs.readdirSync(fullPath).length > 0) {
                    createFolderTree(fullPath, ul);
                } else {
                    // Add "Empty" label for empty folders
                    const emptyLabel = document.createElement('li');
                    emptyLabel.textContent = 'Empty';
                    emptyLabel.classList.add('empty-folder-label'); // CSS class for styling
                    ul.appendChild(emptyLabel);
                }

                li.appendChild(ul);
            } else {
                li.textContent = `📄 ${item}`; // File icon

                // Add right-click event for file options
                li.addEventListener('contextmenu', (event) => {
                    event.preventDefault();
                    currentSelectedFile = fullPath;
                    console.log('Right-clicked on file:', currentSelectedFile);
                    showFileContextMenu(event);
                });

                // Add double-click event to open the file in the viewer pane
                li.addEventListener('dblclick', (event) => {
                    event.stopPropagation();
                    console.log('Double-click detected on file:', fullPath);
                    openFileInViewer(fullPath);
                });

                // Prevent single click on files from toggling folders
                li.addEventListener('click', (event) => {
                    event.stopPropagation(); // Ignore click events on files
                });
            }

            parentElement.appendChild(li);
        });
    } catch (error) {
        console.error(`Error reading directory ${directory}:`, error.message);
    }
}

// Function to show file context menu
function showFileContextMenu(event) {
    const contextMenu = document.getElementById('file-context-menu');
    contextMenu.style.top = `${event.clientY}px`;
    contextMenu.style.left = `${event.clientX}px`;
    contextMenu.style.display = 'block';

    // Hide the context menu when clicking anywhere else
    document.addEventListener('click', () => {
        contextMenu.style.display = 'none';
    }, { once: true });
}

// Function to open files in the viewer pane
function openFileInViewer(filePath) {
    const viewerPane = document.getElementById('file-viewer');
    viewerPane.innerHTML = ''; // Clear previous content

    console.log('Opening file in viewer:', filePath); // Debugging log

    try {
        if (filePath.endsWith('.txt')) {
            // Display text files
            const textContent = fs.readFileSync(filePath, 'utf8');
            console.log('Text file content:', textContent); // Debugging log
            const pre = document.createElement('pre');
            pre.textContent = textContent;
            pre.classList.add('text-viewer'); // Add CSS class for styling
            viewerPane.appendChild(pre);
        } else if (filePath.endsWith('.pdf')) {
            // Display PDF files using an iframe
            const iframe = document.createElement('iframe');
            iframe.src = filePath;
            iframe.classList.add('pdf-viewer'); // Add CSS class for styling
            iframe.style.width = '100%'; // Adjust to fit the width of the viewer
            iframe.style.height = '100%'; // Adjust to fit the height of the viewer
            viewerPane.appendChild(iframe);
        } else {
            viewerPane.textContent = 'Unsupported file type.';
        }
    } catch (error) {
        console.error('Error opening file:', error.message); // Log error
        viewerPane.textContent = 'Error loading file. Please try again.';
    }
}

// Function to add a folder
function addFolder() {
    ipcRenderer.invoke('show-input-dialog', 'Create New Folder').then(folderName => {
        if (!folderName) {
            alert('Folder name cannot be empty.');
            return;
        }

        const newFolderPath = path.join(currentSelectedFolder, folderName);

        if (fs.existsSync(newFolderPath)) {
            alert('A folder with this name already exists.');
            return;
        }

        try {
            fs.mkdirSync(newFolderPath);
            console.log('Folder created:', newFolderPath);
            refreshFolderTree();
        } catch (error) {
            console.error('Error creating folder:', error.message);
            alert('Failed to create folder. Please try again.');
        }
    });
}

// Function to remove a folder
function removeFolder() {
    if (!fs.existsSync(currentSelectedFolder)) {
        alert('No folder selected to remove.');
        return;
    }

    const confirmation = confirm('Are you sure you want to delete this folder and all its contents?');
    if (!confirmation) return;

    try {
        fs.rmdirSync(currentSelectedFolder, { recursive: true });
        console.log('Folder removed:', currentSelectedFolder);
        currentSelectedFolder = baseDir; // Reset to base directory
        refreshFolderTree();
    } catch (error) {
        console.error('Error removing folder:', error.message);
        alert('Failed to remove folder. Please try again.');
    }
}

// Function to rename an item (file or folder)
function renameItem() {
    const itemToRename = currentSelectedFile || currentSelectedFolder;

    if (!itemToRename || !fs.existsSync(itemToRename)) {
        alert('No item selected to rename.');
        return;
    }

    ipcRenderer.invoke('show-input-dialog', 'Rename Item').then(newName => {
        if (!newName) {
            alert('Name cannot be empty.');
            return;
        }

        const parentDir = path.dirname(itemToRename);
        const newPath = path.join(parentDir, newName);

        if (fs.existsSync(newPath)) {
            alert('An item with this name already exists.');
            return;
        }

        try {
            fs.renameSync(itemToRename, newPath);
            console.log('Item renamed to:', newPath);
            refreshFolderTree();
        } catch (error) {
            console.error('Error renaming item:', error.message);
            alert('Failed to rename item. Please try again.');
        }
    });
}

// Function to upload a file
function uploadFile() {
    ipcRenderer.invoke('open-file-dialog').then(filePaths => {
        if (!filePaths || filePaths.length === 0) {
            alert('No file selected for upload.');
            return;
        }

        try {
            filePaths.forEach(filePath => {
                const fileName = path.basename(filePath);
                const destinationPath = path.join(currentSelectedFolder, fileName);

                if (fs.existsSync(destinationPath)) {
                    alert(`File "${fileName}" already exists in the selected folder.`);
                    return;
                }

                fs.copyFileSync(filePath, destinationPath);
                console.log('File uploaded:', destinationPath);
            });
            refreshFolderTree();
        } catch (error) {
            console.error('Error uploading file:', error.message);
            alert('Failed to upload file. Please try again.');
        }
    });
}

// Function to refresh the folder tree
function refreshFolderTree() {
    const folderTreeContainer = document.getElementById('folder-tree');
    folderTreeContainer.innerHTML = ''; // Clear existing tree
    const ul = document.createElement('ul');
    createFolderTree(baseDir, ul);
    folderTreeContainer.appendChild(ul);
}

// Rendering the folder tree
const folderTreeContainer = document.getElementById('folder-tree');
const ul = document.createElement('ul');
createFolderTree(baseDir, ul);
folderTreeContainer.appendChild(ul);

// Initialize file viewer pane
const viewerContainer = document.getElementById('file-viewer');
viewerContainer.classList.add('file-viewer-container'); // Add CSS class for styling
viewerContainer.textContent = 'Select a file to view its contents.';

// Attach event listeners for menu options
document.querySelector('.menu-bar .submenu li:nth-child(1)').addEventListener('click', addFolder); // Add Folder
document.querySelector('.menu-bar .submenu li:nth-child(2)').addEventListener('click', removeFolder); // Remove Folder
document.querySelector('.menu-bar .submenu li:nth-child(3)').addEventListener('click', renameItem); // Rename Item
const uploadButton = document.getElementById('upload-file-btn');
uploadButton.addEventListener('click', uploadFile);

// Attach context menu actions
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('rename-file').addEventListener('click', renameFile);
    document.getElementById('delete-file').addEventListener('click', deleteFile);
    document.getElementById('move-file').addEventListener('click', moveFile);
});

