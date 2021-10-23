import React, { Component } from 'react'
import PropTypes from 'prop-types'
import CssBaseline from '@mui/material/CssBaseline'
import Typography from '@mui/material/Typography'
import config from './config'

class AuthenticatedApp extends Component {
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
    return (
      <>
        <CssBaseline />
        <div>
          <Typography variant="h4">This is not a test</Typography>
        </div>
      </>
    )
  }
}

AuthenticatedApp.propTypes = {
  authenticator: PropTypes.object.isRequired
}

export default AuthenticatedApp
