import React from 'react'
import PropTypes from 'prop-types'

import config from './config'
import AuthenticatedApp from './AuthenticatedApp'
class AuthenticatingApp extends React.Component {
  componentDidMount() {
    const { authenticator } = this.props

    if (!authenticator) {
      console.log('Invalid authenticator')
    }

    authenticator
      .fetch(`${window.location.origin}${config.whoamiPath}`)
      .then(response => {
        switch (response.status) {
          case 200:
            return response.json()
          default:
            throw Error('request failed')
        }
      })
      .then(data => {
        console.log(data)
      })
      .catch(error => {
        console.log(error)
      })

  }

  render() {
    return <AuthenticatedApp authenticator={this.props.authenticator} />
  }
}

AuthenticatingApp.propTypes = {
  authenticator: PropTypes.object.isRequired
}

export default AuthenticatingApp
