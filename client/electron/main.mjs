import { app, BrowserWindow, shell } from 'electron'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawn } from 'node:child_process'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const isDev = !app.isPackaged
const devServerUrl = process.env.VITE_DEV_SERVER_URL ?? 'http://127.0.0.1:5000'
const rendererEntry = isDev
  ? devServerUrl
  : new URL('../dist/index.html', import.meta.url).toString()

let mainWindow
let backendProcess = null

const startBackend = () => {
  if (isDev) {
    console.log('Running in dev mode, skipping backend spawn (assume running manually)')
    return
  }

  const backendName = process.platform === 'win32' ? 'creditnexus-backend.exe' : 'creditnexus-backend'
  const backendPath = path.join(process.resourcesPath, 'creditnexus-backend', backendName)

  console.log('Starting backend from:', backendPath)

  backendProcess = spawn(backendPath, [], {
    stdio: 'inherit',
    windowsHide: true
  })

  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err)
  })

  backendProcess.on('exit', (code, signal) => {
    console.log(`Backend exited with code ${code} and signal ${signal}`)
  })
}

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 720,
    show: false,
    autoHideMenuBar: true,
    backgroundColor: '#0b111a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
      contextIsolation: true,
      sandbox: false,
    },
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
    if (isDev && process.env.DEBUG_DESKTOP === '1') {
      mainWindow.webContents.openDevTools({ mode: 'detach' })
    }
  })

  mainWindow.loadURL(rendererEntry)

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  if (backendProcess) {
    console.log('Killing backend process...')
    backendProcess.kill()
    backendProcess = null
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(() => {
  startBackend()

  const gotLock = app.requestSingleInstanceLock()
  if (!gotLock) {
    app.quit()
    return
  }

  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })

  createWindow()
})
