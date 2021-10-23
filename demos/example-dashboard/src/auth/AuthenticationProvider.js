import React, { Component } from 'react'
import PropTypes from 'prop-types'

import AuthenticationContext from './AuthenticationContext'

class AuthenticationProvider extends Component {
  state = {
    authCredentials: {}
  }

  requestAuthentication() {
    const { host, loginPath } = this.props
    const { protocol, href } = window.location
    const url = `${protocol}//${host}${loginPath}?redirect=${href}`
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

  componentDidMount() {
    this.fetch(`${window.location.origin}${this.props.whoamiPath}`)
      .then(response => {
        switch (response.status) {
          case 200:
            return response.json()
          default:
            throw Error('request failed')
        }
      })
      .then(authCredentials => {
        this.setState({ authCredentials })
        console.log(authCredentials)
      })
      .catch(error => {
        console.log(error)
      })
  }

  render() {
    return (
      <AuthenticationContext.Provider value={this.fetch}>
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
