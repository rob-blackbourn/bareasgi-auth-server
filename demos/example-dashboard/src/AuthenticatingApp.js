import React from 'react'
import PropTypes from 'prop-types'

import config from './config'
import AuthenticatedApp from './AuthenticatedApp'
class AuthenticatingApp extends React.Component {
  render() {
    return <AuthenticatedApp authFetch={this.props.authFetch} />
  }
}

AuthenticatingApp.propTypes = {
  authenticator: PropTypes.object.isRequired
}

export default AuthenticatingApp
