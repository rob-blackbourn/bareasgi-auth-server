import React, { Component } from 'react'
import PropTypes from 'prop-types'
import CssBaseline from '@mui/material/CssBaseline'
import Typography from '@mui/material/Typography'
import config from './config'

class Site extends Component {
  componentDidMount() {
    const { authFetch } = this.props

    if (!authFetch) {
      console.log('Invalid authenticator')
    }

    authFetch(`${window.location.origin}${config.whoamiPath}`)
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

    authFetch(`${window.location.origin}/example/api/hello`)
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

Site.propTypes = {
  authFetch: PropTypes.func.isRequired,
  authCredentials: PropTypes.any.isRequired,
  authRedirect: PropTypes.func.isRequired
}

export default Site
