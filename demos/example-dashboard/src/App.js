import React, { Component } from 'react'
import { AuthenticationProvider, AuthenticationConsumer } from './auth'
import AuthenticatingApp from './AuthenticatingApp'
import config from './config'

class App extends Component {
  render() {
    return (
      <AuthenticationProvider
        host={window.location.host}
        loginPath={config.loginPath}
        whoamiPath={config.whoamiPath}
      >
        <AuthenticationConsumer>
          {authenticator => <AuthenticatingApp authenticator={authenticator} />}
        </AuthenticationConsumer>
      </AuthenticationProvider>
    )
  }
}

export default App
