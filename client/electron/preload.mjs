import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('creditnexus', {
  env: {
    isDesktop: true,
  },
})
