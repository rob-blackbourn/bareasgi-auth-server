import React, { Component } from 'react'
import PropTypes from 'prop-types'

import AuthenticationConsumer from './AuthenticationConsumer'
import AuthenticationProvider from './AuthenticationProvider'

class AuthenticatedApp extends Component {
  render() {
    const { loginPath, whoamiPath, renderer } = this.props
    return (
      <AuthenticationProvider
        loginPath={loginPath}
        whoamiPath={whoamiPath}
      >
        <AuthenticationConsumer>
          {renderer}
        </AuthenticationConsumer>
      </AuthenticationProvider>
    )
  }
}

AuthenticatedApp.propTypes = {
  loginPath: PropTypes.string.isRequired,
  whoamiPath: PropTypes.string.isRequired,
  renderer: PropTypes.func.isRequired
}

export default AuthenticatedApp
