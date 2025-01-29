// main.js

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');

let mainWindow;

app.on('ready', () => {
    mainWindow = new BrowserWindow({
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
    });

    mainWindow.loadFile(path.join(__dirname, 'index.html'));
});

// Handle 'open-file-dialog' from renderer
ipcMain.handle('open-file-dialog', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
        properties: ['openFile', 'multiSelections'],
    });

    if (canceled) {
        return []; // No files selected
    }

    return filePaths; // Return the selected file paths
});

// Handle 'show-input-dialog' from renderer
ipcMain.handle('show-input-dialog', async (event, title) => {
    const { response } = await dialog.showMessageBox({
        type: 'question',
        buttons: ['OK', 'Cancel'],
        title: title,
        message: 'Please provide the input below:',
    });

    if (response === 1) {
        return null; // User canceled
    }

    // Simulating input collection (for actual use, implement a custom input dialog window)
    const input = "UserInputExample"; // Replace with real input handling logic

    return input;
});
