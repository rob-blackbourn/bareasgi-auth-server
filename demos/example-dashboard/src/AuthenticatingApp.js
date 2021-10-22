import React from 'react'
import PropTypes from 'prop-types'
import config from './config'

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

    authenticator
      .fetch(`${window.location.origin}/example/api/hello`)
      .then(response => {
        switch (response.status) {
          case 200:
            return response.text()
          default:
            throw Error('request failed')
        }
      })
      .then(text => {
        console.log(text)
      })
      .catch(error => {
        console.log(error)
      })
  }

  render() {
    return this.props.component
  }
}

AuthenticatingApp.propTypes = {
  authenticator: PropTypes.object.isRequired,
  component: PropTypes.node.isRequired
}

export default AuthenticatingApp
