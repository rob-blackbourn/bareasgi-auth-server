import React, { Component } from 'react'
import PropTypes from 'prop-types'

import AuthenticationContext from './AuthenticationContext'

class Authenticator {
  constructor(host, loginPath, whoamiPath) {
    this.host = host
    this.loginPath = loginPath
    this.whoamiPath = whoamiPath
  }

  requestAuthentication() {
    const { protocol, href } = window.location
    const url = `${protocol}//${this.host}${this.loginPath}?redirect=${href}`
    window.location.replace(url)
  }

  fetch(input, init = {}) {
    return fetch(input, init).then(response => {
      if (response.status === 401) {
        this.requestAuthentication()
      }
      return response
    })
  }
}

class AuthenticationProvider extends Component {
  constructor(props) {
    super(props)
    this.authenticator = new Authenticator(
      this.props.host,
      this.props.loginPath,
      this.props.whoamiPath
    )
  }

  render() {
    return (
      <AuthenticationContext.Provider value={this.authenticator}>
        {this.props.children}
      </AuthenticationContext.Provider>
    )
  }
}

AuthenticationProvider.propTypes = {
  host: PropTypes.string.isRequired,
  loginPath: PropTypes.string.isRequired,
  whoamiPath: PropTypes.string.isRequired
}

export default AuthenticationProvider
