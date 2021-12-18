import React from 'react'

import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'

export default class Page1 extends React.Component {
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
      <Box>
        <Typography variant="h1">Page 1</Typography>
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
