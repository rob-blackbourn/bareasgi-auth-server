import React, { Component } from 'react'
import PropTypes from 'prop-types'

import Box from '@mui/material/Box'
import CssBaseline from '@mui/material/CssBaseline'
import Typography from '@mui/material/Typography'

class Site extends Component {
  state = {
    isLoaded: false,
    isError: false,
    text: ''
  }

  componentDidMount() {
    this.props
      .authFetch(`${window.location.origin}/example/api/hello`)
      .then(response => {
        switch (response.status) {
          case 200:
            return response.text()
          default:
            throw Error('request failed')
        }
      })
      .then(text => {
        this.setState({ text, isLoaded: true, isError: false })
        console.log(text)
      })
      .catch(error => {
        this.setState({ text: error + '', isLoaded: true, isError: true })
      })
  }

  render() {
    const { isLoaded, isError, text } = this.state

    return (
      <Box sx={{ m: 2 }}>
        <CssBaseline />
        <Typography variant="h1">Authenticated Site</Typography>
        <Typography variant="body1">
          This page loads a resource from an authenticated API server.
        </Typography>
        <Typography variant="h4">isLoaded</Typography>
        <Typography variant="body1">{isLoaded ? 'yes' : 'no'}</Typography>
        <Typography variant="h4">isError</Typography>
        <Typography variant="body1">{isError ? 'yes' : 'no'}</Typography>
        <Typography variant="h4">text</Typography>
        <Typography variant="body1">{text}</Typography>
      </Box>
    )
  }
}

Site.propTypes = {
  authFetch: PropTypes.func.isRequired,
  authCredentials: PropTypes.any.isRequired,
  authRedirect: PropTypes.func.isRequired
}

export default Site
