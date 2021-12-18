import * as React from 'react'
import PropTypes from 'prop-types'
import Avatar from '@mui/material/Avatar'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import CssBaseline from '@mui/material/CssBaseline'
import TextField from '@mui/material/TextField'
import Box from '@mui/material/Box'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import Typography from '@mui/material/Typography'
import Container from '@mui/material/Container'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import { createTheme, ThemeProvider } from '@mui/material/styles'

const theme = createTheme()

export default class SignIn extends React.Component {
  state = {
    isChecked: false,
    showDialog: false,
    dialogTitle: '',
    dialogMessage: ''
  }
  redirect = new URLSearchParams(window.location.search).get('redirect')

  handleAccountDisabled = () => {
    this.setState({
      showDialog: true,
      dialogTitle: 'Error',
      dialogMessage: 'This account is disabled'
    })
  }

  handleCommunicationFailure = () => {
    this.setState({
      showDialog: true,
      dialogTitle: 'Error',
      dialogMessage: 'Failed to reach the authentication server'
    })
  }

  handleRedirectFailure = url => {
    this.setState({
      showDialog: true,
      dialogTitle: 'Redirect failed',
      dialogMessage: `Unable to redirect to ${url}`
    })
  }

  handleAuthenticationFailure = status => {
    if (status === 401) {
      this.setState({
        showDialog: true,
        dialogTitle: 'Login failed',
        dialogMessage: 'Invalid credentials, please retry'
      })
    } else if (status === 403) {
      this.setState({
        showDialog: true,
        dialogTitle: 'Login failed',
        dialogMessage: 'Account disabled, contact the administrator'
      })
    } else if (status !== 401) {
      this.handleCommunicationFailure()
    }
  }

  handleCheckAuthentication = response => {
    if (response.ok) {
      this.handleRedirect(true, this.redirect)
    } else {
      this.setState({ isChecked: true }, () => {
        if (response.status === 403) {
          this.handleAccountDisabled()
        } else if (response.status >= 500) {
          this.handleCommunicationFailure()
        }
      })
    }
  }

  checkAuthentication = () => {
    console.log('checkAuthentication')
    const { protocol, host } = window.location
    const url = `${protocol}//${host}${this.props.whoamiPath}`
    console.log('checkAuthentication', url)
    fetch(url)
      .then(response => {
        this.handleCheckAuthentication(response)
      })
      .catch(error => {
        this.handleCommunicationFailure()
      })
  }

  handleRedirect = (ok, url) => {
    if (ok) {
      window.location.href = url
    } else {
      this.handleCommunicationFailure()
    }
  }

  authenticate = (username, password) => {
    const { protocol, host } = window.location
    const url = new URL(this.props.loginPath, `${protocol}//${host}`)
    url.searchParams.append("redirect", this.redirect)
    fetch(url, {
      method: 'POST',
      headers: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        username,
        password
      }),
      redirect: 'follow'
    })
      .then(response => {
        console.log(response)
        if (response.redirected) {
          this.handleRedirect(response.ok, response.url)
        } else {
          this.handleAuthenticationFailure(response.status)
        }
      })
      .catch(error => {
        console.log(error)
        this.handleCommunicationFailure()
      })
  }

  handleSubmit = event => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    this.authenticate(data.get('email'), data.get('password'))
  }

  componentDidMount() {
    debugger
    this.checkAuthentication()
  }

  render() {
    const { isChecked, showDialog, dialogTitle, dialogMessage } = this.state

    if (!isChecked) {
      return (
        <div
          sx={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%'
          }}
        >
          <div>
            <CircularProgress />
          </div>
          <div sx={{ m: 1 }}>
            <Typography variant="h4">Checking authentication</Typography>
          </div>
        </div>
      )
    }

    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />

        <Container component="main" maxWidth="xs">
          <Dialog open={showDialog}>
            <DialogTitle>{dialogTitle}</DialogTitle>
            <DialogContent>
              <Typography variant="body2">{dialogMessage}</Typography>
            </DialogContent>
            <DialogActions>
              <Button
                color="primary"
                onClick={() => this.setState({ showDialog: false })}
              >
                Cancel
              </Button>
            </DialogActions>
          </Dialog>

          <Box
            sx={{
              marginTop: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <Avatar sx={{ m: 1, bgcolor: 'primary.light' }}>
              <LockOutlinedIcon />
            </Avatar>
            <Typography component="h1" variant="h5">
              Sign in
            </Typography>
            <Box
              component="form"
              onSubmit={this.handleSubmit}
              noValidate
              sx={{ mt: 1 }}
            >
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
              >
                Sign In
              </Button>
            </Box>
          </Box>
        </Container>
      </ThemeProvider>
    )
  }
}

SignIn.propTypes = {
  whoamiPath: PropTypes.string.isRequired,
  loginPath: PropTypes.string.isRequired
}
