import React, { Component } from 'react'
import PropTypes from 'prop-types'

import AuthenticationContext from './AuthenticationContext'

class Authenticator {
  constructor(host, path) {
    this.host = host
    this.path = path
  }

  requestAuthentication() {
    const { protocol, href } = window.location
    const url = `${protocol}//${this.host}${this.path}?redirect=${href}`
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
    this.authenticator = new Authenticator(this.props.host, this.props.path)
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
  path: PropTypes.string.isRequired
}

export default AuthenticationProvider
