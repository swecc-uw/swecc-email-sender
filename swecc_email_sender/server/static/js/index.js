// State management
const state = {
  currentPreviewIndex: 0,
  totalRows: 0,
  settings: {},
  validationResults: null
}

const elements = {
  // forms and inputs
  settingsForm: document.getElementById('settingsForm'),
  apiKeyInput: document.getElementById('apiKey'),
  fromEmailInput: document.getElementById('fromEmail'),
  subjectInput: document.getElementById('subject'),
  isMarkdownInput: document.getElementById('isMarkdown'),
  emailContentInput: document.getElementById('emailContent'),
  saveContentBtn: document.getElementById('saveContent'),
  templateForm: document.getElementById('templateForm'),
  templateFileInput: document.getElementById('templateFile'),
  dataForm: document.getElementById('dataForm'),
  dataFileInput: document.getElementById('dataFile'),
  dataStats: document.getElementById('dataStats'),

  // preview nav
  prevEmailBtn: document.getElementById('prevEmail'),
  nextEmailBtn: document.getElementById('nextEmail'),
  emailCounter: document.getElementById('emailCounter'),

  // preview content
  previewLoading: document.getElementById('previewLoading'),
  previewEmail: document.getElementById('previewEmail'),
  previewTo: document.getElementById('previewTo'),
  previewFrom: document.getElementById('previewFrom'),
  previewSubject: document.getElementById('previewSubject'),
  previewFrame: document.getElementById('previewFrame'),
  previewRaw: document.getElementById('previewRaw'),
  dataTable: document.getElementById('dataTable').querySelector('tbody'),

  // tabs
  tabButtons: document.querySelectorAll('.tab-btn'),

  // actions
  previewBtn: document.getElementById('previewBtn'),
  validateBtn: document.getElementById('validateBtn'),

  // validation
  validationResults: document.getElementById('validationResults'),
  validationSummary: document.getElementById('validationSummary'),
  validationTable: document.getElementById('validationTable'),

  // modal
  showCliCommandBtn: document.getElementById('showCliCommand'),
  commandModal: document.getElementById('commandModal'),
  closeModalBtn: document.querySelector('.close'),
  cliCommand: document.getElementById('cliCommand'),
  copyCommandBtn: document.getElementById('copyCommand'),

  // notifications
  notifications: document.getElementById('notifications')
}

// tab switching
elements.tabButtons.forEach(button => {
  button.addEventListener('click', () => {
    const tabGroup = button.closest('.tabs')
    const tabContentId = button.dataset.tab

    // deactivate all tabs in this group
    tabGroup.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active')
    })

    // hide all tab content for this group
    const tabContents = tabGroup.parentElement.querySelectorAll('.tab-content')
    tabContents.forEach(content => {
      content.classList.remove('active')
    })

    // activate the clicked tab
    button.classList.add('active')
    document.getElementById(tabContentId).classList.add('active')
  })
})

const api = {
  async getState () {
    const response = await fetch('/api/state')
    return response.json()
  },

  async updateSettings (settings) {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    })
    return response.json()
  },

  async uploadData (formData) {
    const response = await fetch('/api/upload/data', {
      method: 'POST',
      body: formData
    })
    return response.json()
  },

  async uploadTemplate (formData) {
    const response = await fetch('/api/upload/template', {
      method: 'POST',
      body: formData
    })
    return response.json()
  },

  async previewEmail (rowIndex = 0) {
    const response = await fetch(`/api/preview?row_index=${rowIndex}`)
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to preview email')
    }
    return response.json()
  },

  async validateTemplate () {
    const response = await fetch('/api/validate')
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to validate template')
    }
    return response.json()
  }
}

// UI updates
const ui = {
  showNotification (message, type = 'info') {
    const notification = document.createElement('div')
    notification.className = 'notification'
    notification.textContent = message

    elements.notifications.appendChild(notification)

    // remove after 4 seconds
    setTimeout(() => {
      notification.style.opacity = '0'
      setTimeout(() => {
        elements.notifications.removeChild(notification)
      }, 300)
    }, 4000)
  },

  updatePreviewNavigation () {
    elements.prevEmailBtn.disabled = state.currentPreviewIndex <= 0
    elements.nextEmailBtn.disabled =
      state.currentPreviewIndex >= state.totalRows - 1
    elements.emailCounter.textContent =
      state.totalRows > 0
        ? `Email ${state.currentPreviewIndex + 1} of ${state.totalRows}`
        : 'No data loaded'
  },

  updateDataStats (rows) {
    state.totalRows = rows
    elements.dataStats.textContent = `${rows} data rows loaded`
    this.updatePreviewNavigation()
  },

  async updatePreview (rowIndex = 0) {
    try {
      elements.previewLoading.classList.remove('hidden')
      elements.previewEmail.classList.add('hidden')
      elements.validationResults.classList.add('hidden')

      const previewData = await api.previewEmail(rowIndex)

      state.currentPreviewIndex = rowIndex
      state.totalRows = previewData.total_rows

      elements.previewTo.textContent = previewData.to_email
      elements.previewFrom.textContent = previewData.from_email
      elements.previewSubject.textContent = previewData.subject

      elements.previewRaw.textContent = previewData.content

      const doc = elements.previewFrame.contentDocument
      doc.open()
      doc.write(previewData.html_content)
      doc.close()

      elements.dataTable.innerHTML = ''
      for (const [key, value] of Object.entries(previewData.data_row)) {
        const row = document.createElement('tr')
        const keyCell = document.createElement('td')
        const valueCell = document.createElement('td')

        keyCell.textContent = key
        valueCell.textContent = value

        row.appendChild(keyCell)
        row.appendChild(valueCell)
        elements.dataTable.appendChild(row)
      }

      elements.previewLoading.classList.add('hidden')
      elements.previewEmail.classList.remove('hidden')

      this.updatePreviewNavigation()
    } catch (error) {
      this.showNotification(error.message)
      console.error('Preview error:', error)
    }
  },

  async showValidationResults () {
    try {
      elements.previewLoading.classList.remove('hidden')
      elements.previewEmail.classList.add('hidden')
      elements.validationResults.classList.add('hidden')

      const results = await api.validateTemplate()
      state.validationResults = results

      elements.validationSummary.innerHTML = `
              <p><strong>Total rows:</strong> ${results.total_rows}</p>
              <p><strong>Valid:</strong> ${results.total_valid}</p>
              <p><strong>Invalid:</strong> ${results.total_invalid}</p>
          `

      elements.validationTable.innerHTML = ''
      results.validation_results.forEach(result => {
        const row = document.createElement('tr')

        const indexCell = document.createElement('td')
        indexCell.textContent = result.row_index + 1

        const emailCell = document.createElement('td')
        emailCell.textContent = result.to_email

        const statusCell = document.createElement('td')
        statusCell.textContent = result.has_errors ? 'Invalid' : 'Valid'

        const missingCell = document.createElement('td')
        const missingVars = []
        if (result.missing_keys.length > 0) {
          missingVars.push(
            ...result.missing_keys.map(key => `${key} (content)`)
          )
        }
        if (result.missing_subject_keys.length > 0) {
          missingVars.push(
            ...result.missing_subject_keys.map(key => `${key} (subject)`)
          )
        }
        missingCell.textContent = missingVars.join(', ') || 'None'

        row.appendChild(indexCell)
        row.appendChild(emailCell)
        row.appendChild(statusCell)
        row.appendChild(missingCell)

        elements.validationTable.appendChild(row)
      })

      elements.previewLoading.classList.add('hidden')
      elements.validationResults.classList.remove('hidden')
    } catch (error) {
      this.showNotification(error.message)
      console.error('Validation error:', error)
    }
  },

  generateCliCommand () {
    const command = 'TODO: We still need to implement this...'

    return command
  },

  showCliCommand () {
    elements.cliCommand.textContent = this.generateCliCommand()
    elements.commandModal.classList.remove('hidden')
  },

  hideCliCommand () {
    elements.commandModal.classList.add('hidden')
  },

  copyCliCommand () {
    navigator.clipboard
      .writeText(elements.cliCommand.textContent)
      .then(() => {
        this.showNotification('Command copied to clipboard')
      })
      .catch(err => {
        console.error('Could not copy text: ', err)
        this.showNotification('Failed to copy command')
      })
  },

  async loadInitialState () {
    try {
      const serverState = await api.getState()

      if (serverState.from_email) elements.fromEmailInput.value = serverState.from_email

      if (serverState.subject) elements.subjectInput.value = serverState.subject

      if (serverState.is_markdown) elements.isMarkdownInput.checked = serverState.is_markdown

      if (serverState.content) elements.emailContentInput.value = serverState.content

      if (serverState.has_data && serverState.data) this.updateDataStats(serverState.data.length)

      state.settings = serverState

      this.showNotification('Settings loaded from server')
    } catch (error) {
      console.error('Error loading initial state:', error)
      this.showNotification('Failed to load initial state')
    }
  }
}

// event handlers
function setupEventListeners () {
  elements.settingsForm.addEventListener('submit', async e => {
    e.preventDefault()
    try {
      await api.updateSettings({
        api_key: elements.apiKeyInput.value,
        from_email: elements.fromEmailInput.value,
        subject: elements.subjectInput.value,
        is_markdown: elements.isMarkdownInput.checked
      })
      ui.showNotification('Settings saved')
    } catch (error) {
      ui.showNotification(error.message)
    }
  })

  elements.saveContentBtn.addEventListener('click', async () => {
    try {
      await api.updateSettings({
        content: elements.emailContentInput.value
      })
      ui.showNotification('Content saved')
    } catch (error) {
      ui.showNotification(error.message)
    }
  })

  elements.templateForm.addEventListener('submit', async e => {
    e.preventDefault()

    if (!elements.templateFileInput.files[0]) {
      ui.showNotification('Please select a template file')
      return
    }

    const formData = new FormData()
    formData.append('file', elements.templateFileInput.files[0])

    try {
      const result = await api.uploadTemplate(formData)
      elements.emailContentInput.value = result.content
      ui.showNotification('Template uploaded successfully')
    } catch (error) {
      ui.showNotification(error.message)
    }
  })

  elements.dataForm.addEventListener('submit', async e => {
    e.preventDefault()

    if (!elements.dataFileInput.files[0]) {
      ui.showNotification('Please select a data file')
      return
    }

    const formData = new FormData()
    formData.append('file', elements.dataFileInput.files[0])

    try {
      const result = await api.uploadData(formData)
      ui.updateDataStats(result.rows)
      ui.showNotification(`${result.rows} data rows loaded`)
    } catch (error) {
      ui.showNotification(error.message)
    }
  })

  elements.prevEmailBtn.addEventListener('click', () => {
    if (state.currentPreviewIndex > 0) {
      ui.updatePreview(state.currentPreviewIndex - 1)
    }
  })

  elements.nextEmailBtn.addEventListener('click', () => {
    if (state.currentPreviewIndex < state.totalRows - 1) {
      ui.updatePreview(state.currentPreviewIndex + 1)
    }
  })

  elements.previewBtn.addEventListener('click', () => {
    ui.updatePreview(state.currentPreviewIndex)
  })

  elements.validateBtn.addEventListener('click', () => {
    ui.showValidationResults()
  })

  elements.showCliCommandBtn.addEventListener('click', e => {
    e.preventDefault()
    ui.showCliCommand()
  })

  elements.closeModalBtn.addEventListener('click', () => {
    ui.hideCliCommand()
  })

  elements.copyCommandBtn.addEventListener('click', () => {
    ui.copyCliCommand()
  })

  window.addEventListener('click', e => {
    if (e.target === elements.commandModal) {
      ui.hideCliCommand()
    }
  })
}

async function init () {
  setupEventListeners()
  await ui.loadInitialState()
}

document.addEventListener('DOMContentLoaded', init)
