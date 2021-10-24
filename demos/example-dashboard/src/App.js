import React, { Component } from 'react'

import { createTheme, ThemeProvider } from '@mui/material/styles'

import { AuthenticatedApp } from './components'
import Site from './Site'
import config from './config'

const theme = createTheme()

class App extends Component {
  render() {
    return (
      <ThemeProvider theme={theme}>
        <AuthenticatedApp
          loginPath={config.loginPath}
          whoamiPath={config.whoamiPath}
          renderer={props => <Site {...props} />}
        />
      </ThemeProvider>
    )
  }
}

export default App
