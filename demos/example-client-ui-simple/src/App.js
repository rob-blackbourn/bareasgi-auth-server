import React, { Component } from 'react'

import { AuthenticatedApp } from '@barejs/auth-provider'
import Site from './Site'
import config from './config'

class App extends Component {
  render() {
    return (
      <AuthenticatedApp
        loginPath={config.loginPath}
        whoamiPath={config.whoamiPath}
        renderer={props => <Site {...props} />}
      />
    )
  }
}

export default App
