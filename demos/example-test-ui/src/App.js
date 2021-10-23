import React, { Component } from 'react'
import { AuthenticationProvider, AuthenticationConsumer } from './auth'
import AuthenticatedApp from './AuthenticatedApp'
import config from './config'

class App extends Component {
  render() {
    return (
      <AuthenticationProvider
        host={window.location.host}
        path={config.loginPath}
      >
        <AuthenticationConsumer>
          {authenticator => <AuthenticatedApp authenticator={authenticator} />}
        </AuthenticationConsumer>
      </AuthenticationProvider>
    )
  }
}

export default App
